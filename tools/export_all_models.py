# Batch model exporter: runs every experiment script version through
# tools/export_model_json.py in background Blender and writes
# viewer/models/<experiment>/<agent>_<vXX>.json plus viewer/models/index.json.
#
# Usage:
#   python tools/export_all_models.py [--blender PATH] [--only GLOB] [--dry-run]
#   python tools/export_all_models.py --index-only   # no Blender: just index.json
#
# Every subfolder of experiments/<exp>/ except input/ and references/ is a run
# folder, named after the model that ran it ("ChatGPT 5.1", "Fable",
# "Opus 5.1"); its file slug is the lower-case letters and digits of that name
# ("chatgpt51", "fable", "opus51"). A run that ships a design rationale
# (<Agent>/experiment_NN_<slug>_design_rationale.md) gets it copied next to the
# models as viewer/models/<exp>/<slug>_rationale.md and linked from index.json;
# likewise experiment_NN_<slug>_callouts.json -> <slug>_callouts.json (see
# tools/callouts.py).
#
# Blender path resolution: --blender arg > CRAFTBOT_BLENDER env > known installs.

import argparse
import fnmatch
import glob
import os
import re
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import model_export_core as core

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(REPO_ROOT, "viewer", "models")
EXPORTER = os.path.join(REPO_ROOT, "tools", "export_model_json.py")
RESERVED_DIRS = {"input", "references"}   # every other subfolder of an experiment is a run folder
KNOWN_BLENDERS = [
    r"C:\Program Files\Blender Foundation\Blender 4.3\blender.exe",
    r"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe",
]


def find_blender(cli_path):
    for candidate in [cli_path, os.environ.get("CRAFTBOT_BLENDER")] + KNOWN_BLENDERS:
        if candidate and os.path.isfile(candidate):
            return candidate
    sys.exit("No Blender executable found: pass --blender or set CRAFTBOT_BLENDER")


def agent_slug(agent):
    """Run folder name -> file slug, lower-case letters and digits only
    ("ChatGPT 5.1" -> "chatgpt51", "Opus 5.1" -> "opus51", "Fable" -> "fable")."""
    return re.sub(r"[^a-z0-9]", "", agent.lower())


def run_folders(exp_dir):
    """Run folder names of one experiment, sorted: every subfolder except
    input/, references/ and hidden or private ones."""
    return sorted(name for name in os.listdir(exp_dir)
                  if os.path.isdir(os.path.join(exp_dir, name))
                  and name not in RESERVED_DIRS and not name.startswith((".", "_")))


def resolve_run_folder(exp_dir, agent=None):
    """Path of one run folder of exp_dir: the one named by agent, else the
    only one there is. Exits when the choice is ambiguous."""
    runs = run_folders(exp_dir)
    if agent:
        if agent not in runs:
            sys.exit(f"no run folder {agent!r} in {exp_dir}; found {runs}")
        return os.path.join(exp_dir, agent)
    if len(runs) == 1:
        return os.path.join(exp_dir, runs[0])
    sys.exit(f"{len(runs)} run folders in {exp_dir} {runs}; pass --agent NAME")


