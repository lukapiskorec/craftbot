"""Close-out of an experiment version or run, with validated Claude/Codex transcript archival after all required checks pass; run accepts --transcript-source with --session-id, or --no-archive for preflight.

The Runner agent calls this instead of the six-step sequence by hand and
reads the markdown it writes. Every step reports pass or fail; the script
never stops at the first failure, so one report shows everything.

    python tools/closeout.py version 14 v09 [--agent NAME] [--blender PATH] [--no-screenshot]
        export the version to the viewer, bake and audit layers, rebuild
        index.json, check the view set, screenshot the viewer
        -> experiments/<exp>/<Agent>/closeout_v09.md

    python tools/closeout.py run 14 [--agent NAME] --session-id ID [--transcript-source PATH]
        rationale sections present, hand-off files, callouts check, prompt
        file present, API card current, index rebuilt, then (last) the
        transcript copy
        -> experiments/<exp>/<Agent>/closeout_run.md

    python tools/closeout.py run 14 [--agent NAME] --no-archive
        run checks and rebuild the index, without reading/copying a transcript
        -> experiments/<exp>/<Agent>/closeout_preflight.md

An explicit transcript source can be a Codex rollout or Claude JSONL. Its root
session identity must match --session-id. Without a source, the legacy Claude
lookup is retained but must resolve uniquely. A validated temporary snapshot
replaces the archive atomically, only after every required check passes. Child
sessions and malformed or unidentified transcripts are rejected. Only the chosen
root transcript is copied; subagent logs are not collected. The report is written
after the archive operation. No host-specific runtime launcher is required:
use any working Python, including Blender's bundled interpreter.

The experiment id is the two-digit prefix or the folder name under
experiments/. <Agent> is the run folder, named after the model that ran
the experiment ("Fable", "Opus 5.1", "ChatGPT 5.1"); --agent names it and
is needed only when the experiment has more than one run folder. File
names inside it use the slug (lower-case letters and digits: fable,
opus51). In a multi-variation run the versions live in variation folders
("Fable A", "Fable B": `version 15 v03 --agent "Fable A"`) and the run
close-out runs on the orchestrator folder (`run 15 --agent "Fable"`), which
checks the shared files there and the team files in every variation
folder. Blender resolves like the exporter (--blender, then
CRAFTBOT_BLENDER, then the known installs); Chrome from CRAFTBOT_CHROME or
the default install path.

Provenance: the close-out steps of the running-craftbot-experiment skill
(experiments 01-14), scripted after the experiment 14 context audit.
"""
import argparse
import glob
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(REPO, "tools")
sys.path.insert(0, TOOLS)
from export_all_models import find_blender, agent_slug, resolve_run_folder, run_folders  # noqa: E402

CHROME_DEFAULT = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
SESSIONS_DIR = os.path.join(os.path.expanduser("~"), ".claude", "projects")
RATIONALE_SECTIONS = ["0", "1", "2", "3", "3b", "4", "5", "6", "6b", "7", "8", "9", "10"]


def experiment_dir(exp):
    if os.path.isdir(os.path.join(REPO, "experiments", exp)):
        return os.path.join(REPO, "experiments", exp)
    hits = sorted(glob.glob(os.path.join(REPO, "experiments", f"{exp}_*")))
    if not hits:
        sys.exit(f"no experiment folder for {exp}")
    return hits[0]


def variation_folders(exp_dir, agent):
    """Variation folders of a multi-variation run: the run folders named
    "<agent> <V>" beside the orchestrator folder <agent> ("Fable A", "Fable B"
    for "Fable"); empty for a plain single-variation run."""
    return [name for name in run_folders(exp_dir) if name.startswith(agent + " ")]


def run(cmd, timeout=1200):
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                          timeout=timeout, cwd=REPO)
    return proc.returncode, (proc.stdout + proc.stderr)


