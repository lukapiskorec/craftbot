"""Overlap triage: group penetrating pairs into name families (pure Python).

The overlap check lists pairs deepest first and the harness prints the
first 80; a model with hundreds of pairs usually has three or four causes.
`families()` collapses the pair list into (family_a, family_b, depth) rows
with a count and one example, so the Builder reads a table of causes
instead of a wall of names.

    from triage import families, family, format_families
    rows = families(hits)                      # hits = [(depth_m, name_a, name_b), ...]
    print(format_families(rows))

Provenance: the summarize_check.py scratch script of the experiment 14
Fable run, promoted here.
"""
import collections
import re

_TRAIL = re.compile(r"[_\-]?\d.*$")


def family(name):
    """Name with the first trailing index and everything after it removed:
    'TowerClad_S_B1_026' -> 'TowerClad_S_B', 'Rafter_03N_tail' -> 'Rafter'."""
    return _TRAIL.sub("", name) or name


def families(hits, depth_mm_round=1):
    """[(count, family_a, family_b, depth_mm, example_a, example_b)] sorted by
    count, then depth. Depth is rounded so one geometric cause (a constant
    offset) lands in one row."""
    rows = collections.OrderedDict()
    for depth, a, b in hits:
        d = round(depth * 1000.0, depth_mm_round)
        key = (family(a), family(b), d)
        if key not in rows:
            rows[key] = [0, a, b]
        rows[key][0] += 1
    out = [(n, fa, fb, d, ea, eb) for (fa, fb, d), (n, ea, eb) in rows.items()]
    out.sort(key=lambda r: (-r[0], -r[3]))
    return out


def format_families(rows, limit=40):
    lines = [f"OVERLAP FAMILIES: {len(rows)} (count  depth  family a  x  family b   e.g. a x b)"]
    for n, fa, fb, d, ea, eb in rows[:limit]:
        lines.append(f"  {n:5d}  {d:7.1f} mm  {fa}  x  {fb}   e.g. {ea} x {eb}")
    if len(rows) > limit:
        lines.append(f"  ... {len(rows) - limit} more families")
    return "\n".join(lines)
