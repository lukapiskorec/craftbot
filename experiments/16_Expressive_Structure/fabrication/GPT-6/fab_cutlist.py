# Cut list and stick order from members.json (written by fab_model.py),
# with tools/cutlist.py. Writes cutlist.csv and order.md here.
#
#   python fab_cutlist.py
import os
import sys
import json

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, '..', '..', '..', '..', 'tools')))
from cutlist import write_cutlist

PRICE = {'3x5': 0.40, '2x10': 0.50}   # EUR per stick, karapori.fi, 2026-09-18
URL = 'https://karapori.fi/products/mantyrima-3-x-3-mm'


def load():
    with open(os.path.join(HERE, 'members.json')) as f:
        return json.load(f)


if __name__ == '__main__':
    data = load()
    order = write_cutlist(data, HERE, title=f'Stick order, experiment 16 GPT-6 v02 at 1:{data["scale"]}',
                          intro=f'Mäntyrima 30 cm from {URL}. {len(data["members"])} pieces, frames {data["frames"]}.',
                          prices=PRICE, kerf=1.0, spare=0.10)
    print('Sticks to order:', order)