def _validate_transcript(path, session_id):
    identified = False
    with open(path, encoding="utf-8-sig") as handle:
        for number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except ValueError as exc:
                raise ValueError(f"invalid transcript JSON at line {number}") from exc
            if not isinstance(record, dict):
                raise ValueError(f"transcript line {number} is not an object")
            if record.get("type") == "session_meta":
                meta = record.get("payload")
                if not isinstance(meta, dict) or meta.get("id") != session_id:
                    raise ValueError("Codex transcript session ID does not match --session-id")
                source = meta.get("source")
                if isinstance(source, dict) and "subagent" in source:
                    raise ValueError("a Codex child session cannot be archived as the root")
                identified = True
            if "sessionId" in record:
                if record["sessionId"] != session_id:
                    raise ValueError("Claude transcript session ID does not match --session-id")
                if record.get("isSidechain"):
                    raise ValueError("a Claude sidechain cannot be archived as the root")
                identified = True
    if not identified:
        raise ValueError("transcript has no recognized root session identity")


def archive_transcript(session_id, destination, source=None):
    """Atomically archive a validated snapshot of one root Claude/Codex JSONL session; an omitted source uses unique legacy Claude lookup.

    Existing archives remain unchanged on lookup, copy or validation failures.
    The caller must complete all required run checks before calling this.
    """
    if not session_id or not re.fullmatch(r"[A-Za-z0-9_-]+", session_id):
        raise ValueError("a valid --session-id is required to archive a transcript")
    if source is None:
        hits = glob.glob(os.path.join(SESSIONS_DIR, "*", session_id + ".jsonl"))
        if len(hits) != 1:
            raise ValueError(f"expected one transcript for {session_id}; found {len(hits)} under {SESSIONS_DIR}")
        source = hits[0]
    source = os.path.abspath(source)
    destination = os.path.abspath(destination)
    if os.path.normcase(os.path.realpath(source)) == os.path.normcase(os.path.realpath(destination)):
        raise ValueError("transcript source and archive destination must differ")
    with tempfile.NamedTemporaryFile(prefix=".transcript-", suffix=".jsonl",
                                     dir=os.path.dirname(destination), delete=False) as handle:
        snapshot = handle.name
    try:
        shutil.copyfile(source, snapshot)
        _validate_transcript(snapshot, session_id)
        size = os.path.getsize(snapshot)
        os.replace(snapshot, destination)
    finally:
        if os.path.exists(snapshot):
            os.unlink(snapshot)
    return f"{size // 1024} KB from {source} (root session {session_id})"


class Report:
    def __init__(self, title):
        self.title, self.rows = title, []

    def add(self, name, ok, detail=""):
        self.rows.append((name, ok, detail.strip()))
        print(f"[{'pass' if ok else 'FAIL'}] {name}" + (f": {detail.strip().splitlines()[-1]}" if detail.strip() else ""))

    def write(self, path):
        lines = [f"# {self.title}", "", f"Written by `tools/closeout.py` on {time.strftime('%Y-%m-%d %H:%M')}.", "",
                 "| step | result | detail |", "|---|---|---|"]
        for name, ok, detail in self.rows:
            d = detail.replace("|", "/").replace("\n", " ")
            lines.append(f"| {name} | {'pass' if ok else 'FAIL'} | {d[:300]} |")
        n_fail = sum(1 for _, ok, _ in self.rows if not ok)
        lines += ["", f"{len(self.rows) - n_fail} passed, {n_fail} failed."]
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(lines) + "\n")
        print(f"wrote {os.path.relpath(path, REPO)}: {len(self.rows) - n_fail} passed, {n_fail} failed")
        return n_fail == 0


def views_ok(views_path):
    """The view set needs a frame-only view, a from-below view and an interior
    view (a section cut or a view that hides the envelope)."""
    if not os.path.isfile(views_path):
        return False, os.path.basename(views_path) + " missing"
    t = open(views_path, encoding="utf-8").read()
    problems = []
    if not re.search(r"elev\s*=\s*-\d", t):
        problems.append("no from-below view (elev < 0)")
    if not re.search(r"hide\s*=\s*\[\s*\"", t) and not re.search(r"hide\s*=\s*COVER", t):
        problems.append("no frame-only view (non-empty hide list)")
    if "cut=(" not in t:
        problems.append("no section / interior view (cut=...)")
    return not problems, "; ".join(problems) or "frame-only, from-below and section views present"


