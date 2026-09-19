"""Title blocks (footers) for the fabrication sheets, selectable by key.

`FOOTERS` maps a key to a function `draw(sheet, block)` that draws the sheet
border, the note line and the title block along the bottom of a
`vector_pdf.Sheet` of any width. `block` is a `Block` with the texts of one
sheet. `drafting.SheetSet(..., footer='k')` picks one; `DEFAULT` is the
version chosen in the footer study, the others stay as references.

    a  the first layout, three lines of Arial left and right
    b  MEK-Mono for everything
    c  Bahnschrift, boxed number, inverted studio mark, three cells
    d  Inter, a small MEK-Mono label above every value
    e  Segoe UI Light, tall and airy, underlined title
    f  d with the number white on a black box, heavy 0-50-100 ticks
    g  Bahnschrift, number in a full-height black cell, block scale bar, ruled columns
    h  Arial, outlined number box, crossing ticks, right side as a list
    i  Inter, labels white on black tabs, fine 5 mm ticks
    j  Segoe UI, Segoe caps labels, heavy bar with hanging ticks, ruled columns
    k  DEFAULT: j without the rules, medium top line, large studio mark, h's bar with 0, 50, 100

`python tools/footer_study/footer_study.py` prints every footer as a strip
for comparison. The studio mark is always MEK-Mono (`viewer/fonts`); the
other faces are system fonts, so a sheet must be printed with
`vector_pdf.print_pdf` (headless Chrome), which embeds what it uses.

Provenance: footer study after the experiment 16 fabrication set.
"""
import struct
import datetime

from vector_pdf import THIN, MEDIUM, HEAVY, FONT_FILES

MARGIN = M = 10.0      # mm, sheet border
MEK, SANS, DIN, INTER, SEGOE = 'MEK-Mono', 'Arial', 'Bahnschrift', 'Inter', 'Segoe UI'
DEFAULT = 'k'
VIEWER = 'CraftBot online viewer'
UNITS = 'All numbers on this sheet are model mm.'


class Block:
    """The texts of one sheet's title block. `scale` is the model scale (15
    for 1:15), `scale_text` replaces the scale sentence (an axonometric at
    another scale), `qr` is a `qr_code.qr_matrix` or None."""

    def __init__(self, number, title, note, experiment, subtitle, scale, scale_text=None, studio='', qr=None, date=None):
        self.number, self.title, self.note = f'{number:02d}', title, note
        self.experiment, self.subtitle, self.studio, self.qr = experiment, subtitle, studio, qr
        self.date = date or datetime.date.today().isoformat()
        self.check = f'100 mm in 1:{scale} = {100*scale/1000:.1f} m in 1:1'
        self.scale_sentence = scale_text or f'Scale 1:{scale}, drawn 1:1 to the model.'
        self.scale_value = scale_text.rstrip('.') if scale_text else f'1:{scale}, drawn 1:1 to the model'
        self.set_line = f'{subtitle}. CraftBot fabrication set, {self.date}'


def mek_advance():
    """Advance width of MEK-Mono in em, read from the font's head and hmtx tables."""
    data = open(FONT_FILES[MEK], 'rb').read()
    tables = {data[12+16*i:16+16*i]: struct.unpack('>I', data[20+16*i:24+16*i])[0]
              for i in range(struct.unpack('>H', data[4:6])[0])}
    units = struct.unpack('>H', data[tables[b'head']+18:tables[b'head']+20])[0]
    return struct.unpack('>H', data[tables[b'hmtx']+4:tables[b'hmtx']+6])[0]/units     # glyph 1; glyph 0 is .notdef


def box(sheet, x, y, w, h, fill=0.0, lw=0.01):
    sheet.poly([(x, y), (x+w, y), (x+w, y+h), (x, y+h)], fill=fill, lw=lw)


