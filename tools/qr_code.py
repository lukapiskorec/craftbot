"""Minimal QR code encoder: byte mode, error correction L, versions 1 to 5.

Up to 106 bytes in one Reed-Solomon block, which covers a viewer URL.
Standard library only.

    matrix = qr_matrix('https://...')     # list of rows, True = dark module

Checked against the published Reed-Solomon and format-string vectors (see
tests/test_fabrication_kit.py) and scanned from a printed sheet.

Provenance: experiment 16 fabrication set (viewer link in the title block).
"""

# version: (data codewords, error correction codewords)
CAPACITY = {1: (19, 7), 2: (34, 10), 3: (55, 15), 4: (80, 20), 5: (108, 26)}

EXP, LOG = [0]*512, [0]*256
_x = 1
for _i in range(255):
    EXP[_i], LOG[_x] = _x, _i
    _x <<= 1
    if _x & 0x100:
        _x ^= 0x11d
for _i in range(255, 512):
    EXP[_i] = EXP[_i-255]


def gf_mul(a, b):
    """Product in GF(256) with the QR polynomial 0x11d."""
    return 0 if a == 0 or b == 0 else EXP[LOG[a]+LOG[b]]


def reed_solomon(data, degree):
    """Error correction codewords: remainder of data(x) * x^degree by the generator."""
    generator, root = [0]*(degree-1)+[1], 1      # coefficients below the leading 1
    for _ in range(degree):
        for j in range(degree):
            generator[j] = gf_mul(generator[j], root)
            if j+1 < degree:
                generator[j] ^= generator[j+1]
        root = gf_mul(root, 2)
    remainder = [0]*degree
    for byte in data:
        factor = byte ^ remainder[0]
        remainder = remainder[1:]+[0]
        for i in range(degree):
            remainder[i] ^= gf_mul(generator[i], factor)
    return remainder


def codewords(text):
    """(version, data + error correction codewords) for `text`, in the smallest version that fits."""
    payload = text.encode('utf-8')
    version = next(v for v, (cap, _) in CAPACITY.items() if len(payload)+2 <= cap)
    capacity, ec = CAPACITY[version]
    bits = '0100' + format(len(payload), '08b') + ''.join(format(b, '08b') for b in payload)
    bits += '0'*min(4, capacity*8-len(bits))
    bits += '0'*(-len(bits) % 8)
    data = [int(bits[i:i+8], 2) for i in range(0, len(bits), 8)]
    data += [(0xEC, 0x11)[i % 2] for i in range(capacity-len(data))]
    return version, data+reed_solomon(data, ec)


MASKS = [lambda i, j: (i+j) % 2 == 0, lambda i, j: i % 2 == 0, lambda i, j: j % 3 == 0,
         lambda i, j: (i+j) % 3 == 0, lambda i, j: (i//2+j//3) % 2 == 0,
         lambda i, j: i*j % 2+i*j % 3 == 0, lambda i, j: (i*j % 2+i*j % 3) % 2 == 0,
         lambda i, j: ((i+j) % 2+i*j % 3) % 2 == 0]


def build(version, words, mask):
    """Module matrix for the codewords under one of the eight masks."""
    n = 17+4*version
    dark = [[False]*n for _ in range(n)]      # [row][col]
    fixed = [[False]*n for _ in range(n)]

    def put(row, col, value):
        if 0 <= row < n and 0 <= col < n:
            dark[row][col], fixed[row][col] = value, True

    for r0, c0 in ((3, 3), (3, n-4), (n-4, 3)):             # finders with separators
        for dr in range(-4, 5):
            for dc in range(-4, 5):
                put(r0+dr, c0+dc, max(abs(dr), abs(dc)) in (0, 1, 3))
    if version >= 2:                                         # one alignment pattern
        for dr in range(-2, 3):
            for dc in range(-2, 3):
                put(n-7+dr, n-7+dc, max(abs(dr), abs(dc)) != 1)
    for i in range(8, n-8):                                  # timing
        put(6, i, i % 2 == 0)
        put(i, 6, i % 2 == 0)

    fmt = (0b01 << 3) | mask                                 # level L
    rem = fmt
    for _ in range(10):
        rem = (rem << 1) ^ ((rem >> 9)*0x537)
    fmt = ((fmt << 10) | rem) ^ 0x5412
    bit = lambda i: (fmt >> i) & 1 == 1
    for i in range(6):
        put(i, 8, bit(i))
    put(7, 8, bit(6)); put(8, 8, bit(7)); put(8, 7, bit(8))
    for i in range(9, 15):
        put(8, 14-i, bit(i))
    for i in range(8):
        put(8, n-1-i, bit(i))
    for i in range(8, 15):
        put(n-15+i, 8, bit(i))
    put(n-8, 8, True)

    stream = [(w >> (7-k)) & 1 == 1 for w in words for k in range(8)]
    index, upward = 0, True
    col = n-1
    while col > 0:
        if col == 6:
            col -= 1
        for step in range(n):
            row = n-1-step if upward else step
            for c in (col, col-1):
                if not fixed[row][c]:
                    value = stream[index] if index < len(stream) else False
                    index += 1
                    dark[row][c] = value != MASKS[mask](row, c)
        upward = not upward
        col -= 2
    assert index >= len(stream)
    return dark


def penalty(m):
    """Mask penalty score of a matrix (runs, blocks, finder look-alikes, balance)."""
    n, score = len(m), 0
    lines = [row for row in m] + [[m[r][c] for r in range(n)] for c in range(n)]
    for line in lines:
        run = 1
        for a, b in zip(line, line[1:]+[None]):
            if a == b:
                run += 1
            else:
                if run >= 5:
                    score += run-2
                run = 1
        s = ''.join('1' if v else '0' for v in line)
        score += 40*(s.count('10111010000')+s.count('00001011101'))
    for r in range(n-1):
        for c in range(n-1):
            if m[r][c] == m[r][c+1] == m[r+1][c] == m[r+1][c+1]:
                score += 3
    share = sum(v for row in m for v in row)*100/(n*n)
    return score+10*int(abs(share-50)/5)


def qr_matrix(text):
    """QR matrix for `text` with the lowest-penalty mask."""
    version, words = codewords(text)
    return min((build(version, words, mask) for mask in range(8)), key=penalty)


if __name__ == '__main__':
    import sys
    for row in qr_matrix(sys.argv[1] if len(sys.argv) > 1 else 'https://lukapiskorec.github.io/craftbot/'):
        print(''.join('##' if v else '  ' for v in row))
