"""Newsprint pages: markdown flowed into dense justified columns on a sheet.

For the text pages of a fabrication set, laid out like an old newspaper:
a masthead, then columns of small serif type with thin rules between them,
section heads centred over a rule, tables as run-in paragraphs, and a
figure that spans two columns at the foot of the column it is called in.

    blocks = parse(markdown)                       # headings, paragraphs, list items, table rows, figures
    pages = Newsprint(masthead, figures).flow(blocks, size)      # list of vector_pdf.Sheet
    size, pages = fit(Newsprint(...), blocks, max_pages=2)      # the largest type that fits

`masthead(sheet, page_number)` draws the head of each page and returns the
y where the columns start. `figures` maps a name used as `![name]` in the
markdown to `(caption, draw)` where `draw(sheet, left, top, width)` draws it
and returns its height. Text widths come from the real font file
(`fonts.advance`), and every justified line is also fitted to the column
width with the SVG `textLength`, so the columns print with even edges.

Markdown covered: `#` to `###` headings, paragraphs, `-` and `1.` items,
pipe tables, `**bold**`, `*italic*`, `` `code` `` (set plain), links (the
text only). Everything else is a paragraph.

Provenance: experiment 16 fabrication set, the front page.
"""
import re

from vector_pdf import Sheet, A2, FINE, THIN, HEAVY
from fonts import advance

FONT = 'Times New Roman'
INDENT = 3.0        # mm, first line of a paragraph
LEADING = 1.18      # line height over type size


# ------------------------------------------------------------ markdown
def inline(text):
    """Words of a run of markdown as (word, bold, italic); code and links are set plain."""
    text = re.sub(r'`([^`]*)`', r'\1', text)
    text = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', text)
    words, bold, italic = [], False, False
    for token in re.split(r'(\*\*|(?<![\w*])\*(?=\S)|(?<=\S)\*(?![\w*])|\s+)', text):
        if not token or token.isspace():
            continue
        if token == '**':
            bold = not bold
        elif token == '*':
            italic = not italic
        elif words and not any(ch.isalnum() for ch in token) and token[0] in '.,;:)!?]':
            words[-1] = (words[-1][0]+token,)+words[-1][1:]      # punctuation after a closing ** stays on its word
        elif words and not any(ch.isalnum() for ch in words[-1][0]) and words[-1][0][-1] in '([':
            words[-1] = (words[-1][0]+token, bold, italic)      # an opening bracket before an opening **
        else:
            words.append((token, bold, italic))
    return words


def parse(markdown):
    """Blocks of a markdown text: ('h1'|'h2'|'h3', words), ('p', words), ('item', words, marker),
    ('figure', name). A table becomes one paragraph per row, the first cell bold, the header row italic."""
    blocks, paragraph = [], []

    def flush():
        if paragraph:
            blocks.append(('p', inline(' '.join(paragraph))))
            paragraph.clear()

    table = None
    for raw in markdown.splitlines():
        line = raw.strip()
        if line.startswith('|'):
            cells = [c.strip() for c in line.strip('|').split('|')]
            if all(set(c) <= set('-: ') for c in cells):
                continue          # the rule under the header
            flush()
            if table is None:
                table = True
                blocks.append(('p', [(w, False, True) for w, _, _ in inline('. '.join(cells)+'.')]))
            else:
                head = [(w, True, i) for w, _, i in inline(cells[0]+'.')]
                rest = '. '.join(c.rstrip('.') for c in cells[1:] if c)
                blocks.append(('p', head+inline(rest+('.' if rest else ''))))
            continue
        table = None
        m = re.match(r'!\[([^\]]+)\]', line)
        if m:
            flush()
            blocks.append(('figure', m.group(1)))
        elif line.startswith('#'):
            flush()
            level = len(line)-len(line.lstrip('#'))
            blocks.append((f'h{min(level, 3)}', inline(line.lstrip('#').strip())))
        elif re.match(r'[-*]\s+', line) or re.match(r'\d+\.\s+', line):
            flush()
            marker = '-' if line[0] in '-*' else line.split('.')[0]+'.'
            blocks.append(('item', inline(re.sub(r'^([-*]|\d+\.)\s+', '', line)), marker))
        elif not line:
            flush()
        else:
            paragraph.append(line)
    flush()
    return blocks