def frame(sheet, title_h, lw, top_lw=None):
    """Sheet border and the line above the title block."""
    w, h = sheet.w, sheet.h
    sheet.poly([(M, M), (w-M, M), (w-M, h-M), (M, h-M)], fill=None, lw=lw)
    sheet.line((M, M+title_h), (w-M, M+title_h), top_lw or lw)


def qr(sheet, matrix, qx, qy, side):
    """QR code with its bottom-left corner at (qx, qy), dark modules merged into row runs."""
    n = len(matrix)
    cell = side/n
    for r, row in enumerate(matrix):
        c = 0
        while c < n:
            run = c
            while run < n and row[run]:
                run += 1
            if run > c:
                box(sheet, qx+c*cell, qy+side-(r+1)*cell, (run-c)*cell, cell)
            c = run+1


BARS = {   # check bar styles: base line width, then (every n mm, line width, mm above the base, mm below)
    'plain': (MEDIUM, [(10, MEDIUM, 1.8, 0), (50, MEDIUM, 3.0, 0)]),
    'thin': (THIN, [(10, THIN, 1.5, 0), (50, THIN, 3.0, 0)]),
    'weights': (THIN, [(10, THIN, 1.6, 0), (50, HEAVY, 3.2, 0)]),
    'cross': (THIN, [(10, THIN, 1.5, 0), (50, MEDIUM, 2.4, 2.4), (100, HEAVY, 2.4, 2.4)]),
    'fine': (THIN, [(5, THIN, 1.0, 0), (10, THIN, 2.0, 0), (50, THIN, 3.4, 0)]),
    'hang': (HEAVY, [(10, THIN, 0, 1.6), (50, THIN, 0, 3.0)]),
}


def bar(sheet, style, cx, by, font=SANS):
    """The 100 mm print check bar centred on cx with its base line at by, in one of the BARS styles.
    'blocks' is filled 10 mm segments and 'cross_numbers' the cross bar, both with 0, 50, 100 under them."""
    if style in ('blocks', 'cross_numbers'):
        for mm in (0, 50, 100):
            sheet.text(cx-50+mm, by-(3.2 if style == 'blocks' else 5.6), str(mm), 2.4, 'middle', font=font)
    if style == 'blocks':
        for i in range(10):
            box(sheet, cx-50+10*i, by, 10, 1.4, fill=float(i % 2), lw=THIN)
        return
    base, ticks = BARS['cross' if style == 'cross_numbers' else style]
    sheet.line((cx-50, by), (cx+50, by), base)
    for mm in range(0, 101, 5):
        step = [t for t in ticks if mm % t[0] == 0]
        if step:
            _, lw, up, down = step[-1]
            sheet.line((cx-50+mm, by-down), (cx-50+mm, by+up), lw)


def three_lines(s, b, font, h=30, rows=(20.5, 12, 4.5), sizes=(5, 3.8, 2.6, 3.0), title=None, weights=(400, 400, 400)):
    """The left and right columns of the unlabelled versions: three lines of text each, QR code far right."""
    w = s.w
    s.text(M+4, M+rows[0], title or f'{b.number}  {b.title}', sizes[0], font=font, weight=weights[0])
    s.text(M+4, M+rows[1], b.experiment, sizes[1], font=font, weight=weights[1])
    s.text(M+4, M+rows[2], b.set_line, sizes[2], font=font, weight=weights[2])
    if b.qr:
        qr(s, b.qr, w-M-27, M+3, 24)
        s.text(w-M-32, M+rows[0], '3D model in ' + VIEWER, sizes[3], 'end', font=font, weight=weights[2])
    s.text(w-M-32, M+rows[1], b.scale_sentence, max(sizes[3], sizes[1]-0.8), 'end', font=font, weight=weights[1])
    s.text(w-M-32, M+rows[2], UNITS, sizes[2], 'end', font=font, weight=weights[2])


