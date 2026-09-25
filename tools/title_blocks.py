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
    k  j without the rules, medium top line, large studio mark, h's bar with 0, 50, 100
    l  k mirrored for binding, number box right, QR left, credits band underneath, 40 mm
    m  32 mm, credits as a list column between the bar and the title, one left column
    n  32 mm, three rows of pairs left, bar over fine print in the middle
    o  32 mm, credits listed under the bar, check sentence folded into SCALE
    p  32 mm, credits as run-in fine print under the left pairs
    q  32 mm, credits as run-in fine print under the title
    r  DEFAULT: 32 mm, M revised by Luka: two list columns after the QR code, 1 m real scale bar, title over project over studio

`HEIGHTS` gives the height of each block, which `drafting` keeps clear.
`python tools/footer_study/footer_study.py` prints every footer as a strip
for comparison. The studio mark is always MEK-Mono (`viewer/fonts`); the
other faces are system fonts, so a sheet must be printed with
`vector_pdf.print_pdf` (headless Chrome), which embeds what it uses.

Provenance: footer study after the experiment 16 fabrication set.
"""
import struct
import datetime

from vector_pdf import THIN, MEDIUM, HEAVY, FONT_FILES
from fonts import advance

MARGIN = M = 10.0      # mm, sheet border
MEK, SANS, DIN, INTER, SEGOE = 'MEK-Mono', 'Arial', 'Bahnschrift', 'Inter', 'Segoe UI'
DEFAULT = 'r'
VIEWER = 'CraftBot online viewer'
UNITS = 'All numbers on this sheet are model mm.'


class Block:
    """The texts of one sheet's title block. `scale` is the model scale (15
    for 1:15), `scale_text` replaces the scale sentence (an axonometric at
    another scale), `qr` is a `qr_code.qr_matrix` or None."""

    def __init__(self, number, title, note, experiment, subtitle, scale, scale_text=None, studio='', qr=None, date=None,
                 credits=()):
        self.number, self.title, self.note = f'{number:02d}', title, note
        self.experiment, self.subtitle, self.studio, self.qr = experiment, subtitle, studio, qr
        self.credits = list(credits)      # (LABEL, value) pairs of the set, for the band of footer l
        self.date = date or datetime.date.today().isoformat()
        self.check = f'100 mm in 1:{scale} = {100*scale/1000:.1f} m in 1:1'
        self.scale_num = scale
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


def footer_l(s, b):
    """K mirrored for binding in a folder: the sheet number and title on the right, the QR code on the left
    with the 3D MODEL label beside it, and under the block a two-line band of small print with the credits
    of the set (supervision, agents, workflow, disclaimer, source code), wrapped in the order given."""
    w, h, font = s.w, HEIGHTS['l'], SEGOE
    frame(s, h, THIN, MEDIUM)
    band = 11.0                                 # height of the small print under the block
    base = M+band
    label_y, low_y = M+h-4.2, base+3.0          # baselines: upper labels, lower values
    title_size = 5.4
    high_y, low_label_y = label_y-1.8-0.72*title_size, low_y+4.2

    def label(x, y, word, anchor='start'):
        s.text(x, y, word, 2.0, anchor, font=font, weight=600, spacing=0.3)

    def pair(x, word, value, upper=True, size=3.0, weight=400, anchor='start'):
        label(x, label_y if upper else low_label_y, word, anchor)
        s.text(x, high_y if upper else low_y, value, size, anchor, font=font, weight=weight)

    if b.note:      # wrapped onto a second line when it is too long for the sheet, the first line on top
        lines, words = [''], b.note.split()
        for word in words:
            if lines[-1] and advance(lines[-1]+' '+word, 2.8, font) > w-2*M-21:
                lines.append('')
            lines[-1] = (lines[-1]+' '+word).strip()
        label(M+4, M+h+3.5+3.6*(len(lines)-1), 'NOTE')
        for i, line in enumerate(lines):
            s.text(M+17, M+h+3.5+3.6*(len(lines)-1-i), line, 2.8, font=font)

    # Left: QR code, then the viewer and the date, then scale and units.
    side = 24.0
    y0 = base+(h-band-side)/2
    if b.qr:
        qr(s, b.qr, M+4, y0, side)
    pair(M+4+side+5, '3D MODEL', VIEWER if b.qr else '', size=3.4)
    pair(M+4+side+5, 'DATE', b.date, upper=False)
    pair(M+4+side+57, 'SCALE', b.scale_value, size=3.4, weight=600)
    pair(M+4+side+57, 'UNITS', 'model mm', upper=False)

    # Middle: print check, then the studio mark.
    s.text(w/2, label_y-0.4, b.check, 2.8, 'middle', font=font)
    bar(s, 'cross_numbers', w/2, label_y-6.4, font)
    s.text(w/2, low_y, b.studio, 5.2, 'middle', font=MEK)

    # Right: the sheet number in its black box, title and project flush against it.
    x1 = w-M-4-side
    box(s, x1, y0, side, side)
    s.text(x1+side/2, y0+side-3.6, 'SHEET', 2.0, 'middle', font=font, weight=600, spacing=0.3, white=True)
    s.text(x1+side/2, y0+side*0.16, b.number, side*0.5, 'middle', font=font, weight=700, white=True)
    pair(x1-5, 'TITLE', b.title, size=title_size, weight=600, anchor='end')
    pair(x1-5, 'PROJECT', b.experiment, upper=False, anchor='end')

    # The band: label and value pairs left to right, wrapped onto the second line when the first is full.
    x, lines, gap = M+4, [M+7.0, M+2.9], 7.0
    for word, value in b.credits:
        need = advance(word, 2.0, font, 600)+len(word)*0.3+2.0+advance(value, 2.4, font)
        if x+need > w-M-4 and lines and x > M+4:
            lines.pop(0)
            x = M+4
        if not lines:
            break
        label(x, lines[0], word)
        s.text(x+advance(word, 2.0, font, 600)+len(word)*0.3+2.0, lines[0], value, 2.4, font=font)
        x += need+gap


# ---- the 32 mm variants with the credits inside the block (m to q), sharing these pieces
QR_SIDE = 24.0
SIDE_TITLE = 5.4      # mm, the title at full size


def fitted(text, avail, size, font, weight=400, spacing=0.0, floor=3.0):
    """The largest size down to `floor` at which `text` fits `avail` mm."""
    while advance(text, size, font, weight)+len(text)*spacing > avail and size-0.2 >= floor:
        size -= 0.2
    return size


def label_text(s, x, y, word, size=2.0, anchor='start', font=SEGOE, white=False):
    s.text(x, y, word, size, anchor, font=font, weight=600, spacing=0.3, white=white)


def label_width(word, size=2.0, font=SEGOE):
    return advance(word, size, font, 600)+len(word)*0.3


def wrap(text, width, size, font=SEGOE, weight=400):
    """Lines of `text` no wider than `width`."""
    lines = ['']
    for word in text.split():
        trial = (lines[-1]+' '+word).strip()
        if lines[-1] and advance(trial, size, font, weight) > width:
            lines.append(word)
        else:
            lines[-1] = trial
    return lines


def run_in(s, x, top, width, size, items, font=SEGOE, pitch=None):
    """Fine print: LABEL value pairs flowed as one paragraph inside `width`, wrapping on words.
    Returns the last baseline."""
    pitch = pitch or 1.3*size
    y, cx = top-size, x
    space = advance(' ', size, font)

    def put(word, bold):
        nonlocal cx, y
        w = label_width(word, size*0.9, font) if bold else advance(word, size, font)
        if cx > x and cx+w > x+width:
            cx, y = x, y-pitch
        if bold:
            label_text(s, cx, y, word, size*0.9, font=font)
        else:
            s.text(cx, y, word, size, font=font)
        cx += w+space*(1.8 if bold else 1)
    for word, value in items:
        put(word, True)
        for token in value.split():
            put(token, False)
        cx += 2.5
    return y


def listing(s, x, top, width, size, items, font=SEGOE, pitch=None, label_w=None):
    """Fine print as a list: the label in its own column, the value wrapped beside it. Returns the last baseline."""
    if not items:
        return top
    pitch = pitch or 1.3*size
    label_w = label_w or max(label_width(word, size*0.9, font) for word, _ in items)+2.0
    y = top-size
    for word, value in items:
        label_text(s, x, y, word, size*0.9, font=font)
        for line in wrap(value, width-label_w, size, font):
            s.text(x+label_w, y, line, size, font=font)
            y -= pitch
    return y+pitch


def left_pairs(s, b, high_y, low_y, label_y, low_label_y, font=SEGOE, columns=2, size=3.4):
    """QR code, then [3D MODEL / DATE] and, with two columns, [SCALE / UNITS]. Returns the right edge."""
    x = M+4+QR_SIDE+5

    def pair(x, word, value, upper, size=3.0, weight=400):
        label_text(s, x, label_y if upper else low_label_y, word, font=font)
        s.text(x, high_y if upper else low_y, value, size, font=font, weight=weight)
    pair(x, '3D MODEL', VIEWER if b.qr else '', True, size)
    if columns == 2:
        pair(x, 'DATE', b.date, False)
        x2 = x+advance(VIEWER, size, font)+8
        pair(x2, 'SCALE', b.scale_value, True, size, 600)
        pair(x2, 'UNITS', 'model mm', False)
        return x2+advance(b.scale_value, size, font, 600)
    pair(x, 'SCALE', b.scale_value, False, 3.0, 600)
    return x+max(advance(VIEWER, size, font), advance(b.scale_value, 3.0, font, 600))


def bar_stack(s, b, cx, label_y, studio_y, font=SEGOE):
    """Check text over the bar over the studio mark, centred on cx."""
    s.text(cx, label_y-0.4, b.check, 2.8, 'middle', font=font)
    bar(s, 'cross_numbers', cx, label_y-6.4, font)
    s.text(cx, studio_y, b.studio, 5.2, 'middle', font=MEK)


def right_title(s, b, x_right, avail, high_y, low_y, label_y, low_label_y, font=SEGOE, project=True):
    """TITLE and PROJECT flush right at x_right, the title shrunk to fit `avail`. Returns the title size."""
    size = fitted(b.title, avail, SIDE_TITLE, font, 600)
    label_text(s, x_right, label_y, 'TITLE', anchor='end', font=font)
    s.text(x_right, high_y, b.title, size, 'end', font=font, weight=600)
    if project:
        label_text(s, x_right, low_label_y, 'PROJECT', anchor='end', font=font)
        s.text(x_right, low_y, b.experiment, fitted(b.experiment, avail, 3.0, font, floor=2.4), 'end', font=font)
    return size


def number_box(s, b, y0, font=SEGOE):
    """The sheet number white on black at the right edge. Returns its left edge."""
    x1 = s.w-M-4-QR_SIDE
    box(s, x1, y0, QR_SIDE, QR_SIDE)
    label_text(s, x1+QR_SIDE/2, y0+QR_SIDE-3.6, 'SHEET', anchor='middle', font=font, white=True)
    s.text(x1+QR_SIDE/2, y0+QR_SIDE*0.16, b.number, QR_SIDE*0.5, 'middle', font=font, weight=700, white=True)
    return x1


def note_line(s, b, h, font=SEGOE):
    """The note above the block, wrapped onto a second line when too long, the first line on top."""
    if not b.note:
        return
    lines = wrap(b.note, s.w-2*M-21, 2.8, font)
    label_text(s, M+4, M+h+3.5+3.6*(len(lines)-1), 'NOTE', font=font)
    for i, line in enumerate(lines):
        s.text(M+17, M+h+3.5+3.6*(len(lines)-1-i), line, 2.8, font=font)


def footer_m(s, b):
    """Credits as a list column. One left column (3D MODEL over SCALE), the bar, then DATE, UNITS and the
    credits as a small list with the label beside each value, and the title shrunk to what is left."""
    h, font = 32.0, SEGOE
    frame(s, h, THIN, MEDIUM)
    note_line(s, b, h)
    label_y, low_y = M+h-4.4, M+3.5
    high_y, low_label_y = label_y-1.8-0.72*SIDE_TITLE, low_y+4.2
    y0 = M+(h-QR_SIDE)/2
    if b.qr:
        qr(s, b.qr, M+4, y0, QR_SIDE)
    left = left_pairs(s, b, high_y, low_y, label_y, low_label_y, columns=1, size=3.0)
    cx = left+8+53
    bar_stack(s, b, cx, label_y, low_y)
    items = [('DATE', b.date), ('UNITS', 'model mm')]+b.credits
    lx, lw = cx+53+8, 96.0
    listing(s, lx, M+h-3.6, lw, 1.8, items, pitch=2.35)
    x1 = number_box(s, b, y0)
    right_title(s, b, x1-5, x1-5-(lx+lw+6), high_y, low_y, label_y, low_label_y)


def footer_n(s, b):
    """Three rows. Six labelled pairs left of the bar (3D MODEL, DATE, SUPERVISION; SCALE, UNITS, SOURCE CODE),
    the bar over three lines of fine print (AGENTS, WORKFLOW, DISCLAIMER) in the middle, the title,
    project and studio mark on the right."""
    h, font = 32.0, SEGOE
    frame(s, h, THIN, MEDIUM)
    note_line(s, b, h)
    rows = [M+25.2, M+16.0, M+6.8]      # value baselines; labels 3.4 above
    y0 = M+(h-QR_SIDE)/2
    if b.qr:
        qr(s, b.qr, M+4, y0, QR_SIDE)
    credit = dict(b.credits)
    cols = [[('3D MODEL', VIEWER if b.qr else '', 400), ('DATE', b.date, 400), ('SUPERVISION', credit.get('SUPERVISION', ''), 400)],
            [('SCALE', b.scale_value, 600), ('UNITS', 'model mm', 400), ('SOURCE CODE', credit.get('SOURCE CODE', ''), 400)]]
    x = M+4+QR_SIDE+5
    for col in cols:
        widest = 0
        for (word, value, weight), y in zip(col, rows):
            label_text(s, x, y+3.4, word, 1.8, font=font)
            s.text(x, y, value, 2.8, font=font, weight=weight)
            widest = max(widest, advance(value, 2.8, font, weight))
        x += widest+7
    cx = x+53
    s.text(cx, rows[0]+3.0, b.check, 2.6, 'middle', font=font)
    bar(s, 'cross_numbers', cx, rows[0]-2.8, font)
    fine = [(word, credit[word]) for word in ('AGENTS', 'WORKFLOW', 'DISCLAIMER') if word in credit]
    run_in(s, cx-50, rows[1]-2.6, 100, 1.7, fine, pitch=2.25)
    x1 = number_box(s, b, y0)
    right = x1-5
    avail = right-(cx+56)
    size = fitted(b.title, avail, SIDE_TITLE, font, 600)
    label_text(s, right, rows[0]+3.4, 'TITLE', 1.8, anchor='end', font=font)
    s.text(right, rows[0]-1.0, b.title, size, 'end', font=font, weight=600)
    label_text(s, right, rows[1]+1.0, 'PROJECT', 1.8, anchor='end', font=font)
    s.text(right, rows[1]-2.6, b.experiment, fitted(b.experiment, avail, 2.8, font, floor=2.2), 'end', font=font)
    s.text(right, rows[2]-0.5, b.studio, 4.2, 'end', font=MEK)


def footer_o(s, b):
    """Credits under the bar. Left and right as in k, the title at full size; the middle stacks the studio mark,
    the bar and a small list of the credits. The print check sentence moves into the SCALE value."""
    h, font = 32.0, SEGOE
    frame(s, h, THIN, MEDIUM)
    note_line(s, b, h)
    label_y, low_y = M+h-4.4, M+3.5
    high_y, low_label_y = label_y-1.8-0.72*SIDE_TITLE, low_y+4.2
    y0 = M+(h-QR_SIDE)/2
    if b.qr:
        qr(s, b.qr, M+4, y0, QR_SIDE)
    scale_value = b.scale_value+', '+b.check.split(' = ')[0]+' = '+b.check.split(' = ')[1].replace(' in 1:1', '')
    x = M+4+QR_SIDE+5
    label_text(s, x, label_y, '3D MODEL', font=font)
    s.text(x, high_y, VIEWER if b.qr else '', 3.2, font=font)
    label_text(s, x, low_label_y, 'DATE', font=font)
    s.text(x, low_y, b.date, 3.0, font=font)
    x2 = x+advance(VIEWER, 3.2, font)+8
    label_text(s, x2, label_y, 'SCALE', font=font)
    s.text(x2, high_y, scale_value, 2.8, font=font, weight=600)
    label_text(s, x2, low_label_y, 'UNITS', font=font)
    s.text(x2, low_y, 'model mm', 3.0, font=font)
    cx = x2+advance(scale_value, 2.8, font, 600)+10+50
    s.text(cx, M+h-6.0, b.studio, 3.8, 'middle', font=MEK)
    bar(s, 'cross_numbers', cx, M+h-9.6, font)
    listing(s, cx-50, M+h-16.4, 104, 1.7, b.credits, pitch=2.2)
    x1 = number_box(s, b, y0)
    right_title(s, b, x1-5, x1-5-(cx+56), high_y, low_y, label_y, low_label_y)


def footer_p(s, b):
    """Credits as fine print under the left pairs: the rows move up a little and four lines of run-in
    small print fill the left section beneath DATE and UNITS. Bar and title as in k."""
    h, font = 32.0, SEGOE
    frame(s, h, THIN, MEDIUM)
    note_line(s, b, h)
    label_y, low_y = M+29.3, M+15.6
    high_y, low_label_y = label_y-1.8-0.72*SIDE_TITLE, low_y+3.9
    y0 = M+(h-QR_SIDE)/2
    if b.qr:
        qr(s, b.qr, M+4, y0, QR_SIDE)
    left = left_pairs(s, b, high_y, low_y, label_y, low_label_y, size=3.2)
    cx = max(s.w/2, left+12+53)
    bar_stack(s, b, cx, label_y, M+5.5)
    run_in(s, M+4+QR_SIDE+5, M+12.6, cx-53-10-(M+4+QR_SIDE+5), 1.8, b.credits, pitch=2.3)
    x1 = number_box(s, b, y0)
    right_title(s, b, x1-5, x1-5-(cx+56), high_y, low_y, label_y, low_label_y)


def footer_q(s, b):
    """Credits as fine print under the title: everything about the project sits in the right section next
    to the sheet number. Left pairs and bar as in k, rows moved up a little."""
    h, font = 32.0, SEGOE
    frame(s, h, THIN, MEDIUM)
    note_line(s, b, h)
    label_y, low_y = M+29.3, M+15.6
    high_y, low_label_y = label_y-1.8-0.72*SIDE_TITLE, low_y+3.9
    y0 = M+(h-QR_SIDE)/2
    if b.qr:
        qr(s, b.qr, M+4, y0, QR_SIDE)
    left = left_pairs(s, b, high_y, low_y, label_y, low_label_y)
    cx = left+10+53
    bar_stack(s, b, cx, label_y, M+5.5)
    x1 = number_box(s, b, y0)
    lx = cx+56+8
    right_title(s, b, x1-5, x1-5-lx, high_y, low_y, label_y, low_label_y)
    run_in(s, lx, M+12.6, x1-5-lx, 1.7, b.credits, pitch=2.2)


def real_bar(s, x0, y, scale, font=SEGOE):
    """A print check bar of 1 m real on the line y: ticks every 10 cm standing on it, heavier at 0, 50
    and 100 cm, labelled in real centimetres above them. Returns its length on the sheet."""
    length = 1000/scale
    s.line((x0, y), (x0+length, y), THIN)
    for cm in range(0, 101, 10):
        x = x0+cm*length/100
        heavy = cm in (0, 100)
        s.line((x, y), (x, y+(2.4 if heavy or cm == 50 else 1.5)), HEAVY if heavy else MEDIUM if cm == 50 else THIN)
        if cm in (0, 50, 100):
            s.text(x, y+3.4, f'{cm}cm', 2.2, 'middle', font=font)
    return length


def spread(s, x, top, bottom, width, size, items, font=SEGOE, pitch=None):
    """`listing` spread evenly between `top` (the cap line of the first label) and `bottom` (the baseline
    of the last line): the lines of one item keep their pitch, the gaps between items share the rest."""
    if not items:
        return
    pitch = pitch or 1.3*size
    label_w = max(label_width(word, size*0.9, font) for word, _ in items)+2.0
    wrapped = [(word, wrap(value, width-label_w, size, font)) for word, value in items]
    y = top-0.72*size
    inner = sum((len(lines)-1)*pitch for _, lines in wrapped)
    gap = pitch if len(items) < 2 else (y-bottom-inner)/(len(items)-1)
    for word, lines in wrapped:
        label_text(s, x, y, word, size*0.9, font=font)
        for line in lines:
            s.text(x+label_w, y, line, size, font=font)
            y -= pitch
        y += pitch-gap


def footer_r(s, b):
    """M as Luka revised it: QR code, two list columns of the set's facts (DATE, SUPERVISION, AGENTS,
    WORKFLOW, DISCLAIMER, SOURCE CODE), the scale line under its SCALE value in real centimetres,
    title over project over the studio mark, and the sheet number."""
    h, font = 32.0, SEGOE
    frame(s, h, THIN, MEDIUM)
    note_line(s, b, h)
    y0 = M+(h-QR_SIDE)/2
    if b.qr:
        qr(s, b.qr, M+4, y0, QR_SIDE)
    # Two list columns, the items split where the line count balances.
    items = [('DATE', b.date)]+[c for c in b.credits if c[0] != 'SOURCE CODE']+[c for c in b.credits if c[0] == 'SOURCE CODE']
    col_w, size, pitch, top = 78.0, 2.4, 3.05, y0+QR_SIDE
    x = M+4+QR_SIDE+5
    lines = [len(wrap(value, col_w-label_width(word, size*0.9, font)-2.0, size, font)) for word, value in items]
    split, count = len(items), 0
    for i, n in enumerate(lines):
        count += n
        if count >= sum(lines)/2:
            split = i+1
            break
    for column in (items[:split], items[split:]):
        spread(s, x, top, y0, col_w, size, column, pitch=pitch)
        x += col_w+6
    # The scale: label and value at the top, the bar of 1 m real on the line of the QR code's bottom edge.
    label_text(s, x, top-0.72*size, 'SCALE', size*0.9, font=font)      # on the line of DATE and DISCLAIMER
    s.text(x, top-0.72*size-4.6, b.scale_value+', units mm', size, font=font)
    length = real_bar(s, x, y0, b.scale_num, font)
    x += max(length, advance(b.scale_value+', units mm', 2.4, font))+8
    # Title, project, studio mark, flush right against the number box.
    x1 = number_box(s, b, y0)
    right, avail = x1-5, x1-5-x
    # TITLE label's cap line on the box top, the studio mark's baseline on the box bottom, the rest spaced between.
    top_line, bottom_line = y0+QR_SIDE, y0
    label_text(s, right, top_line-0.72*1.8, 'TITLE', 1.8, anchor='end', font=font)
    s.text(right, top_line-7.2, b.title, fitted(b.title, avail, SIDE_TITLE, font, 600), 'end', font=font, weight=600)
    label_text(s, right, bottom_line+10.6, 'PROJECT', 1.8, anchor='end', font=font)
    s.text(right, bottom_line+6.4, b.experiment, fitted(b.experiment, avail, 2.8, font, floor=2.2), 'end', font=font)
    s.text(right, bottom_line+0.3, b.studio, 4.2, 'end', font=MEK)


FOOTERS = {name[-1]: fn for name, fn in sorted(globals().items()) if name.startswith('footer_')}
HEIGHTS = {'a': 30, 'b': 30, 'c': 28, 'd': 26, 'e': 38, 'f': 28, 'g': 26, 'h': 30, 'i': 28, 'j': 32, 'k': 32, 'l': 40,
           'm': 32, 'n': 32, 'o': 32, 'p': 32, 'q': 32, 'r': 32}      # mm
