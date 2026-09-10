"""Apply a highlight-only linear Levels adjustment to a Workbench line image.

Run inside Blender:
  blender --background --factory-startup --python-exit-code 1 \
    --python tools/adjust_line_levels.py -- input.png output.png
"""

import argparse
import sys
from pathlib import Path

import bpy
import numpy as np


def linear_to_srgb(values):
    return np.where(values <= .0031308, values * 12.92,
                    1.055 * np.power(values, 1 / 2.4) - .055)


def srgb_to_linear(values):
    return np.where(values <= .04045, values / 12.92,
                    np.power((values + .055) / 1.055, 2.4))


def levels_lut(shadow_anchor=.90, output_white=.96, background_white=.9999, size=4096):
    """Build a linear highlight-remapping LUT; shadows and pure white are fixed."""
    values = np.linspace(0, 1, size, dtype=np.float32)
    mapped = values.copy()
    highlights = (values > shadow_anchor) & (values < background_white)
    mapped[highlights] = shadow_anchor + (values[highlights] - shadow_anchor) * (
        (output_white - shadow_anchor) / (background_white - shadow_anchor))
    mapped[values >= background_white] = 1
    return mapped


def apply_lut(values, lut):
    positions = np.clip(values, 0, 1) * (len(lut) - 1)
    lower = positions.astype(np.int32)
    upper = np.minimum(lower + 1, len(lut) - 1)
    fraction = positions - lower
    return lut[lower] * (1 - fraction) + lut[upper] * fraction


def adjust_pixels(pixels, shadow_anchor=.90, output_white=.96, background_white=.9999):
    rgba = pixels.reshape((-1, 4)).copy()
    srgb = linear_to_srgb(np.clip(rgba[:, :3], 0, 1))
    rgba[:, :3] = srgb_to_linear(apply_lut(srgb, levels_lut(
        shadow_anchor, output_white, background_white)))
    return rgba


def adjust(input_path, output_path, shadow_anchor=.90, output_white=.96, background_white=.9999):
    source = bpy.data.images.load(str(input_path.resolve()), check_existing=False)
    pixels = np.empty(len(source.pixels), dtype=np.float32)
    source.pixels.foreach_get(pixels)
    adjusted = adjust_pixels(pixels, shadow_anchor, output_white, background_white)
    output = bpy.data.images.new("AdjustedLineLevels", width=source.size[0], height=source.size[1], alpha=True)
    output.colorspace_settings.name = "sRGB"
    output.pixels.foreach_set(adjusted.ravel())
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output.filepath_raw = str(output_path.resolve())
    output.file_format = "PNG"
    output.save()


def unit_checks():
    samples = np.array([[.50, .50, .50, 1], [.90, .90, .90, 1],
                        [.95, .95, .95, 1], [1, 1, 1, 1]], dtype=np.float32)
    linear = samples.copy()
    linear[:, :3] = srgb_to_linear(samples[:, :3])
    result = linear_to_srgb(adjust_pixels(linear.ravel(), .90, .92)[:, :3])
    assert np.allclose(result[0], .50, atol=2e-4) and np.allclose(result[1], .90, atol=2e-4)
    assert .90 < result[2, 0] < .92, "Light gray must move toward the preserved dark anchor"
    assert np.allclose(result[3], 1, atol=2e-4), "Pure-white background must remain white"
    identity = linear_to_srgb(adjust_pixels(linear.ravel(), .90, 1)[:, :3])
    assert np.allclose(identity, samples[:, :3], atol=3e-4), "Output white 1 must be the identity mapping"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--shadow-anchor", type=float, default=.90)
    parser.add_argument("--output-white", type=float, default=.96)
    parser.add_argument("--background-white", type=float, default=.9999)
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    if not 0 <= args.shadow_anchor <= args.output_white <= args.background_white <= 1:
        parser.error("values must satisfy 0 <= shadow anchor <= output white <= background white <= 1")
    unit_checks()
    adjust(args.input, args.output, args.shadow_anchor, args.output_white, args.background_white)
    print(args.output)