def footer_a(s, b):
    """The first layout and sizes in Arial. Only the studio mark is MEK-Mono."""
    frame(s, 30, MEDIUM)
    s.text(M+4, M+33, b.note, 2.7)
    three_lines(s, b, SANS)
    s.text(s.w/2, M+20.5, b.check, 2.8, 'middle')
    bar(s, 'plain', s.w/2, M+14.5)
    s.text(s.w/2, M+5, b.studio, 3.6, 'middle', font=MEK)


def footer_b(s, b):
    """MEK-Mono for everything. Caps title with tracking, thin lines, three sizes."""
    frame(s, 30, THIN)
    s.text(M+4, M+33.5, b.note, 2.8, font=MEK)
    three_lines(s, b, MEK, sizes=(4.4, 3.4, 2.8, 2.8), title=f'{b.number}  {b.title.upper()}')
    s.text(s.w/2, M+21, b.check, 2.8, 'middle', font=MEK)
    bar(s, 'thin', s.w/2, M+15)
    s.text(s.w/2, M+5, b.studio, 4.4, 'middle', font=MEK)


def footer_c(s, b):
    """Bahnschrift in bold and light. Boxed sheet number, inverted studio mark, note in its own band, three cells."""
    w = s.w
    frame(s, 28, HEAVY)
    s.line((M, M+35), (w-M, M+35), THIN)                         # note band above the title block
    s.text(M+4, M+30.3, b.note, 2.8, font=DIN, weight=300)
    left, right = w/2-60, w/2+60
    s.line((left, M), (left, M+28), THIN)
    s.line((right, M), (right, M+28), THIN)
    box(s, M+4, M+10, 14, 14)
    s.text(M+11, M+14.2, b.number, 8, 'middle', font=DIN, weight=700, white=True)
    s.text(M+22, M+18.5, b.title, 6, font=DIN, weight=700)
    s.text(M+22, M+11, b.experiment, 3.6, font=DIN, weight=300)
    s.text(M+4, M+3.5, b.set_line, 2.6, font=DIN, weight=300)
    s.text(w/2, M+22.5, b.check, 2.6, 'middle', font=DIN, weight=300)
    bar(s, 'plain', w/2, M+16.5)
    box(s, left, M, 120, 9)
    s.text(w/2, M+3.1, b.studio, 4, 'middle', font=MEK, white=True)
    if b.qr:
        qr(s, b.qr, w-M-25, M+3, 22)
        s.text(w-M-30, M+3.5, '3D model in ' + VIEWER, 2.8, 'end', font=DIN, weight=300)
    s.text(w-M-30, M+18.5, b.scale_sentence, 3.6, 'end', font=DIN, weight=700)
    s.text(w-M-30, M+11, UNITS, 2.8, 'end', font=DIN, weight=300)


def footer_e(s, b):
    """Segoe UI Light, tall 38 mm block with more air. Large light title, underlined, italic small text."""
    w = s.w
    frame(s, 38, THIN)
    s.text(M+6, M+43, b.note, 3.2, font=SEGOE, weight=300, italic=True)
    s.text(M+6, M+25, b.number, 9, font=SEGOE, weight=700)
    s.text(M+22, M+25, b.title, 9, font=SEGOE, weight=300, underline=True)
    s.text(M+6, M+14, b.experiment, 3.8, font=SEGOE, weight=600)
    s.text(M+6, M+6, b.set_line, 2.8, font=SEGOE, weight=300, italic=True)
    s.text(w/2, M+29, b.check, 2.8, 'middle', font=SEGOE, weight=300, italic=True)
    bar(s, 'thin', w/2, M+22)
    s.text(w/2, M+8, b.studio, 5, 'middle', font=MEK)
    s.line((w/2-27, M+5.2), (w/2+27, M+5.2), HEAVY)
    if b.qr:
        qr(s, b.qr, w-M-33, M+5, 28)
        s.text(w-M-39, M+6, '3D model in ' + VIEWER, 2.8, 'end', font=SEGOE, weight=300, italic=True)
    s.text(w-M-39, M+25, b.scale_sentence, 3.8, 'end', font=SEGOE, weight=600)
    s.text(w-M-39, M+14, UNITS, 2.8, 'end', font=SEGOE, weight=300, italic=True)


