"""Apply the default Levels + adaptive line overlay to a presentation batch.

Run inside Blender:
  blender --background --factory-startup --python-exit-code 1 \
    --python tools/compose_presentation_batch.py -- <batch_dir>

The batch must contain sources/<model>/cycles_view_*_none_<foundation-state>.png
and matching lines_view_*.png files. Final images go to renders/<model>/.
"""

import argparse
import html
import json
import os
import re
import sys
from pathlib import Path

import bpy
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from adjust_line_levels import adjust_pixels, unit_checks as levels_unit_checks
from composite_line_overlay import blend_pixels, read_pixels, save_pixels


SETTINGS = dict(shadow_anchor=.90, output_white=.96, background_white=.9999,
                light_strength=.28, dark_strength=.88, gamma=.75,
                mask_threshold=.03, line_width=1)


def compose_pair(cycles_path, lines_path, output_path):
    cycles_image, cycles = read_pixels(cycles_path)
    lines_image, lines = read_pixels(lines_path)
    if tuple(cycles_image.size) != tuple(lines_image.size):
        raise ValueError(f"Image sizes differ: {cycles_path} and {lines_path}")
    width, height = cycles_image.size
    adjusted = adjust_pixels(lines, SETTINGS["shadow_anchor"], SETTINGS["output_white"],
                             SETTINGS["background_white"])
    output = blend_pixels(cycles, adjusted.ravel(), SETTINGS["light_strength"],
                          SETTINGS["dark_strength"], SETTINGS["gamma"],
                          SETTINGS["mask_threshold"], width, height,
                          line_width=SETTINGS["line_width"])
    save_pixels(output, width, height, output_path, "PresentationComposite")
    bpy.data.images.remove(cycles_image)
    bpy.data.images.remove(lines_image)


def write_gallery(root, records):
    by_model = {}
    for record in records:
        by_model.setdefault(record["model"], {})[record["view"]] = record["output"]
    views_order = sorted({record["view"] for record in records})
    rows = []
    for model, views in sorted(by_model.items()):
        cells = []
        for view in views_order:
            path = views.get(view)
            cells.append(f'<td><a href="{html.escape(path)}"><img loading="lazy" src="{html.escape(path)}"></a><small>{html.escape(view)}</small></td>' if path else "<td></td>")
        rows.append(f"<tr><th>{html.escape(model)}</th>{''.join(cells)}</tr>")
    document = """<!doctype html><meta charset=utf-8><title>CraftBot presentation batch</title>
<style>body{font:14px system-ui;margin:20px;background:#eee;color:#222}table{border-collapse:collapse;width:100%}th{position:sticky;left:0;background:#eee;text-align:left;padding:8px;min-width:120px}td{padding:5px;vertical-align:top}img{display:block;width:100%;min-width:220px;background:white}small{display:block;margin-top:4px}</style>
<table>ROWS</table>""".replace("ROWS", "".join(rows))
    (root / "index.html").write_text(document, encoding="utf-8")


def main(root):
    sources = root / "sources"
    records = []
    pattern = re.compile(r"^cycles_view_(.+)_none_(?:no_foundation|with_foundation)\.png$")
    for cycles_path in sorted(sources.rglob("cycles_view_*.png")):
        match = pattern.match(cycles_path.name)
        if not match:
            continue
        model = cycles_path.parent.relative_to(sources).as_posix()
        view = match.group(1)
        lines_path = cycles_path.with_name(f"lines_view_{view}.png")
        if not lines_path.exists():
            raise FileNotFoundError(f"Missing matching Workbench source: {lines_path}")
        output_path = root / "renders" / model / f"{view}.png"
        compose_pair(cycles_path, lines_path, output_path)
        records.append(dict(model=model, view=view,
                            cycles=cycles_path.relative_to(root).as_posix(),
                            lines=lines_path.relative_to(root).as_posix(),
                            output=output_path.relative_to(root).as_posix()))
        print("COMPOSED", output_path, flush=True)
    if not records:
        raise FileNotFoundError(f"No Cycles presentation sources found under {sources}")
    manifest = dict(settings=SETTINGS,
                    expected_views=sorted({record["view"] for record in records}), images=records)
    (root / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    write_gallery(root, records)
    print(f"COMPOSED_BATCH {len(records)} images", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("batch_dir", type=Path)
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    levels_unit_checks()
    main(args.batch_dir.resolve())
