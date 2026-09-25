"""Text widths from the font files that headless Chrome prints with.

`vector_pdf.text_width` guesses with Helvetica widths, good enough to place
a label. Justified newsprint columns and boxes drawn around a text need the
real advance of the face in use, so `advance` reads it from the font file
with Pillow (already a dependency of `drawing_assets.trace`). Families: the
Windows faces Chrome uses on this machine and the files in `viewer/fonts`.
A family without a file falls back to the Helvetica guess.

    advance('brief, review rounds', 3.2, 'Times New Roman', italic=True)      # mm

Provenance: experiment 16 fabrication set, the newsprint front page.
"""
import os
from functools import lru_cache

from vector_pdf import text_width, FONT_FILES

WINDOWS = os.path.join(os.environ.get('WINDIR', 'C:/Windows'), 'Fonts')
# family: (regular, bold, italic, bold italic) files
FILES = {'Times New Roman': ('times.ttf', 'timesbd.ttf', 'timesi.ttf', 'timesbi.ttf'),
         'Georgia': ('georgia.ttf', 'georgiab.ttf', 'georgiai.ttf', 'georgiaz.ttf'),
         'Arial': ('arial.ttf', 'arialbd.ttf', 'ariali.ttf', 'arialbi.ttf'),
         'Segoe UI': ('segoeui.ttf', 'segoeuib.ttf', 'segoeuii.ttf', 'segoeuiz.ttf')}
EM = 1000      # px the faces are loaded at; widths scale linearly


@lru_cache(maxsize=None)
def face(family, bold=False, italic=False):
    """The Pillow face of a family in one style, or None when there is no file for it."""
    try:
        from PIL import ImageFont
    except ImportError:
        return None
    if family in FONT_FILES:
        path = FONT_FILES[family]
    elif family in FILES:
        path = os.path.join(WINDOWS, FILES[family][(1 if bold else 0)+(2 if italic else 0)])
    else:
        return None
    return ImageFont.truetype(path, EM) if os.path.exists(path) else None


@lru_cache(maxsize=None)
def length(text, family, bold, italic):
    """Advance of `text` in em, from the font file; None without one."""
    f = face(family, bold, italic)
    return f.getlength(text)/EM if f else None


def advance(text, size, family='Times New Roman', weight=400, italic=False):
    """Width in mm of `text` set at `size` mm in the family and style, from the font file."""
    em = length(text, family, weight >= 600, italic)
    return em*size if em is not None else text_width(text, size)