def labelled(s, b, h, font, label_font=MEK, label_weight=400, label_size=2.2, tabs=False, number='box', bar_style='weights',
             right='grid', note='label', border=THIN, top=HEAVY, strong=600, light=400, title_size=4.6, studio_size=3.8,
             check_font=None):
    """The labelled title block, a small caps label above every value. `h` is its height, `number` the sheet
    number style (plain, box, outline, cell), `right` the layout of the right side (grid, ruled, columns, list),
    `tabs` sets the labels white on black, `check_font` overrides the font of the print check text."""
    w = s.w
    frame(s, h, border, top)
    label_y, low_y = M+h-4.4, M+3.5            # baselines: upper labels, lower values
    high_y, low_label_y = label_y-1.8-0.72*title_size, low_y+4.2

    def label(x, y, word, anchor='start'):
        if tabs:
            width = len(word)*(mek_advance()*label_size+0.3)+1.4
            box(s, x-(width if anchor == 'end' else 0), y-0.9, width, label_size+1.0)
            x += -0.85 if anchor == 'end' else 0.85
        s.text(x, y, word, label_size, anchor, font=label_font, weight=label_weight, spacing=0.3, white=tabs)

    def pair(x, word, value, upper=True, size=3.0, weight=None, anchor='start'):
        label(x, label_y if upper else low_label_y, word, anchor)
        s.text(x, high_y if upper else low_y, value, size, anchor, font=font, weight=weight or light)

    # Note line above the block.
    if note == 'band':
        s.line((M, M+h+7), (w-M, M+h+7), THIN)
    note_y = M+h+(2.4 if note == 'band' else 3.5)
    if b.note and note == 'italic':
        s.text(M+4, note_y, b.note, 2.8, font=font, weight=light, italic=True)
    elif b.note:
        label(M+4, note_y, 'NOTE')
        s.text(M+17, note_y, b.note, 2.8, font=font, weight=light)

    # Left: sheet number, then title over project and model.
    side = h if number == 'cell' else h-8
    x0 = M+(0 if number == 'cell' else 4)
    if number == 'plain':
        label(x0, label_y, 'SHEET')
        s.text(x0, label_y-1.8-0.72*7.5, b.number, 7.5, font=font, weight=700)
        x0 += 16
    else:
        y0 = M+(h-side)/2
        outline = number == 'outline'
        box(s, x0, y0, side, side, fill=1.0 if outline else 0.0, lw=HEAVY if outline else 0.01)
        s.text(x0+side/2, y0+side-3.6, 'SHEET', label_size, 'middle', font=label_font, weight=label_weight, spacing=0.3, white=not outline)
        s.text(x0+side/2, y0+side*0.16, b.number, side*0.5, 'middle', font=font, weight=700, white=not outline)
        x0 += side+5
    pair(x0, 'TITLE', b.title, size=title_size, weight=strong)
    pair(x0, 'PROJECT', b.experiment, upper=False)
    pair(x0+70, 'MODEL', b.subtitle, upper=False)

    # Middle: print check, then the studio mark.
    if check_font == MEK:
        s.text(w/2, label_y-0.4, b.check.upper(), 2.2, 'middle', font=MEK, spacing=0.3)
    else:
        s.text(w/2, label_y-0.4, b.check, 2.8, 'middle', font=font, weight=light)
    bar(s, bar_style, w/2, label_y-(5.0 if bar_style == 'hang' else 7.0 if bar_style == 'blocks' else 6.4), font)
    s.text(w/2, M+3.5, b.studio, studio_size, 'middle', font=MEK)

    # Right: QR code, then label and value pairs.
    qr_side = min(h-6, 24)
    qx = w-M-3-qr_side
    if b.qr:
        qr(s, b.qr, qx, M+(h-qr_side)/2, qr_side)
    items = {'3D MODEL': (VIEWER if b.qr else '', None), 'DATE': (b.date, None),
             'SCALE': (b.scale_value, strong), 'UNITS': ('model mm', None)}
    if right == 'list':                                  # one row per item, label left of its value
        rows = [word for word in ('SCALE', 'UNITS', '3D MODEL', 'DATE') if items[word][0]]
        pitch = (h-5)/4
        for i, word in enumerate(rows):
            y = M+h-2.2-pitch*(i+0.62)
            label(qx-56, y, word, 'end')
            s.text(qx-53, y, items[word][0], 3.2, font=font, weight=items[word][1] or light)
        return
    # Two columns. 'grid' is flush right, 'columns' flush left, 'ruled' flush left with a thin rule before each.
    anchor = 'end' if right == 'grid' else 'start'
    for x, upper, lower in ((qx-59 if right == 'grid' else qx-104, '3D MODEL', 'DATE'),
                            (qx-5 if right == 'grid' else qx-56, 'SCALE', 'UNITS')):
        if right == 'ruled':
            s.line((x-4, M), (x-4, M+h), THIN)
        if items[upper][0]:
            pair(x, upper, items[upper][0], size=3.4, weight=items[upper][1], anchor=anchor)
        pair(x, lower, items[lower][0], upper=False, anchor=anchor)
    if right == 'ruled':
        s.line((qx-4, M), (qx-4, M+h), THIN)


