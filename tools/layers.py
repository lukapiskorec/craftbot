# Element -> layer classification for the viewer, baked into the model JSON.
#
# Layers (see the LAYERS section of the viewer):
#   frame         timber/steel members of walls, floors and roof - the structure
#   cladding ext  outer skin of the exterior walls (ply, boards, tiles, battens)
#   cladding int  inner skin of the exterior walls
#   interior      boards on interior walls, skirting
#   roof          roof covering, fascias, roof sheathing, uppermost ceiling
#   floors        floor and ceiling coverings inside, slabs, decks
#   foundations   footings, plinths, podium - everything under/outside the house
#   fixtures      windows, doors, louvres, glass, railings, stairs
#   other         nothing matched - the audit flags these; aim for zero
#
# Rules are regexes tried in order against "<collection path>|<name>" in
# lower case; first match wins. OVERRIDES (per experiment id) run before the
# generic RULES: they resolve naming that only makes sense in that script.
#
# Usage:
#   python tools/layers.py --audit [--only 04]   # table of every name family -> layer
#   python tools/layers.py --bake  [--only 04]   # rewrite viewer/models/*/*.json

import argparse
import collections
import glob
import json
import os
import re
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(REPO_ROOT, "viewer", "models")

LAYERS = ["frame", "cladding ext", "cladding int", "interior", "roof", "floors",
          "foundations", "fixtures", "other"]

FRAME, CLAD_EXT, CLAD_INT, INTERIOR, ROOF, FLOORS, FOUND, FIXT, OTHER = LAYERS

RULES = [
    (FOUND, r"found|footing|plinth|podium|gravel|stilt|\bpad|padslab|steppad"),
    (ROOF, r"kerb"),  # skylight kerbs, before "skylight" -> fixtures
    # Members that are structure whatever collection they sit in
    (FRAME, r"stud|joist|rafter|truss|purlin|nog|bearer|girder|stiffener|trimmer"
            r"|chord|strut|brace|king|queen|collar|hip_|valley|jack|header|lintel"
            r"|fink|web|beam|ridge(?!_?cap)"),
    (FRAME, r"structure|framing|frame"),  # collection-level
    (FIXT, r"glass|glaz|window|win(?:jamb|head|sill|mullion)|door|louv|baluster"
           r"|balustrade|(?<!eave_)rail|stair|flight|tread|stringer|step|landing"
           r"|skylight|canopy|mullion|transom|jamb|entrance|leaf|shutter|grill"
           r"|opening"),
    (INTERIOR, r"ply_p\d|skirt|shear_"),
    (CLAD_EXT, r"gable_ply|gable_sheath"),
    (ROOF, r"roof_?clad|roof_?sheet|roofs?_?board|roofw_board|roof_?deck|roof/deck"
           r"|roof_?slab|roof_cover|covering|tray|fascia|barge|ridge_?cap|verge"
           r"|ceiling|^(?!.*(facade|exterior|interior|wall)).*sheath|batten"),
    (FLOORS, r"floor_?board|subfloor|deck_?board|decking|slab|flooring|floors/"
             r"|patio_deck|deck_p|floor_?deck|^\|floor(?:_|\d|$)"),
    (CLAD_INT, r"_int|int_|inner|lining|_in(?:_|\d|$)|interior"),
    (CLAD_EXT, r"ext|outer|_out|clad|siding|weatherboard|tile|bead|panel_|sheath"
               r"|facade|board"),
    (FRAME, r"post|column|plate|sill|purlin|wall|pier|core|party|corridor|leg"
            r"|portal|portico|gusset|sole|rib|cleat|ledger|runner|knee|tie|jowl"
            r"|bent|block|rim|cage|bar|box|principal|finial|corner|support"),
]

# Collections that hold the whole model tell nothing about an element
UNINFORMATIVE_COLLECTIONS = {"structure"}

