"""Footer study: every title block of `title_blocks.FOOTERS` as a strip, for comparison.

Each strip is the bottom 80 mm of a real A2 sheet at 1:1, with the texts of
sheet 11 of the experiment 16 set, and the footer's key and description in
the margin below the border. The default footer is also drawn on a
landscape sheet.

    python tools/footer_study/footer_study.py      # writes pdf/ beside this file

Provenance: review of the experiment 16 fabrication set footer.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from vector_pdf import Sheet, A2, print_pdf     # noqa: E402
from title_blocks import FOOTERS, DEFAULT, Block, MARGIN     # noqa: E402
from qr_code import qr_matrix                   # noqa: E402

STRIP = 80.0      # mm of sheet shown
NOTE = ('Frame F0, glue-up template. Numbers: cut length in mm. Circles: stick profile and layer, '
        'L1 lies on the paper. Grey: the middle layer.')
QR = qr_matrix('https://lukapiskorec.github.io/craftbot/?model=models%2F16_Expressive_Structure%2Fgpt6_v02.json')


class Strip(Sheet):
    """A sheet that writes only its bottom STRIP mm."""

    def svg(self):
        full = f'width="{self.w}mm" height="{self.h}mm" viewBox="0 0 {self.w} {self.h}"'
        crop = f'width="{self.w}mm" height="{STRIP}mm" viewBox="0 {self.h-STRIP} {self.w} {STRIP}"'
        return Sheet.svg(self).replace(full, crop, 1)


def strip(key, paper):
    sheet = Strip(*paper)
    FOOTERS[key](sheet, Block(11, 'Frame F0 template', NOTE, 'Experiment 16 - Expressive Structure', 'GPT-6 v02, stick model',
                              15, studio='{protocell:labs}', qr=QR, date='2026-09-19'))
    sheet.text(MARGIN, 4, f'Version {key.upper()}. {FOOTERS[key].__doc__}', 2.4)      # review label, outside the border
    page = Sheet(sheet.w, STRIP)       # print_pdf sizes the page from w and h
    page.svg = sheet.svg
    return page


def main():
    strips = {key: strip(key, A2) for key in FOOTERS}
    strips[DEFAULT + '_landscape'] = strip(DEFAULT, A2[::-1])
    os.makedirs(os.path.join(HERE, 'pdf'), exist_ok=True)
    for key, page in strips.items():
        print_pdf(os.path.join(HERE, 'pdf', f'footer_{key}.pdf'), [page])
    stacked = Sheet(A2[0], STRIP*len(FOOTERS))       # all portrait strips on one page
    stacked.svg = lambda: ''.join(strips[key].svg() for key in FOOTERS)
    print_pdf(os.path.join(HERE, 'pdf', '00_all_versions.pdf'), [stacked])
    print('wrote', os.path.join(HERE, 'pdf'))


if __name__ == '__main__':
    main()
