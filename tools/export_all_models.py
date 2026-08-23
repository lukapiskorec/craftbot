# Batch model exporter: runs every experiment script version through
# tools/export_model_json.py in background Blender and writes
# viewer/models/<experiment>/<agent>_<vXX>.json plus viewer/models/index.json.
#
# Usage:
#   python tools/export_all_models.py [--blender PATH] [--only GLOB] [--dry-run]
#
# Blender path resolution: --blender arg > CRAFTBOT_BLENDER env > known installs.

import argparse
import fnmatch
import glob
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import model_export_core as core

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(REPO_ROOT, "viewer", "models")
EXPORTER = os.path.join(REPO_ROOT, "tools", "export_model_json.py")
AGENT_DIRS = {"ChatGPT 5.1": "chatgpt51", "Fable": "fable"}
KNOWN_BLENDERS = [
    r"C:\Program Files\Blender Foundation\Blender 4.3\blender.exe",
    r"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe",
]


def find_blender(cli_path):
    for candidate in [cli_path, os.environ.get("CRAFTBOT_BLENDER")] + KNOWN_BLENDERS:
        if candidate and os.path.isfile(candidate):
            return candidate
    sys.exit("No Blender executable found: pass --blender or set CRAFTBOT_BLENDER")


def find_scripts():
    """Yield (experiment_id, agent, version, script_path, lib_dir) in order."""
    jobs = []
    for exp_dir in sorted(glob.glob(os.path.join(REPO_ROOT, "experiments", "*"))):
        if not os.path.isdir(exp_dir):
            continue
        exp_id = os.path.basename(exp_dir)
        lib_dir = os.path.join(exp_dir, "input")
        if not os.path.isfile(os.path.join(lib_dir, "craftbot_lib.py")):
            continue
        for agent in AGENT_DIRS:
            agent_dir = os.path.join(exp_dir, agent)
            if not os.path.isdir(agent_dir):
                continue
            for script in sorted(glob.glob(os.path.join(agent_dir, "experiment_*.py"))):
                m = core.VERSION_RE.search(os.path.basename(script))
                if not m:
                    continue  # render_fable.py and other helpers
                jobs.append((exp_id, agent, f"v{m.group(1)}", script, lib_dir))
    return jobs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--blender", default=None)
    ap.add_argument("--only", default=None,
                    help="glob matched against the script path (e.g. *fable_v06*)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

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
        out_rel = f"{exp_id}/{AGENT_DIRS[agent]}_{v}.json"
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


def rebuild_index():
    """Regenerate index.json from every model JSON currently on disk, so
    partial runs (--only) never shrink the index."""
    import json
    agents_by_slug = {slug: agent for agent, slug in AGENT_DIRS.items()}
    entries = []
    for path in glob.glob(os.path.join(MODELS_DIR, "*", "*.json")):
        rel = os.path.relpath(path, MODELS_DIR).replace(os.sep, "/")
        m = re.match(r"(.+)/([a-z0-9]+)_(v\d+)\.json$", rel)
        if not m:
            continue
        exp_id, slug, v = m.groups()
        with open(path, encoding="utf-8") as f:
            model = json.load(f)
        entries.append({
            "experiment": exp_id,
            "agent": agents_by_slug.get(slug, slug),
            "v": v,
            "file": rel,
            "elements": len(model["boxes"]) + len(model["meshes"]),
            "bytes": os.path.getsize(path),
        })
    os.makedirs(MODELS_DIR, exist_ok=True)
    core.dump_compact(core.build_index(entries),
                      os.path.join(MODELS_DIR, "index.json"))
    return len(entries)


if __name__ == "__main__":
    main()
