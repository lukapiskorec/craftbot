# Design-rationale callouts: validation of the authored files.
#
# A Fable run may ship experiments/<exp>/Fable/experiment_NN_fable_callouts.json:
#   {"callouts": [{"id": "heel",                 # unique, [a-z0-9-]
#                  "label": "Truss heel over the full 112 binder",
#                  "section": "5.1",             # numbered heading of the rationale
#                  "quote": "the heel is 28 mm outside the wall face",  # optional,
#                                                # verbatim (whitespace-insensitive)
#                                                # text inside that section
#                  "match": {"names": "Truss_*_BottomChord",  # glob: * ? and | alternatives
#                            "collection": "Structure/*"},     # optional glob
#                  "anchor": "nearest"}]}        # or "centroid" (default)
# export_all_models.py --index-only copies it next to the models and the
# viewer (callouts.js) draws each callout as a tag pointing at its elements.
#
# Usage:
#   python tools/callouts.py --check [--only 04]   # exit 1 on any error
#   python tools/callouts.py --names 04            # authoring aid: element name
#                                                  # patterns per collection

import argparse
import collections
import glob
import json
import os
import re
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(REPO_ROOT, "viewer", "models")
MAX_CALLOUTS = 15
MAX_LABEL = 80
ANCHORS = ("centroid", "nearest")
SECTION_RE = re.compile(r"^(\d+[a-z]?(?:\.\d+)*)\.?\s")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$", re.M)


def glob_re(pattern):
    """Same semantics as callout-data.js globToRegExp."""
    alts = []
    for g in str(pattern).split("|"):
        g = g.strip()
        if g:
            alts.append(re.escape(g).replace(r"\*", ".*").replace(r"\?", "."))
    return re.compile("^(?:" + "|".join(alts) + ")$")


def section_of(heading_text):
    m = SECTION_RE.match(heading_text)
    return m.group(1) if m else None


def sections(md):
    """[(section, heading text)] for every numbered heading."""
    out = []
    for m in HEADING_RE.finditer(md):
        s = section_of(m.group(2))
        if s:
            out.append((s, m.group(2)))
    return out


def section_range(md, section):
    """(start, end) of a section body: after its heading up to the next
    heading of the same or a higher level; None if the section is missing."""
    start, level = None, 0
    for m in HEADING_RE.finditer(md):
        if start is None:
            if section_of(m.group(2)) == section:
                start, level = m.end(), len(m.group(1))
        elif len(m.group(1)) <= level:
            return start, m.start()
    return None if start is None else (start, len(md))


def find_quote(md, section, quote):
    """(start, end) of the first whitespace-insensitive occurrence of quote
    inside its section, or None."""
    rng = section_range(md, section)
    if rng is None:
        return None
    pattern = r"\s+".join(re.escape(w) for w in quote.split())
    m = re.compile(pattern).search(md, rng[0], rng[1])
    return (m.start(), m.end()) if m else None


def in_fence(md, pos):
    return md.count("```", 0, pos) % 2 == 1


def resolve(model, match):
    """Element names of a model JSON selected by a match spec."""
    name_re = glob_re(match.get("names", "*"))
    coll_re = glob_re(match["collection"]) if match.get("collection") else None
    colls = model["collections"]
    hits = []
    for row in model["boxes"]:
        if name_re.match(row[0]) and (not coll_re or coll_re.match(colls[row[1]])):
            hits.append(row[0])
    for mesh in model["meshes"]:
        if name_re.match(mesh["name"]) and (not coll_re or coll_re.match(colls[mesh["collection"]])):
            hits.append(mesh["name"])
    return hits


