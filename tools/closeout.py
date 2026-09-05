"""Close-out of an experiment version or run, as one command.

The Runner agent calls this instead of the six-step sequence by hand and
reads the markdown it writes. Every step reports pass or fail; the script
never stops at the first failure, so one report shows everything.

    python tools/closeout.py version 14 v09 [--blender PATH] [--no-screenshot]
        export the version to the viewer, bake and audit layers, rebuild
        index.json, check the view set, screenshot the viewer
        -> experiments/<exp>/Fable/closeout_v09.md

    python tools/closeout.py run 14 [--session-id ID]
        rationale sections present, callouts check, prompt file present,
        API card current, index rebuilt, then (last) the transcript copy
        -> experiments/<exp>/Fable/closeout_run.md

The experiment id is the two-digit prefix or the folder name under
experiments/. Blender resolves like the exporter (--blender, then
CRAFTBOT_BLENDER, then the known installs); Chrome from CRAFTBOT_CHROME or
the default install path.

Provenance: the close-out steps of the running-craftbot-experiment skill
(experiments 01-14), scripted after the experiment 14 context audit.
"""
import argparse
import glob
import os
import re
import shutil
import socket
import subprocess
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(REPO, "tools")
sys.path.insert(0, TOOLS)
from export_all_models import find_blender  # noqa: E402

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


def run(cmd, timeout=1200):
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                          timeout=timeout, cwd=REPO)
    return proc.returncode, (proc.stdout + proc.stderr)


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
        return False, "views_fable.py missing"
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
    fable = os.path.join(exp_dir, "Fable")
    rep = Report(f"Close-out of {exp_id} {args.version}")
    script = os.path.join(fable, f"experiment_{nn}_fable_{args.version}.py")
    rep.add("script exists", os.path.isfile(script), os.path.relpath(script, REPO))
    blender = find_blender(args.blender)
    only = f"{exp_id}/Fable/experiment_{nn}_fable_{args.version}"
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
    ok, detail = views_ok(os.path.join(fable, "views_fable.py"))
    rep.add("view set complete", ok, detail)
    renders = glob.glob(os.path.join(fable, f"experiment_{nn}_fable_{args.version}_blender_view_*.png"))
    rep.add("renders present", len(renders) > 0, f"{len(renders)} view PNGs")
    if not args.no_screenshot:
        png = os.path.join(fable, f"closeout_{args.version}_viewer.png")
        ok, detail = screenshot(f"models/{exp_id}/fable_{args.version}.json", png)
        rep.add("viewer loads the model", ok, detail)
    return rep.write(os.path.join(fable, f"closeout_{args.version}.md"))


def closeout_run(args):
    exp_dir = experiment_dir(args.exp)
    exp_id = os.path.basename(exp_dir)
    nn = exp_id[:2]
    fable = os.path.join(exp_dir, "Fable")
    rep = Report(f"Close-out of the {exp_id} run")
    rationale = os.path.join(fable, f"experiment_{nn}_fable_design_rationale.md")
    if os.path.isfile(rationale):
        text = open(rationale, encoding="utf-8").read()
        heads = re.findall(r"^##\s+(\d+[a-z]?)\.", text, re.M)
        missing = [s for s in RATIONALE_SECTIONS if s not in heads]
        rep.add("rationale sections", not missing, "missing: " + ", ".join(missing) if missing else "sections 0-10 present")
    else:
        rep.add("rationale sections", False, "rationale missing")
    for name in ("brief.md", "concept.md", "requirements.md", "sources.md", "design_notes.md", "version_notes.md"):
        p = os.path.join(fable, name)
        rep.add(f"hand-off file {name}", os.path.isfile(p), "present" if os.path.isfile(p) else "missing (single-agent runs before experiment 15 have none)")
    prompt = os.path.join(exp_dir, "input", f"experiment_{nn}_prompts_fable.txt")
    rep.add("prompt file", os.path.isfile(prompt), os.path.relpath(prompt, REPO))
    code, out = run([sys.executable, os.path.join(TOOLS, "callouts.py"), "--check", "--only", exp_id])
    rep.add("callouts check", code == 0, out)
    code, out = run([sys.executable, os.path.join(TOOLS, "api_card.py"), "--check"])
    rep.add("API card current", code == 0, out)
    code, out = run([sys.executable, os.path.join(TOOLS, "export_all_models.py"), "--index-only"])
    rep.add("index.json rebuilt", code == 0, out)
    if args.session_id:
        hits = glob.glob(os.path.join(SESSIONS_DIR, "*", args.session_id + ".jsonl"))
        if hits:
            dst = os.path.join(fable, f"experiment_{nn}_fable_conversation.jsonl")
            shutil.copy(hits[0], dst)
            rep.add("transcript archived (last step)", True, f"{os.path.getsize(dst) // 1024} KB from {hits[0]}")
        else:
            rep.add("transcript archived (last step)", False, f"no {args.session_id}.jsonl under {SESSIONS_DIR}")
    else:
        rep.add("transcript archived (last step)", False, "no --session-id given; archive by hand as the last action")
    return rep.write(os.path.join(fable, "closeout_run.md"))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("version")
    v.add_argument("exp")
    v.add_argument("version")
    v.add_argument("--blender", default=None)
    v.add_argument("--no-screenshot", action="store_true")
    r = sub.add_parser("run")
    r.add_argument("exp")
    r.add_argument("--session-id", default=None)
    args = ap.parse_args()
    ok = closeout_version(args) if args.cmd == "version" else closeout_run(args)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
