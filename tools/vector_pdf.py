"""Vector drawing canvas that writes PDF and SVG with the standard library.

A `Sheet` is one page in millimetres with the origin at the bottom left. It
collects filled polygons, lines, circles and text, then writes itself as a
PDF page or an SVG file. `write_pdf` puts any number of sheets in one PDF.
Text is Helvetica, Latin-1 only.

    sheet = Sheet(*A2)
    sheet.poly([(10, 10), (60, 10), (60, 40)], fill=1.0)
    sheet.text(10, 45, 'triangle', 3)
    write_pdf('out.pdf', [sheet])

Provenance: experiment 16 fabrication set; the repo has no PDF library.
"""
import math
import zlib

A2 = (420.0, 594.0)     # mm, portrait; use A2[::-1] for landscape
A3 = (297.0, 420.0)
THIN, MEDIUM, HEAVY = 0.13, 0.25, 0.45   # line widths, mm

# Helvetica advance widths per 1000 em, for anchoring text in the PDF.
WIDTHS = {' ': 278, '.': 278, ',': 278, ':': 278, '+': 584, '-': 333, '=': 584, '{': 334, '}': 334,
          'i': 222, 'l': 222, 'j': 222, 't': 278, 'f': 278, 'r': 333, 'm': 833, 'w': 722, 'M': 833, 'W': 944, 'I': 278}


def text_width(s, size):
    """Approximate width in mm of `s` set in Helvetica at `size` mm."""
    return sum(WIDTHS.get(c, 667 if c.isupper() else 556 if c.isdigit() else 530) for c in s)*size/1000


class Sheet:
    """One page in mm, origin bottom-left. Collects polygons, lines and
    text, then writes itself as a PDF page stream or an SVG file."""

    def __init__(self, width, height):
        self.w, self.h, self.ops = width, height, []

    def poly(self, pts, fill=1.0, lw=THIN, dash=False, stroke=0.0):
        """Closed polygon; `fill` and `stroke` are greys 0..1, `fill=None` leaves it open to what is below."""
        self.ops.append(('poly', pts, fill, lw, dash, stroke))

    def line(self, a, b, lw=THIN, dash=False):
        """Straight line from a to b."""
        self.ops.append(('poly', [a, b], None, lw, dash, 0.0))

    def circle(self, x, y, r, fill=1.0, lw=THIN):
        """Circle as a 24-gon."""
        self.poly([(x+r*math.cos(i*math.pi/12), y+r*math.sin(i*math.pi/12)) for i in range(24)], fill, lw)

    def text(self, x, y, s, size=2.5, anchor='start'):
        """Text with its baseline at (x, y); `anchor` is 'start', 'middle' or 'end'."""
        self.ops.append(('text', x, y, s, size, anchor))

    def pdf_stream(self):
        """The page as an uncompressed PDF content stream."""
        k = 72/25.4
        out = ['1 J 1 j']
        for op in self.ops:
            if op[0] == 'poly':
                _, pts, fill, lw, dash, stroke = op
                out.append(f'{lw*k:.3f} w {stroke:.2f} G ' + ('[2 1.5] 0 d' if dash else '[] 0 d'))
                path = ' '.join(f'{x*k:.2f} {y*k:.2f} {"m" if i == 0 else "l"}' for i, (x, y) in enumerate(pts))
                if len(pts) == 2 or fill is None:
                    out.append(path + (' S' if len(pts) == 2 else ' h S'))
                else:
                    out.append(f'{fill:.2f} g {path} h B')
            else:
                _, x, y, s, size, anchor = op
                width = text_width(s, size)
                x -= {'start': 0, 'middle': width/2, 'end': width}[anchor]
                s = s.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')
                out.append(f'0 g BT /F1 {size*k:.2f} Tf {x*k:.2f} {y*k:.2f} Td ({s}) Tj ET')
        return '\n'.join(out).encode('latin-1')

    def svg(self):
        """The page as an SVG document, for a quick look in a browser."""
        grey = lambda g: '#%02x%02x%02x' % ((int(g*255),)*3)
        out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}mm" height="{self.h}mm" '
               f'viewBox="0 0 {self.w} {self.h}"><rect width="100%" height="100%" fill="white"/>']
        for op in self.ops:
            if op[0] == 'poly':
                _, pts, fill, lw, dash, stroke = op
                paint = 'none' if fill is None or len(pts) == 2 else grey(fill)
                d = ' '.join(f'{x:.2f},{self.h-y:.2f}' for x, y in pts)
                tag = 'polyline' if len(pts) == 2 else 'polygon'
                dashes = ' stroke-dasharray="2 1.5"' if dash else ''      # no backslash in the f-string: Blender's Python is 3.11
                out.append(f'<{tag} points="{d}" fill="{paint}" stroke="{grey(stroke)}" stroke-width="{lw}" '
                           f'stroke-linejoin="round" stroke-linecap="round"{dashes}/>')
            else:
                _, x, y, s, size, anchor = op
                out.append(f'<text x="{x:.2f}" y="{self.h-y:.2f}" font-family="Helvetica,Arial" '
                           f'font-size="{size}" text-anchor="{anchor}">{s}</text>')
        return '\n'.join(out+['</svg>'])


def write_pdf(path, sheets):
    """Write the sheets as the pages of one PDF 1.4 file."""
    objects = [None, None, b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>']
    kids = []
    for sheet in sheets:
        stream = zlib.compress(sheet.pdf_stream())
        objects.append(b'<< /Length %d /Filter /FlateDecode >>\nstream\n' % len(stream) + stream + b'\nendstream')
        objects.append(b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 %.2f %.2f] /Contents %d 0 R '
                       b'/Resources << /Font << /F1 3 0 R >> >> >>' % (sheet.w*72/25.4, sheet.h*72/25.4, len(objects)))
        kids.append(len(objects))
    objects[0] = b'<< /Type /Catalog /Pages 2 0 R >>'
    objects[1] = b'<< /Type /Pages /Count %d /Kids [%s] >>' % (len(kids), b' '.join(b'%d 0 R' % k for k in kids))
    body, offsets = b'%PDF-1.4\n', []
    for i, obj in enumerate(objects):
        offsets.append(len(body))
        body += b'%d 0 obj\n' % (i+1) + obj + b'\nendobj\n'
    xref = len(body)
    body += b'xref\n0 %d\n0000000000 65535 f \n' % (len(objects)+1)
    body += b''.join(b'%010d 00000 n \n' % o for o in offsets)
    body += b'trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n' % (len(objects)+1, xref)
    with open(path, 'wb') as f:
        f.write(body)