# ------------------------------------------------------------ type
class Style:
    """Type size, weight and italic of one kind of block, with its space before and after in lines."""

    def __init__(self, size, weight=400, italic=False, before=0.0, after=0.0, centred=False, indent=INDENT):
        self.size, self.weight, self.italic = size, weight, italic
        self.before, self.after, self.centred, self.indent = before, after, centred, indent

    def width(self, text, bold=False, italic=False):
        return advance(text, self.size, FONT, 700 if bold or self.weight >= 600 else self.weight, italic or self.italic)


def styles(size):
    """Block styles for a body size in mm."""
    return {'p': Style(size), 'item': Style(size, indent=0.0),
            'h1': Style(size*1.5, 700, before=1.6, after=0.5, centred=True, indent=0.0),
            'h2': Style(size*1.2, 700, before=1.2, after=0.25, indent=0.0),
            'h3': Style(size, 700, italic=True, before=0.8, after=0.1, indent=0.0)}


def break_lines(words, style, width, first_indent):
    """Lines of (runs, justified) for words (word, bold, italic) in a column `width`; a run is
    (text, bold, italic, width, spaces). A word wider than the column is broken by characters."""
    space = style.width(' ')
    lines, line, used = [], [], first_indent
    for word, bold, italic in words:
        w = style.width(word, bold, italic)
        while w > width and len(word) > 1:      # a path or URL wider than the column
            cut = max(1, int(len(word)*(width-used-space)/w))
            head, word = word[:cut], word[cut:]
            line.append((head, bold, italic, style.width(head, bold, italic)))
            lines.append((line, True))
            line, used, w = [], 0.0, style.width(word, bold, italic)
        if line and used+space+w > width:
            lines.append((line, True))
            line, used = [], 0.0
        used += (space if line else 0)+w
        line.append((word, bold, italic, w))
    if line:
        lines.append((line, False))
    out = []
    for words_, justified in lines:
        runs, current = [], None
        for word, bold, italic, w in words_:
            if current and current[1:3] == [bold, italic]:
                current[0] += ' '+word
                current[4] += 1
            else:
                current = [word, bold, italic, 0.0, 0]
                runs.append(current)
        for run in runs:
            run[3] = style.width(run[0], run[1], run[2])
        out.append((runs, justified))
    return out


