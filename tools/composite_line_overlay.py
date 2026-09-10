"""Multiply a Workbench outline mask onto a matching Cycles render.

Run inside Blender:
  blender --background --factory-startup --python-exit-code 1 \
    --python tools/composite_line_overlay.py -- cycles.png lines.png output.png
"""

import argparse
import sys
from pathlib import Path

import bpy
import numpy as np


def edge_mask(lines, width, height, mask_threshold=.03, hardening=0, binary=False, line_width=1):
    """Extract and optionally harden/expand the Workbench outline mask."""
    line_image = lines.reshape((-1, 4))
    line_luma = line_image[:, :3] @ np.array((.2126, .7152, .0722), dtype=np.float32)
    mask = np.clip((1.0 - line_luma - mask_threshold) / (1.0 - mask_threshold), 0.0, 1.0)
    hardening = 1.0 if binary else hardening
    if hardening:
        solid = (mask > 0).astype(np.float32)
        mask += hardening * (solid - mask)
    if line_width > 1:
        original = mask.reshape((height, width))
        before = (line_width - 1) // 2
        after = line_width // 2
        padded = np.pad(original, ((before, after), (before, after)), mode="constant")
        expanded = np.zeros_like(original)
        for row in range(line_width):
            for column in range(line_width):
                expanded = np.maximum(expanded, padded[row:row + height, column:column + width])
        mask = expanded.ravel()
    return mask


def blend_pixels(cycles, lines, light_strength, dark_strength, gamma, mask_threshold,
                 width=None, height=None, mask_hardening=0, binary_mask=False, line_width=1):
    """Return RGBA pixels; darker source pixels receive the stronger line overlay."""
    source = cycles.reshape((-1, 4))
    mask = edge_mask(lines, width, height, mask_threshold, mask_hardening, binary_mask, line_width)
    source_luma = np.clip(source[:, :3] @ np.array((.2126, .7152, .0722), dtype=np.float32), 0.0, 1.0)
    strength = light_strength + (dark_strength - light_strength) * np.power(1.0 - source_luma, gamma)
    output = source.copy()
    output[:, :3] *= 1.0 - mask[:, None] * strength[:, None]
    return output


def read_pixels(path):
    image = bpy.data.images.load(str(path.resolve()), check_existing=False)
    pixels = np.empty(len(image.pixels), dtype=np.float32)
    image.pixels.foreach_get(pixels)
    return image, pixels


def save_pixels(pixels, width, height, path, name):
    image = bpy.data.images.new(name, width=width, height=height, alpha=True)
    image.colorspace_settings.name = "sRGB"
    image.pixels.foreach_set(pixels.ravel())
    path.parent.mkdir(parents=True, exist_ok=True)
    image.filepath_raw = str(path.resolve())
    image.file_format = "PNG"
    image.save()
    bpy.data.images.remove(image)


def composite(cycles_path, lines_path, output_path, light_strength=.28, dark_strength=.88,
              gamma=.75, mask_threshold=.03, mask_hardening=0, binary_mask=False, line_width=1,
              mask_output=None):
    cycles_image, cycles = read_pixels(cycles_path)
    lines_image, lines = read_pixels(lines_path)
    if tuple(cycles_image.size) != tuple(lines_image.size):
        raise ValueError(f"Image sizes differ: {tuple(cycles_image.size)} and {tuple(lines_image.size)}")
    width, height = cycles_image.size
    output = blend_pixels(cycles, lines, light_strength, dark_strength, gamma, mask_threshold,
                          width, height, mask_hardening, binary_mask, line_width)
    save_pixels(output, width, height, output_path, "LineComposite")
    if mask_output:
        mask = edge_mask(lines, width, height, mask_threshold, mask_hardening, binary_mask, line_width)
        preview = np.ones((width * height, 4), dtype=np.float32)
        preview[:, :3] = 1.0 - mask[:, None]
        save_pixels(preview, width, height, mask_output, "LineMask")
    bpy.data.images.remove(cycles_image)
    bpy.data.images.remove(lines_image)


def unit_checks():
    source = np.array([[.9, .9, .9, 1], [.2, .2, .2, 1], [.5, .5, .5, 1]], dtype=np.float32).ravel()
    lines = np.array([[0, 0, 0, 1], [0, 0, 0, 1], [1, 1, 1, 1]], dtype=np.float32).ravel()
    result = blend_pixels(source, lines, .25, .9, .75, .03).reshape((-1, 4))
    light_fraction = result[0, 0] / .9
    dark_fraction = result[1, 0] / .2
    assert dark_fraction < light_fraction, "Dark surfaces must receive a stronger edge overlay"
    assert np.allclose(result[2], (.5, .5, .5, 1)), "White mask pixels must preserve the source"
    white = np.ones((9, 4), dtype=np.float32)
    center_line = white.copy()
    center_line[4, :3] = 0
    expanded = blend_pixels(white.ravel(), center_line.ravel(), 1, 1, 1, 0,
                            width=3, height=3, line_width=3).reshape((-1, 4))
    assert np.all(expanded[:, :3] == 0), "A three-pixel kernel must expand the center line to 3 x 3"
    gray_line = white.copy()
    gray_line[4, :3] = .9
    original = edge_mask(gray_line.ravel(), 3, 3, mask_threshold=.01)
    middle = edge_mask(gray_line.ravel(), 3, 3, mask_threshold=.01, hardening=.5)
    hardened = edge_mask(gray_line.ravel(), 3, 3, mask_threshold=.01, binary=True)
    assert original[4] < middle[4] < hardened[4], "Hardening grades must increase mask coverage monotonically"
    assert hardened[4] == 1, "Binary masks must turn a faint accepted line completely black"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cycles", type=Path)
    parser.add_argument("lines", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--light-strength", type=float, default=.28,
                        help="Line opacity over a white source pixel; default .28")
    parser.add_argument("--dark-strength", type=float, default=.88,
                        help="Line opacity over a black source pixel; default .88")
    parser.add_argument("--gamma", type=float, default=.75,
                        help="Source-luminance response curve; default .75")
    parser.add_argument("--mask-threshold", type=float, default=.03,
                        help="Ignore this much off-white variation in the line render; default .03")
    parser.add_argument("--binary-mask", action="store_true",
                        help="Turn every accepted gray outline pixel into a solid black mask pixel")
    parser.add_argument("--mask-hardening", type=float, default=0,
                        help="Blend toward a binary mask: 0 keeps gray antialiasing, 1 fully hardens")
    parser.add_argument("--line-width", type=int, default=1,
                        help="Raster mask width: 1 keeps Workbench width; 2 or 3 expands it")
    parser.add_argument("--mask-output", type=Path,
                        help="Optional path for the processed black-on-white mask PNG")
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    if not 0 <= args.light_strength <= args.dark_strength <= 1:
        parser.error("strengths must satisfy 0 <= light <= dark <= 1")
    if (args.gamma <= 0 or not 0 <= args.mask_threshold < 1 or
            not 0 <= args.mask_hardening <= 1 or args.line_width < 1):
        parser.error("gamma and line width must be positive; mask threshold and hardening must be in [0, 1]")
    unit_checks()
    composite(args.cycles, args.lines, args.output, args.light_strength, args.dark_strength,
              args.gamma, args.mask_threshold, args.mask_hardening, args.binary_mask,
              args.line_width, args.mask_output)
    print(args.output)