# Experiment id prefix -> [(regex, layer)], tried before RULES. Mostly the
# ChatGPT runs, which name everything ad hoc and use no collections.
OVERRIDES = {
    "02": [
        (r"^\|batten", ROOF),
        (r"^\|", FRAME),                  # ChatGPT run: timber only
    ],
    "03": [
        (r"shear_panels\|", INTERIOR),    # ply on the bath/storage walls
        (r"^\|shell_wall_short", CLAD_EXT),
        (r"^\|skylight.*plate", FRAME),
        (r"^\|int_", INTERIOR),           # ChatGPT run: interior walls as boxes
        (r"^\|shell_long", CLAD_EXT),
        (r"^\|(loft_deck|shell_floor)", FLOORS),
    ],
    "04": [
        (r"verandah\|ver_column", FRAME),
        (r"verandah\|ver_toprail", FRAME),
        (r"beading\|skirt_(?!p)", CLAD_INT),  # skirting of the exterior walls (Skirt_P* stays interior)
        (r"^\|door_?lintel", FIXT),
        (r"^\|(bottom|top)_[nsew]", FRAME),   # ChatGPT run: wall plates
        (r"^\|roof(_slope_[ns])?(_|\d|$)", ROOF),
    ],
    "05": [
        (r"^\|(bottom|top)_[nsew]", FRAME),
        (r"^\|roof(_slope_[ns])?(_|\d|$)", ROOF),
    ],
    "06": [
        (r"\|tray_.*_rib", FRAME),         # ribs of the roof trays
    ],
    "07": [
        (r"^\|(bottom|top)_[nsew]", FRAME),
        (r"^\|roof_rul", FRAME),          # before the generic roof_* rule below
        (r"^\|roof(_slope_[ns])?(_|\d|$)", ROOF),
        (r"^\|tess_stud", FRAME),
        (r"^\|(shard|south_horizontal_cut|tess_)", CLAD_EXT),
        (r"^\|mezzanine_hanger", FRAME),
    ],
    "08": [
        (r"battens\|batint", CLAD_INT),
        (r"battens\|", CLAD_EXT),          # BatExt, rails, sole plates, floor bands
        (r"core\|core_", CLAD_INT),         # infill-panel core, between the plies
        (r"^\|wall_", CLAD_EXT),            # ChatGPT run: Wall_* are the infill panels
        (r"^\|postext", FRAME),
        (r"^\|frame_", FIXT),              # ChatGPT run: window/door frames
        (r"^\|skylightroof", ROOF),
        (r"\|canopystrut", FIXT),
    ],
    "09": [
        (r"\|(landing_|flight_)", FIXT),  # stairs everywhere, podium included
        (r"podium", FOUND),                # the rest of the podium, before the name rules below
        (r"^\|ext_", FRAME),               # ChatGPT run: CLT exterior walls
        (r"\|roof_(?!glass)", ROOF),       # plates, CLT roof panels, covering (skylight glass stays fixtures)
        (r"\|(int_|elev_|partition_|corridor_|ledger_|knee_|parting_)", INTERIOR),
        (r"\|core_(?!slab)", INTERIOR),    # core walls (core slabs stay floors)
        (r"\|[snew]_", CLAD_EXT),          # ChatGPT run: S_/N_/E_/W_ piers and wall bands
        (r"\|(wall_|gable_)", CLAD_INT),
        (r"\|rib_", FLOORS),
    ],
    "12": [
        (r"^\|dormer_window", FRAME),
    ],
}

_compiled = {}


def _rules_for(exp_id):
    key = exp_id[:2]
    if key not in _compiled:
        over = [(re.compile(rx), layer) for rx, layer in OVERRIDES.get(key, [])]
        generic = [(re.compile(rx), layer) for layer, rx in RULES]
        _compiled[key] = over + generic
    return _compiled[key]


def classify(exp_id, collection, name):
    """Layer name for one element."""
    coll = (collection or "").lower()
    if coll in UNINFORMATIVE_COLLECTIONS:
        coll = ""
    text = f"{coll}|{name or ''}".lower()
    for rx, layer in _rules_for(exp_id):
        if rx.search(text):
            return layer
    return OTHER


def classify_index(exp_id, collection, name):
    return LAYERS.index(classify(exp_id, collection, name))


def experiment_of(path):
    """Experiment id from a model JSON path or an export source path."""
    m = re.search(r"(\d\d_[A-Za-z0-9_\-]+?_Blender_Python)", path.replace("\\", "/"))
    return m.group(1) if m else ""


def bake_dict(model, exp_id):
    """Add layer indices to a craftbot-model dict in place (idempotent)."""
    colls = model["collections"]
    model["layers"] = list(LAYERS)
    for row in model["boxes"]:
        li = classify_index(exp_id, colls[row[1]], row[0])
        if len(row) > 14:
            row[14] = li
        else:
            row.append(li)
    for mesh in model["meshes"]:
        mesh["layer"] = classify_index(exp_id, colls[mesh["collection"]], mesh["name"])
    return model


def model_files(only):
    """Model JSONs (<agent>_vNN.json) - not the rationale/callouts files beside them."""
    files = sorted(glob.glob(os.path.join(MODELS_DIR, "*", "*_v[0-9][0-9].json")))
    return [f for f in files if not only or only in f]


def bake(only):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import model_export_core as core
    for path in model_files(only):
        with open(path, encoding="utf-8") as fh:
            model = json.load(fh)
        bake_dict(model, experiment_of(path))
        core.dump_compact(model, path)
        print(f"baked {os.path.relpath(path, REPO_ROOT)}")


def family(name):
    """Name with trailing index/digits removed: Rafter_S_12 -> Rafter_S."""
    return re.sub(r"[_\-]?\d.*$", "", name) or name


def audit(only):
    """Print one line per (experiment, collection, name family) with its layer.
    Counts are summed over all versions of all agents."""
    rows = collections.Counter()
    for path in model_files(only):
        exp_id = experiment_of(path)
        with open(path, encoding="utf-8") as fh:
            model = json.load(fh)
        colls = model["collections"]
        for row in model["boxes"]:
            rows[(exp_id[:2], colls[row[1]], family(row[0]), classify(exp_id, colls[row[1]], row[0]))] += 1
        for mesh in model["meshes"]:
            coll = colls[mesh["collection"]]
            rows[(exp_id[:2], coll, family(mesh["name"]), classify(exp_id, coll, mesh["name"]))] += 1
    unmatched = 0
    for (exp, coll, fam, layer), n in sorted(rows.items()):
        flag = "  <-- OTHER" if layer == OTHER else ""
        unmatched += n if layer == OTHER else 0
        print(f"{exp} | {layer:12} | {coll or '(none)':40} | {fam:32} | {n}{flag}")
    print(f"\n{unmatched} elements in 'other'")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--audit", action="store_true")
    ap.add_argument("--bake", action="store_true")
    ap.add_argument("--only", default="", help="substring of the model path")
    args = ap.parse_args()
    if args.audit:
        audit(args.only)
    elif args.bake:
        bake(args.only)
    else:
        ap.print_help()