def screenshot(model_rel, out_png):
    chrome = os.environ.get("CRAFTBOT_CHROME", CHROME_DEFAULT)
    if not os.path.isfile(chrome):
        return False, f"Chrome not found at {chrome}"
    port = 8123
    with socket.socket() as s:
        s.settimeout(0.2)
        if s.connect_ex(("127.0.0.1", port)) == 0:
            port = 8124
    server = subprocess.Popen([sys.executable, "-m", "http.server", "-d", os.path.join(REPO, "viewer"), str(port)],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        time.sleep(1.0)
        url = f"http://127.0.0.1:{port}/?model={model_rel}&anim=none"
        code, out = run([chrome, "--headless=new", "--hide-scrollbars", "--window-size=1600,1000",
                         f"--screenshot={out_png}", "--virtual-time-budget=8000", url], timeout=120)
    finally:
        server.terminate()
    ok = os.path.isfile(out_png) and os.path.getsize(out_png) > 20000
    return ok, ("screenshot written to " + out_png) if ok else ("no screenshot: " + out[-300:])


def closeout_version(args):
    exp_dir = experiment_dir(args.exp)
    exp_id = os.path.basename(exp_dir)
    nn = exp_id[:2]
    run_dir = resolve_run_folder(exp_dir, args.agent)
    agent = os.path.basename(run_dir)
    slug = agent_slug(agent)
    rep = Report(f"Close-out of {exp_id} {agent} {args.version}")
    script = os.path.join(run_dir, f"experiment_{nn}_{slug}_{args.version}.py")
    rep.add("script exists", os.path.isfile(script), os.path.relpath(script, REPO))
    blender = find_blender(args.blender)
    only = f"{exp_id}/{agent}/experiment_{nn}_{slug}_{args.version}"
    code, out = run([sys.executable, os.path.join(TOOLS, "export_all_models.py"), "--blender", blender, "--only", only])
    rep.add("export to viewer", code == 0 and "failed this run: 0" in out, out)
    code, out = run([sys.executable, os.path.join(TOOLS, "layers.py"), "--bake", "--only", exp_id])
    rep.add("layers baked", code == 0, out)
    code, out = run([sys.executable, os.path.join(TOOLS, "layers.py"), "--audit", "--only", exp_id])
    m = re.search(r"(\d+) elements in 'other'", out)
    n_other = int(m.group(1)) if m else -1
    rep.add("layers audit: nothing in 'other'", n_other == 0,
            f"{n_other} elements in 'other'" + ("; add an OVERRIDES entry in tools/layers.py" if n_other else ""))
    code, out = run([sys.executable, os.path.join(TOOLS, "export_all_models.py"), "--index-only"])
    rep.add("index.json rebuilt", code == 0, out)
    ok, detail = views_ok(os.path.join(run_dir, f"views_{slug}.py"))
    rep.add("view set complete", ok, detail)
    renders = glob.glob(os.path.join(run_dir, f"experiment_{nn}_{slug}_{args.version}_blender_view_*.png"))
    rep.add("renders present", len(renders) > 0, f"{len(renders)} view PNGs")
    if not args.no_screenshot:
        png = os.path.join(run_dir, f"closeout_{args.version}_viewer.png")
        ok, detail = screenshot(f"models/{exp_id}/{slug}_{args.version}.json", png)
        rep.add("viewer loads the model", ok, detail)
    return rep.write(os.path.join(run_dir, f"closeout_{args.version}.md"))


def closeout_run(args):
    exp_dir = experiment_dir(args.exp)
    exp_id = os.path.basename(exp_dir)
    nn = exp_id[:2]
    run_dir = resolve_run_folder(exp_dir, args.agent)
    agent = os.path.basename(run_dir)
    slug = agent_slug(agent)
    rep = Report(f"Close-out of the {exp_id} {agent} run")
    rationale = os.path.join(run_dir, f"experiment_{nn}_{slug}_design_rationale.md")
    if os.path.isfile(rationale):
        with open(rationale, encoding="utf-8") as handle:
            text = handle.read()
        heads = re.findall(r"^##\s+(\d+[a-z]?)\.", text, re.M)
        missing = [s for s in RATIONALE_SECTIONS if s not in heads]
        rep.add("rationale sections", not missing, "missing: " + ", ".join(missing) if missing else "sections 0-10 present")
    else:
        rep.add("rationale sections", False, "rationale missing")
    variations = variation_folders(exp_dir, agent)
    if variations:
        shared = ("agent.md", "brief.md", "concept_shared.md", "sources.md")
        team = ("agent.md", "concept.md", "requirements.md", "design_notes.md", "version_notes.md")
        rep.add("multi-variation run", True, "variation folders: " + ", ".join(variations))
    else:
        shared = ("agent.md", "brief.md", "concept.md", "requirements.md", "sources.md", "design_notes.md", "version_notes.md")
        team = ()
    for name in shared:
        p = os.path.join(run_dir, name)
        rep.add(f"hand-off file {name}", os.path.isfile(p), "present" if os.path.isfile(p) else "missing (single-agent runs before experiment 15 have none)")
    for var in variations:
        for name in team:
            p = os.path.join(exp_dir, var, name)
            rep.add(f"hand-off file {var}/{name}", os.path.isfile(p), "present" if os.path.isfile(p) else "missing")
        callouts = glob.glob(os.path.join(exp_dir, var, "experiment_*_callouts.json"))
        rep.add(f"callouts file {var}", bool(callouts), os.path.relpath(callouts[0], REPO) if callouts else "missing: one callouts file per variation folder")
    prompt = os.path.join(exp_dir, "input", f"experiment_{nn}_prompts_{slug}.txt")
    rep.add("prompt file", os.path.isfile(prompt), os.path.relpath(prompt, REPO))
    code, out = run([sys.executable, os.path.join(TOOLS, "callouts.py"), "--check", "--only", exp_id])
    rep.add("callouts check", code == 0, out)
    code, out = run([sys.executable, os.path.join(TOOLS, "api_card.py"), "--check"])
    rep.add("API card current", code == 0, out)
    code, out = run([sys.executable, os.path.join(TOOLS, "export_all_models.py"), "--index-only"])
    rep.add("index.json rebuilt", code == 0, out)
    no_archive = getattr(args, "no_archive", False)
    if no_archive:
        rep.add("transcript archive deferred", True, "preflight only; existing archive and final report unchanged")
    elif not all(ok for _, ok, _ in rep.rows):
        rep.add("transcript archived (last step)", False, "blocked by failed run checks; existing archive unchanged")
    else:
        dst = os.path.join(run_dir, f"experiment_{nn}_{slug}_conversation.jsonl")
        try:
            detail = archive_transcript(args.session_id, dst, getattr(args, "transcript_source", None))
            rep.add("transcript archived (last step)", True, detail)
        except (OSError, ValueError) as exc:
            rep.add("transcript archived (last step)", False, str(exc))
    report_name = "closeout_preflight.md" if no_archive else "closeout_run.md"
    return rep.write(os.path.join(run_dir, report_name))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("version")
    v.add_argument("exp")
    v.add_argument("version")
    v.add_argument("--agent", default=None, help="run folder name, e.g. \"Opus 5.1\"; needed when the experiment has several")
    v.add_argument("--blender", default=None)
    v.add_argument("--no-screenshot", action="store_true")
    r = sub.add_parser("run")
    r.add_argument("exp")
    r.add_argument("--agent", default=None, help="run folder name, e.g. \"Opus 5.1\"; needed when the experiment has several")
    r.add_argument("--session-id", default=None)
    r.add_argument("--transcript-source", default=None, help="explicit root Claude/Codex JSONL; requires --session-id")
    r.add_argument("--no-archive", action="store_true", help="run checks/index rebuild only; write closeout_preflight.md")
    args = ap.parse_args()
    if args.cmd == "run":
        if args.transcript_source and not args.session_id:
            ap.error("--transcript-source requires --session-id")
        if args.no_archive and (args.session_id or args.transcript_source):
            ap.error("--no-archive cannot be combined with transcript arguments")
    ok = closeout_version(args) if args.cmd == "version" else closeout_run(args)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