def find_scripts():
    """Yield (experiment_id, agent, version, script_path, lib_dir) in order."""
    jobs = []
    for exp_dir in sorted(glob.glob(os.path.join(REPO_ROOT, "experiments", "*"))):
        if not os.path.isdir(exp_dir):
            continue
        exp_id = os.path.basename(exp_dir)
        lib_dir = os.path.join(exp_dir, "input")   # old runs keep craftbot_lib V1.1 here;
        if not os.path.isdir(lib_dir):              # newer runs import tools/ instead
            lib_dir = exp_dir
        for agent in run_folders(exp_dir):
            agent_dir = os.path.join(exp_dir, agent)
            for script in sorted(glob.glob(os.path.join(agent_dir, "experiment_*.py"))):
                m = core.VERSION_RE.search(os.path.basename(script))
                if not m:
                    continue  # render_*.py and other helpers
                jobs.append((exp_id, agent, f"v{m.group(1)}", script, lib_dir))
    return jobs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--blender", default=None)
    ap.add_argument("--only", default=None,
                    help="glob matched against the script path (e.g. *fable_v06*)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--index-only", action="store_true",
                    help="rebuild index.json (and copy rationale docs) without Blender")
    args = ap.parse_args()

    if args.index_only:
        print(f"indexed {rebuild_index()} models")
        return

    jobs = find_scripts()
    if args.only:
        jobs = [j for j in jobs if fnmatch.fnmatch(j[3].replace("\\", "/"),
                                                   f"*{args.only}*")]
    if args.dry_run:
        for exp_id, agent, v, script, _ in jobs:
            print(f"{exp_id}  {agent}  {v}  {os.path.relpath(script, REPO_ROOT)}")
        print(f"{len(jobs)} scripts")
        return

    blender = find_blender(args.blender)
    failures = []
    for i, (exp_id, agent, v, script, lib_dir) in enumerate(jobs, 1):
        out_rel = f"{exp_id}/{agent_slug(agent)}_{v}.json"
        out_path = os.path.join(MODELS_DIR, out_rel.replace("/", os.sep))
        print(f"[{i}/{len(jobs)}] {out_rel} ... ", end="", flush=True)
        try:
            proc = subprocess.run(
                [blender, "--background", "--python", EXPORTER, "--",
                 script, lib_dir, out_path],
                capture_output=True, text=True, encoding="utf-8",
                errors="replace", timeout=120, cwd=REPO_ROOT)
            ok_line = next((ln for ln in proc.stdout.splitlines()
                            if ln.startswith("EXPORT OK")), None)
        except subprocess.TimeoutExpired:
            proc, ok_line = None, None
        if ok_line:
            _, _, n_boxes, n_meshes, n_bytes = ok_line.split()
            print(f"OK {int(n_boxes) + int(n_meshes)} elements, {n_bytes} bytes")
        else:
            tail = "TIMEOUT" if proc is None else \
                "\n".join((proc.stdout + proc.stderr).splitlines()[-6:])
            failures.append((out_rel, tail))
            print("FAILED")

    n_indexed = rebuild_index()
    print(f"\nindexed {n_indexed} models / failed this run: {len(failures)}")
    for rel, tail in failures:
        safe = tail.encode("ascii", "replace").decode("ascii")
        print(f"\n--- FAILED {rel}\n{safe}")


def sync_run_doc(exp_id, agent, pattern, dst_name):
    """Copy a run document (rationale md, callouts json) from the run folder
    next to the experiment's models; returns the index-relative path, or None."""
    found = glob.glob(os.path.join(REPO_ROOT, "experiments", exp_id, agent, pattern))
    if not found:
        return None
    dst = os.path.join(MODELS_DIR, exp_id, dst_name)
    src = sorted(found)[0]
    if not os.path.isfile(dst) or open(src, "rb").read() != open(dst, "rb").read():
        shutil.copyfile(src, dst)
    return f"{exp_id}/{dst_name}"


def sync_rationale(exp_id, agent):
    return sync_run_doc(exp_id, agent, "experiment_*_design_rationale.md",
                        f"{agent_slug(agent)}_rationale.md")


def sync_callouts(exp_id, agent):
    return sync_run_doc(exp_id, agent, "experiment_*_callouts.json",
                        f"{agent_slug(agent)}_callouts.json")


def agents_by_slug():
    """{slug: run folder name} over every experiment on disk."""
    names = {}
    for exp_dir in glob.glob(os.path.join(REPO_ROOT, "experiments", "*")):
        if os.path.isdir(exp_dir):
            for agent in run_folders(exp_dir):
                names[agent_slug(agent)] = agent
    return names


def rebuild_index():
    """Regenerate index.json from every model JSON currently on disk, so
    partial runs (--only) never shrink the index."""
    import json
    names = agents_by_slug()
    docs = {}   # (exp_id, agent) -> (rationale path, callouts path)
    entries = []
    for path in glob.glob(os.path.join(MODELS_DIR, "*", "*.json")):
        rel = os.path.relpath(path, MODELS_DIR).replace(os.sep, "/")
        m = re.match(r"(.+)/([a-z0-9]+)_(v\d+)\.json$", rel)
        if not m:
            continue
        exp_id, slug, v = m.groups()
        with open(path, encoding="utf-8") as f:
            model = json.load(f)
        agent = names.get(slug, slug)
        if (exp_id, agent) not in docs:
            docs[(exp_id, agent)] = (sync_rationale(exp_id, agent), sync_callouts(exp_id, agent))
        rationale, callouts = docs[(exp_id, agent)]
        entries.append({
            "experiment": exp_id,
            "agent": agent,
            "v": v,
            "file": rel,
            "elements": len(model["boxes"]) + len(model["meshes"]),
            "bytes": os.path.getsize(path),
            "rationale": rationale,
            "callouts": callouts,
        })
    os.makedirs(MODELS_DIR, exist_ok=True)
    core.dump_compact(core.build_index(entries),
                      os.path.join(MODELS_DIR, "index.json"))
    return len(entries)


if __name__ == "__main__":
    main()
