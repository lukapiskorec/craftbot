"""Rasterize a drawing sheet SVG to PNG with headless Chrome, whole or zoomed.

PDF sheets cannot be looked at from a script, so `drafting.SheetSet.write`
also writes SVG; this turns one into a PNG an agent can read.

    python tools/sheet_png.py sheet.svg out.png                       # the whole sheet, 1500 px wide
    python tools/sheet_png.py sheet.svg out.png --zoom 150 120 130    # a 130 mm square with its top-left corner
                                                                      # 150 mm from the left, 120 mm from the top

Looks for Chrome in the usual places; pass --chrome to override. Standard
library only.

Provenance: experiment 16 fabrication set, where every sheet was checked this way.
"""
import os
import re
import sys
import shutil
import argparse
import tempfile
import subprocess

CHROME = [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
          r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
          "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"]


def find_chrome():
    """Path of a Chrome or Chromium executable, or None."""
    for path in CHROME:
        if os.path.isfile(path):
            return path
    return shutil.which("google-chrome") or shutil.which("chromium") or shutil.which("chrome")


def render(svg_path, png_path, zoom=None, width=1500, chrome=None):
    """Write `png_path` from `svg_path`; `zoom` is (left, top, size) in sheet mm measured from the top-left corner."""
    text = open(svg_path, encoding="utf-8").read()
    root = re.search(r"<svg[^>]*>", text).group(0)
    w, h = (float(v) for v in re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', root).groups())
    box = (0, 0, w, h) if zoom is None else (zoom[0], zoom[1], zoom[2], zoom[2])
    fitted = re.sub(r'width="[^"]*" height="[^"]*" viewBox="[^"]*"',
                    'width="100%%" viewBox="%s %s %s %s"' % box, root, count=1)
    height = round(width*box[3]/box[2])
    with tempfile.TemporaryDirectory() as tmp:
        copy = os.path.join(tmp, "sheet.svg")
        with open(copy, "w", encoding="utf-8") as f:
            f.write(text.replace(root, fitted, 1))
        subprocess.run([chrome or find_chrome(), "--headless=new", "--disable-gpu", "--hide-scrollbars",
                        f"--window-size={width},{height}", "--screenshot=" + os.path.abspath(png_path),
                        "file:///" + copy.replace(os.sep, "/").lstrip("/")],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("svg")
    parser.add_argument("png")
    parser.add_argument("--zoom", nargs=3, type=float, metavar=("LEFT", "TOP", "SIZE"), help="square region in sheet mm from the top-left corner")
    parser.add_argument("--width", type=int, default=1500, help="PNG width in pixels")
    parser.add_argument("--chrome", help="path of the Chrome executable")
    args = parser.parse_args()
    if not (args.chrome or find_chrome()):
        sys.exit("Chrome not found: pass --chrome <path>")
    render(args.svg, args.png, args.zoom, args.width, args.chrome)
    print(f"wrote {args.png}")