def check(data, md, models):
    """Validate a callouts dict against the rationale markdown and
    {version: model dict}. Returns (errors, report lines)."""
    errors, report = [], []
    callouts = data.get("callouts")
    if not isinstance(callouts, list):
        return ['top-level "callouts" list missing'], report
    if len(callouts) > MAX_CALLOUTS:
        errors.append(f"{len(callouts)} callouts, max {MAX_CALLOUTS}")
    known = {s for s, _ in sections(md)}
    seen = set()
    latest = max(models) if models else None
    for c in callouts:
        cid = c.get("id", "?")
        tag = f"[{cid}]"
        if not re.fullmatch(r"[a-z0-9-]+", str(cid)):
            errors.append(f"{tag} id must be [a-z0-9-]")
        if cid in seen:
            errors.append(f"{tag} duplicate id")
        seen.add(cid)
        label = c.get("label", "")
        if not label or len(label) > MAX_LABEL:
            errors.append(f"{tag} label missing or longer than {MAX_LABEL} chars")
        section = str(c.get("section", ""))
        if section not in known:
            errors.append(f"{tag} section {section!r} not a heading of the rationale")
        quote = c.get("quote")
        if quote:
            hit = find_quote(md, section, quote) if section in known else None
            if not hit:
                errors.append(f"{tag} quote not found in section {section}: {quote!r}")
            elif in_fence(md, hit[0]):
                errors.append(f"{tag} quote sits inside a code fence")
        if c.get("anchor", "centroid") not in ANCHORS:
            errors.append(f"{tag} anchor must be one of {ANCHORS}")
        match = c.get("match")
        if not isinstance(match, dict) or not match.get("names"):
            errors.append(f"{tag} match.names missing")
            continue
        counts = {v: len(resolve(m, match)) for v, m in sorted(models.items())}
        if latest and counts[latest] == 0:
            errors.append(f"{tag} matches no element of {latest}: {match}")
        report.append(f"  {tag:14} " + " ".join(f"{v}:{n}" for v, n in counts.items()))
    return errors, report


def experiment_files(exp_id):
    """(callouts path, rationale path, {version: model path}) or None."""
    fable = os.path.join(REPO_ROOT, "experiments", exp_id, "Fable")
    found = glob.glob(os.path.join(fable, "experiment_*_callouts.json"))
    if not found:
        return None
    docs = glob.glob(os.path.join(fable, "experiment_*_design_rationale.md"))
    models = {}
    for p in glob.glob(os.path.join(MODELS_DIR, exp_id, "fable_v*.json")):
        models[re.search(r"(v\d+)\.json$", p).group(1)] = p
    return sorted(found)[0], (sorted(docs)[0] if docs else None), models


def check_all(only=""):
    ok = True
    for exp_dir in sorted(glob.glob(os.path.join(REPO_ROOT, "experiments", "*"))):
        exp_id = os.path.basename(exp_dir)
        if only and only not in exp_id:
            continue
        files = experiment_files(exp_id)
        if not files:
            continue
        callouts_path, doc_path, model_paths = files
        print(exp_id)
        if not doc_path:
            print("  ERROR: no design rationale next to the callouts")
            ok = False
            continue
        with open(callouts_path, encoding="utf-8") as fh:
            data = json.load(fh)
        with open(doc_path, encoding="utf-8") as fh:
            md = fh.read()
        models = {}
        for v, p in model_paths.items():
            with open(p, encoding="utf-8") as fh:
                models[v] = json.load(fh)
        errors, report = check(data, md, models)
        for line in report:
            print(line)
        for e in errors:
            print(f"  ERROR: {e}")
        ok = ok and not errors
    return ok


def print_names(only):
    """Element name patterns (digits -> #) per collection of the latest
    Fable version of each matching experiment, with counts."""
    for exp_dir in sorted(glob.glob(os.path.join(REPO_ROOT, "experiments", "*"))):
        exp_id = os.path.basename(exp_dir)
        if only and only not in exp_id:
            continue
        versions = sorted(glob.glob(os.path.join(MODELS_DIR, exp_id, "fable_v*.json")))
        if not versions:
            continue
        with open(versions[-1], encoding="utf-8") as fh:
            model = json.load(fh)
        colls = model["collections"]
        groups = collections.defaultdict(collections.Counter)
        for row in model["boxes"]:
            groups[colls[row[1]]][re.sub(r"\d+", "#", row[0])] += 1
        for mesh in model["meshes"]:
            groups[colls[mesh["collection"]]][re.sub(r"\d+", "#", mesh["name"])] += 1
        print(f"{exp_id} ({os.path.basename(versions[-1])})")
        for coll in sorted(groups):
            names = ", ".join(f"{k} x{v}" for k, v in sorted(groups[coll].items()))
            print(f"  {coll or '(no collection)'}: {names}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--names", default=None, metavar="EXP",
                    help="print element name patterns of an experiment")
    ap.add_argument("--only", default="")
    args = ap.parse_args()
    if args.names is not None:
        print_names(args.names)
    elif args.check:
        sys.exit(0 if check_all(args.only) else 1)
    else:
        ap.print_help()