# ------------------------------------------------------------ pages
class Newsprint:
    """Columns on a sheet. `masthead(sheet, number)` draws the head of page `number` and returns the y
    where the columns start; `figures` maps a name to (caption, draw(sheet, left, top, width) -> height)."""

    def __init__(self, masthead, figures=None, paper=A2, margin=12.0, columns=4, gutter=5.0, foot=12.0):
        self.masthead, self.figures = masthead, figures or {}
        self.paper, self.margin, self.columns, self.gutter, self.foot = paper, margin, columns, gutter, foot
        self.width = (paper[0]-2*margin-(columns-1)*gutter)/columns

    def column_x(self, c):
        return self.margin+c*(self.width+self.gutter)

    def flow(self, blocks, size, cut=None):
        """Lay the blocks out at body `size`; stops after `cut` pages when given. Returns the sheets
        and the fraction of the last page's columns that is filled."""
        st = styles(size)
        pages, sheet, top, c, y, bottoms = [], None, 0.0, 0, 0.0, []

        def finish_page():
            """Rules between the columns, from the head down to the foot or to a figure spanning the gutter."""
            for k in range(1, self.columns):
                x = self.column_x(k)-self.gutter/2
                low = max(bottoms[k-1], bottoms[k])
                sheet.line((x, top), (x, low-size*LEADING*0.3 if low > self.foot else self.foot), FINE)
            pages.append(sheet)

        def new_page():
            nonlocal sheet, top, c, y, bottoms
            if sheet is not None:
                finish_page()
            sheet = Sheet(*self.paper)
            top = self.masthead(sheet, len(pages)+1)
            bottoms = [self.foot]*self.columns
            c, y = 0, top

        def next_column():
            nonlocal c, y
            c += 1
            y = top
            if c == self.columns:
                if cut and len(pages)+1 >= cut:
                    return False
                new_page()
            return True

        def room():
            return y-bottoms[c]

        new_page()
        stopped = False
        for block in blocks:
            if stopped:
                break
            kind = block[0]
            if kind == 'figure':
                # Two columns wide at the foot of the first column pair, from this column on, that has room
                # for it under three lines of text; otherwise at the foot of the next page's first pair.
                caption, draw = self.figures[block[1]]
                span, lh = 2*self.width+self.gutter, size*LEADING
                height = draw(Sheet(*self.paper), 0, 0, span)+2*lh+2      # figure, caption line, air
                while True:
                    fits = [k for k in range(c, self.columns-1)
                            if (y if k == c else top)-bottoms[k]-height >= 3*lh and bottoms[k+1] == self.foot]
                    if fits:
                        k = fits[0]
                        break
                    c = self.columns-1
                    if not next_column():
                        stopped = True
                        break
                if stopped:
                    break
                left, base = self.column_x(k), bottoms[k]
                fig_h = draw(sheet, left, base+height-lh, span)
                sheet.text(left+span/2, base+lh*0.3, caption, size, 'middle', font=FONT, italic=True)
                for j in (k, k+1):
                    bottoms[j] = base+height+lh*0.6
                    sheet.line((self.column_x(j), bottoms[j]-lh*0.3), (self.column_x(j)+self.width, bottoms[j]-lh*0.3), THIN)
                continue
            style = st[kind if kind in st else 'p']
            words = block[1]
            lines = break_lines(words, style, self.width-(4.0 if kind == 'item' else 0.0), style.indent)
            lh = style.size*LEADING
            need = lh*(min(len(lines), 2)+style.before)+(lh*2 if kind.startswith('h') else 0)      # keep a head with two lines
            if room() < need and not next_column():
                break
            y -= lh*style.before
            for i, (runs, justified) in enumerate(lines):
                if room() < lh:
                    if not next_column():
                        stopped = True
                        break
                x0 = self.column_x(c)+(4.0 if kind == 'item' else 0.0)
                width = self.width-(4.0 if kind == 'item' else 0.0)
                if i == 0 and kind == 'item':
                    sheet.text(self.column_x(c), y-lh*0.82, block[2] if block[2] != '-' else '–', style.size, font=FONT)
                indent = style.indent if i == 0 else 0.0
                self.line(sheet, runs, style, x0+indent, y-lh*0.82, width-indent, justified and not style.centred)
                y -= lh
            y -= lh*style.after
        if sheet is not None:
            finish_page()
        used = sum(top-bottoms[k] for k in range(c))+(top-y)
        fill = used/sum(top-b for b in bottoms)
        return pages, fill

    def line(self, sheet, runs, style, x, baseline, width, justified):
        """One line of runs at the baseline: justified by word spacing, centred, or ragged right."""
        space = style.width(' ')
        natural = sum(r[3] for r in runs)+space*(len(runs)-1)
        gaps = sum(r[4] for r in runs)+len(runs)-1
        ws = (width-natural)/gaps if justified and gaps and natural < width else 0.0
        if style.centred:
            x += (width-natural)/2
        for text, bold, italic, w, spaces in runs:
            fitted = w+spaces*ws
            sheet.text(x, baseline, text, style.size, font=FONT, weight=700 if bold or style.weight >= 600 else style.weight,
                       italic=italic or style.italic, width=fitted if ws else None, word_spacing=ws)
            x += fitted+space+ws


def fit(press, blocks, max_pages=2, sizes=None):
    """The largest body size (mm) at which the blocks fit `max_pages` pages, and those pages; when even the
    smallest size overflows, the text is cut after `max_pages` pages. Returns (size, pages, fill, cut)."""
    sizes = sizes or [3.6-0.02*i for i in range(81)]      # 3.6 down to 2.0
    for size in sizes:
        pages, fill = press.flow(blocks, size)
        if len(pages) <= max_pages:
            return size, pages, fill, False
    pages, fill = press.flow(blocks, sizes[-1], cut=max_pages)
    return sizes[-1], pages, fill, True