def footer_d(s, b):
    """Inter, compact 26 mm block. Small tracked caps labels in MEK-Mono above the values, check text in MEK-Mono too, italic note."""
    labelled(s, b, 26, INTER, number='plain', bar_style='thin', right='grid', note='italic', check_font=MEK)


def footer_f(s, b):
    """D refined, Inter, 28 mm. Number white on a black box as in C, check text in Inter, bar with heavy 0-50-100 ticks on a thin line. NOTE label."""
    labelled(s, b, 28, INTER, number='box', bar_style='weights', right='grid')


def footer_g(s, b):
    """Bahnschrift bold and light, 26 mm. Number in a black cell flush with the border, block scale bar with numerals, right side in ruled columns set flush left, note in a band."""
    labelled(s, b, 26, DIN, number='cell', bar_style='blocks', right='ruled', note='band', border=MEDIUM, strong=700, light=300, title_size=5)


def footer_h(s, b):
    """Arial, 30 mm. Outlined number box, bar with 0-50-100 ticks crossing the line and heavy ends, right side as a list with each label left of its value."""
    labelled(s, b, 30, SANS, number='outline', bar_style='cross', right='list', border=MEDIUM, top=MEDIUM, strong=700, title_size=5)


def footer_i(s, b):
    """Inter, 28 mm. Labels white on black tabs, plain large number, all-thin bar with 5 mm ticks in three heights, italic note without a label."""
    labelled(s, b, 28, INTER, tabs=True, number='plain', bar_style='fine', right='grid', note='italic')


def footer_j(s, b):
    """Segoe UI semibold and regular, 32 mm with more air. Labels in Segoe caps instead of MEK-Mono, boxed number, heavy bar with thin ticks hanging below, ruled right side."""
    labelled(s, b, 32, SEGOE, label_font=SEGOE, label_weight=600, label_size=2.0, number='box', bar_style='hang', right='ruled',
             title_size=5.4)


def footer_k(s, b):
    """The default. J with no vertical rules on the right, a medium top line, a larger studio mark, H's scale line with 0, 50, 100 under it."""
    labelled(s, b, 32, SEGOE, label_font=SEGOE, label_weight=600, label_size=2.0, number='box', bar_style='cross_numbers',
             right='columns', top=MEDIUM, title_size=5.4, studio_size=5.2)


FOOTERS = {name[-1]: fn for name, fn in sorted(globals().items()) if name.startswith('footer_')}
