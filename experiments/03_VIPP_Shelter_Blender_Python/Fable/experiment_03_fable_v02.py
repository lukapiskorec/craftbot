# ------------------------------------------------------------------
# CRAFT BOT - Experiment 03 (Fable run) - VIPP Shelter, timber frame
# ------------------------------------------------------------------
# Two-storey prefabricated living unit: 11.5 x 5.2 m ground floor on
# steel stilts, fully glazed long sides, solid bathroom end wall, ring
# beam carrying a flat roof with two 5.0 x 2.5 m loft boxes on the
# back (+Y) side: box 1 = loft bed (floor + ladder hatch), box 2 = open
# light well over the kitchen.  All members are axis-aligned boxes made
# with craftbot.place_element and sorted into collections.
#
# Coordinates: X = length (0..11.5), Y = width (0..5.2, boxes at +Y),
# Z up, ground at z = 0.  Units: metres.

import bpy
import importlib
import craftbot_lib as craftbot

importlib.reload(craftbot)

# ------------------------------------------------------------------
# PARAMETERS

L, W = 11.5, 5.2                  # ground floor outer dimensions
PLY = 0.018                       # plywood sheathing / deck thickness
SHEET_W, SHEET_L = 1.22, 2.44     # plywood sheet size
GLASS = 0.020

POST_H = 0.60                     # steel stilt height (ground to girder)
GIRDER_D, GIRDER_W = 0.25, 0.10   # longitudinal bearers (doubled 50x250)
JOIST_D, JOIST_W = 0.20, 0.05     # floor joists 50x200 @ 600
SPACING = 0.60

Z_GIRDER = POST_H
Z_JOIST = Z_GIRDER + GIRDER_D
Z_SUBFLOOR = Z_JOIST + JOIST_D
FFL = Z_SUBFLOOR + PLY            # finished floor level (top of subfloor)

PLATE = 0.05                      # plate / stud thickness
STUD_D = 0.15                     # ground floor stud depth
POST = 0.15                       # glazing mullion posts 150x150
RING_D = 0.30                     # ring beam 150 x 300
Z_SILL_TOP = FFL + PLATE
Z_RING_BOT = Z_SILL_TOP + 2.45    # stud / post top
Z_RING_TOP = Z_RING_BOT + RING_D
ROOF_JOIST_D = 0.25               # roof / loft floor joists 50x250
Z_ROOF_JOIST_TOP = Z_RING_TOP + ROOF_JOIST_D
Z_ROOF_DECK = Z_ROOF_JOIST_TOP + PLY   # top of roof deck = loft floor

BOX_STUD_D = 0.10                 # loft box studs 50x100
BOX_H = 2.05                      # box height above roof deck (to top of rim)
BOX_RIM_D = 0.15                  # box roof rim joists 50x150
Z_BOX_TOP = Z_ROOF_DECK + BOX_H
Z_BOX_RIM_BOT = Z_BOX_TOP - BOX_RIM_D

BOX_Y0 = 2.70                     # boxes occupy y = 2.7 .. 5.2
BOX1_X = (0.50, 5.50)             # loft bed box
BOX2_X = (6.00, 11.00)            # light well box

INT_STUD_D = 0.10                 # interior partitions 50x100
Z_INT_TOP = Z_RING_TOP            # partitions run up to the roof joists

# ------------------------------------------------------------------
# HELPERS


def get_collection(path):
    """Return (creating if needed) a nested collection 'A/B/C'."""
    parent = bpy.context.scene.collection
    for name in path.split("/"):
        child = parent.children.get(name)
        if child is None:
            child = bpy.data.collections.get(name)
            if child is None:
                child = bpy.data.collections.new(name)
            parent.children.link(child)
        parent = child
    return parent


def box(name, coll, x0, x1, y0, y1, z0, z1):
    """Axis-aligned box from min/max corners, moved into collection."""
    obj = craftbot.place_element(
        name=name,
        loc=((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2),
        axis=(0, 0, 1),
        angle=0,
        scale=((x1 - x0) / 2, (y1 - y0) / 2, (z1 - z0) / 2),
    )
    for c in obj.users_collection:
        c.objects.unlink(obj)
    get_collection(coll).objects.link(obj)
    return obj


def positions(start, end, spacing, thick):
    """Member centre positions from start to end (first and last flush with
    the ends), intermediate ones on the spacing grid; a grid member closer
    than half a spacing to the last one is dropped."""
    first, last = start + thick / 2, end - thick / 2
    pos = [first]
    p = start + spacing
    while p < last - spacing / 2:
        pos.append(p)
        p += spacing
    pos.append(last)
    return pos


def tile_sheets(prefix, coll, x0, x1, y0, y1, z0, z1):
    """Cover a horizontal rectangle with plywood sheets (long side along X,
    rows staggered by half a sheet), clipping the last sheet of each row."""
    n = 0
    row = 0
    y = y0
    while y < y1 - 1e-6:
        yy = min(y + SHEET_W, y1)
        x = x0
        first_len = SHEET_L if row % 2 == 0 else SHEET_L / 2
        while x < x1 - 1e-6:
            xx = min(x + (first_len if x == x0 else SHEET_L), x1)
            box(f"{prefix}_{n:03d}", coll, x, xx, y, yy, z0, z1)
            n += 1
            x = xx
        y = yy
        row += 1


def tile_wall_x(prefix, coll, x0, x1, y0, y1, z0, z1):
    """Vertical sheets on a wall running along X (sheets stood upright,
    1.22 wide, full height)."""
    n = 0
    x = x0
    while x < x1 - 1e-6:
        xx = min(x + SHEET_W, x1)
        box(f"{prefix}_{n:02d}", coll, x, xx, y0, y1, z0, z1)
        n += 1
        x = xx


def tile_wall_y(prefix, coll, x0, x1, y0, y1, z0, z1):
    """Vertical sheets on a wall running along Y."""
    n = 0
    y = y0
    while y < y1 - 1e-6:
        yy = min(y + SHEET_W, y1)
        box(f"{prefix}_{n:02d}", coll, x0, x1, y, yy, z0, z1)
        n += 1
        y = yy


def stud_wall(prefix, coll, along, a0, a1, b0, b1, z_sole, z_top, openings=(), noggins=True):
    """Stud wall with sole plate, studs @600, double top plate and a row of
    mid-height noggins.  along = 'x' or 'y' is the wall direction; a0..a1 its
    extent along that axis, b0..b1 its thickness across.
    openings = [(aa, ab, z_sill, z_head)]: framed with jack + king studs and a
    150 mm header; z_sill > sole plate gives a window (sill + cripples below),
    z_sill = None gives a door."""

    def rect(name, p0, p1, z0, z1):
        if along == "x":
            box(name, coll, p0, p1, b0, b1, z0, z1)
        else:
            box(name, coll, b0, b1, p0, p1, z0, z1)

    rect(f"{prefix}_Sole", a0, a1, z_sole, z_sole + PLATE)
    rect(f"{prefix}_Top1", a0, a1, z_top - 2 * PLATE, z_top - PLATE)
    rect(f"{prefix}_Top2", a0, a1, z_top - PLATE, z_top)
    z0, z1 = z_sole + PLATE, z_top - 2 * PLATE
    verticals = []          # (p0, p1) of full-height members, for the noggins
    for i, c in enumerate(positions(a0, a1, SPACING, PLATE)):
        if any(aa - 2 * PLATE - PLATE / 2 < c < ab + 2 * PLATE + PLATE / 2 for aa, ab, _, _ in openings):
            continue
        rect(f"{prefix}_Stud_{i:02d}", c - PLATE / 2, c + PLATE / 2, z0, z1)
        verticals.append((c - PLATE / 2, c + PLATE / 2))
    for k, (aa, ab, zs, zh) in enumerate(openings):
        zj = z0 if zs is None else zs
        rect(f"{prefix}_Op{k}_JackL", aa - PLATE, aa, z0, zh)
        rect(f"{prefix}_Op{k}_KingL", aa - 2 * PLATE, aa - PLATE, z0, z1)
        rect(f"{prefix}_Op{k}_JackR", ab, ab + PLATE, z0, zh)
        rect(f"{prefix}_Op{k}_KingR", ab + PLATE, ab + 2 * PLATE, z0, z1)
        rect(f"{prefix}_Op{k}_Header", aa - PLATE, ab + PLATE, zh, zh + 0.15)
        verticals += [(aa - 2 * PLATE, aa - PLATE), (ab + PLATE, ab + 2 * PLATE)]
        for j, c in enumerate(positions(aa - PLATE, ab + PLATE, SPACING, PLATE)[1:-1]):
            rect(f"{prefix}_Op{k}_Cripple_{j}", c - PLATE / 2, c + PLATE / 2, zh + 0.15, z1)
        if zs is not None:
            rect(f"{prefix}_Op{k}_Sill", aa, ab, zs - PLATE, zs)
            for j, c in enumerate(positions(aa, ab, SPACING, PLATE)[1:-1]):
                rect(f"{prefix}_Op{k}_SillCripple_{j}", c - PLATE / 2, c + PLATE / 2, z0, zs - PLATE)
    if noggins:
        zc = (z0 + z1) / 2
        verticals.sort()
        for i in range(len(verticals) - 1):
            pa, pb = verticals[i][1], verticals[i + 1][0]
            if pb - pa < 0.05:
                continue
            if any(aa - 2 * PLATE <= pa and pb <= ab + 2 * PLATE for aa, ab, _, _ in openings):
                continue   # bay is the opening itself
            rect(f"{prefix}_Nog_{i:02d}", pa, pb, zc - PLATE / 2, zc + PLATE / 2)


def clad_x(prefix, coll, x0, x1, y0, y1, z0, z1, holes=()):
    """Vertical sheathing on a wall along X with rectangular holes
    [(xa, xb, za, zb)]: the wall is split into left / right / below / above
    rectangles around each hole (holes are assumed not to overlap in X)."""
    xs = sorted({x0, x1} | {v for xa, xb, _, _ in holes for v in (xa, xb)})
    n = 0
    for i in range(len(xs) - 1):
        xa, xb = xs[i], xs[i + 1]
        hole = next(((za, zb) for ha, hb, za, zb in holes if ha <= xa and xb <= hb), None)
        if hole is None:
            tile_wall_x(f"{prefix}_{n}", coll, xa, xb, y0, y1, z0, z1)
            n += 1
        else:
            za, zb = hole
            box(f"{prefix}_{n}_below", coll, xa, xb, y0, y1, z0, za)
            box(f"{prefix}_{n}_above", coll, xa, xb, y0, y1, zb, z1)
            n += 1


# ------------------------------------------------------------------
# 1. FOUNDATION: steel stilts under two longitudinal girders

C_FOUND = "Structure/Foundation"
GIRDER_Y = (0.60, W - 0.60)
STILT = 0.15
for i, x in enumerate((0.75, 3.25, 5.75, 8.25, 10.75)):
    for j, y in enumerate(GIRDER_Y):
        box(f"Stilt_{i}{j}", C_FOUND, x - STILT / 2, x + STILT / 2, y - STILT / 2, y + STILT / 2, 0.0, POST_H)

# ------------------------------------------------------------------
# 2. FLOOR PLATFORM: girders, joists @600 across Y, header joists, subfloor

C_FLOOR = "Structure/Floor_Framing"
for j, y in enumerate(GIRDER_Y):
    box(f"Girder_{j}", C_FLOOR, 0.0, L, y - GIRDER_W / 2, y + GIRDER_W / 2, Z_GIRDER, Z_JOIST)
for i, xc in enumerate(positions(0.0, L, SPACING, JOIST_W)):
    box(f"Floor_Joist_{i:02d}", C_FLOOR, xc - JOIST_W / 2, xc + JOIST_W / 2, JOIST_W, W - JOIST_W, Z_JOIST, Z_SUBFLOOR)
box("Floor_Header_S", C_FLOOR, 0.0, L, 0.0, JOIST_W, Z_JOIST, Z_SUBFLOOR)
box("Floor_Header_N", C_FLOOR, 0.0, L, W - JOIST_W, W, Z_JOIST, Z_SUBFLOOR)
tile_sheets("Subfloor", "Floors/Ground_Subfloor", 0.0, L, 0.0, W, Z_SUBFLOOR, FFL)

# ------------------------------------------------------------------
# 3. GROUND FLOOR WALLS
#    - sill plate 50x150 all round on the subfloor
#    - solid end wall at x=0 (bathroom end): studs 50x150 @600 + noggins
#    - glazed long sides and far end: 150x150 posts, glass between
#    - ring beam 150x300 on top all round

C_WALL = "Structure/Ground_Walls"
box("Sill_S", C_WALL, 0.0, L, 0.0, STUD_D, FFL, Z_SILL_TOP)
box("Sill_N", C_WALL, 0.0, L, W - STUD_D, W, FFL, Z_SILL_TOP)
box("Sill_W", C_WALL, 0.0, STUD_D, STUD_D, W - STUD_D, FFL, Z_SILL_TOP)
box("Sill_E", C_WALL, L - STUD_D, L, STUD_D, W - STUD_D, FFL, Z_SILL_TOP)

for name, (x0, y0) in {"SW": (0.0, 0.0), "NW": (0.0, W - POST),
                       "SE": (L - POST, 0.0), "NE": (L - POST, W - POST)}.items():
    box(f"Corner_Post_{name}", C_WALL, x0, x0 + POST, y0, y0 + POST, Z_SILL_TOP, Z_RING_BOT)

y_studs = positions(POST, W - POST, SPACING, PLATE)[1:-1]
for i, yc in enumerate(y_studs):
    box(f"End_Wall_Stud_{i:02d}", C_WALL, 0.0, STUD_D, yc - PLATE / 2, yc + PLATE / 2, Z_SILL_TOP, Z_RING_BOT)
y_edges = [POST] + [(yc - PLATE / 2, yc + PLATE / 2) for yc in y_studs] + [W - POST]
bays = []
prev = POST
for item in y_edges[1:]:
    if isinstance(item, tuple):
        bays.append((prev, item[0]))
        prev = item[1]
    else:
        bays.append((prev, item))
zc = (Z_SILL_TOP + Z_RING_BOT) / 2
for i, (ya, yb) in enumerate(bays):
    box(f"End_Wall_Nog_{i:02d}", C_WALL, 0.0, STUD_D, ya, yb, zc - PLATE / 2, zc + PLATE / 2)

MULLIONS_X = [L * k / 4 for k in (1, 2, 3)]
for i, xc in enumerate(MULLIONS_X):
    box(f"Mullion_S_{i}", C_WALL, xc - POST / 2, xc + POST / 2, 0.0, POST, Z_SILL_TOP, Z_RING_BOT)
    box(f"Mullion_N_{i}", C_WALL, xc - POST / 2, xc + POST / 2, W - POST, W, Z_SILL_TOP, Z_RING_BOT)
box("Mullion_E", C_WALL, L - POST, L, W / 2 - POST / 2, W / 2 + POST / 2, Z_SILL_TOP, Z_RING_BOT)

box("Ring_Beam_S", C_WALL, 0.0, L, 0.0, POST, Z_RING_BOT, Z_RING_TOP)
box("Ring_Beam_N", C_WALL, 0.0, L, W - POST, W, Z_RING_BOT, Z_RING_TOP)
box("Ring_Beam_W", C_WALL, 0.0, POST, POST, W - POST, Z_RING_BOT, Z_RING_TOP)
box("Ring_Beam_E", C_WALL, L - POST, L, POST, W - POST, Z_RING_BOT, Z_RING_TOP)

# ------------------------------------------------------------------
# 4. GLAZING: 20 mm panels centred in the post depth

C_GLASS = "Facade/Glazing"
x_breaks = [POST] + [v for xc in MULLIONS_X for v in (xc - POST / 2, xc + POST / 2)] + [L - POST]
gy = (POST - GLASS) / 2
for i in range(0, len(x_breaks), 2):
    xa, xb = x_breaks[i], x_breaks[i + 1]
    box(f"Glass_S_{i // 2}", C_GLASS, xa, xb, gy, gy + GLASS, Z_SILL_TOP, Z_RING_BOT)
    box(f"Glass_N_{i // 2}", C_GLASS, xa, xb, W - gy - GLASS, W - gy, Z_SILL_TOP, Z_RING_BOT)
for i, (ya, yb) in enumerate(((POST, W / 2 - POST / 2), (W / 2 + POST / 2, W - POST))):
    box(f"Glass_E_{i}", C_GLASS, L - gy - GLASS, L - gy, ya, yb, Z_SILL_TOP, Z_RING_BOT)

# ------------------------------------------------------------------
# 5. INTERIOR PARTITIONS (bathroom module, storage / fireplace wall)

C_INT = "Structure/Interior_Walls"
BATH_X, BATH_Y = 2.45, 2.85      # outer faces of the bathroom module
stud_wall("Bath_Wall_Y", C_INT, "y", STUD_D, BATH_Y + INT_STUD_D, BATH_X, BATH_X + INT_STUD_D, FFL, Z_INT_TOP)
stud_wall("Bath_Wall_X", C_INT, "x", STUD_D, BATH_X, BATH_Y, BATH_Y + INT_STUD_D, FFL, Z_INT_TOP,
          openings=[(0.40, 1.25, None, FFL + 2.10)])
STOR_X = 3.60
stud_wall("Storage_Wall_Y", C_INT, "y", STUD_D, BATH_Y + INT_STUD_D, STOR_X, STOR_X + INT_STUD_D, FFL, Z_INT_TOP)
stud_wall("Fireplace_Wall_X", C_INT, "x", STOR_X + INT_STUD_D, 4.50, 1.60, 1.60 + INT_STUD_D, FFL, Z_INT_TOP)

# ------------------------------------------------------------------
# 6. ROOF / LOFT FLOOR FRAMING: joists 50x250 @600 across Y on the ring
#    beam; doubled trimmer joists under the box side walls; light well
#    opening (box 2) with a doubled header; ladder hatch in the loft
#    floor (box 1) with headers between two joists

C_ROOF = "Structure/Roof_Framing"
RJ = JOIST_W
TRIMMERS = [BOX1_X[0], BOX1_X[1] - 2 * RJ, BOX2_X[0], BOX2_X[1] - 2 * RJ]   # x0 of doubled joists
for i, x0 in enumerate(TRIMMERS):
    box(f"Roof_Trimmer_{i}a", C_ROOF, x0, x0 + RJ, 0.0, W, Z_RING_TOP, Z_ROOF_JOIST_TOP)
    box(f"Roof_Trimmer_{i}b", C_ROOF, x0 + RJ, x0 + 2 * RJ, 0.0, W, Z_RING_TOP, Z_ROOF_JOIST_TOP)
HATCH_X = (3.025, 3.575)
HATCH_Y = (3.40, 4.60)
for i, xc in enumerate(positions(0.0, L, SPACING, RJ)):
    if any(x0 - RJ < xc < x0 + 3 * RJ for x0 in TRIMMERS):
        continue
    x0, x1 = xc - RJ / 2, xc + RJ / 2
    in_well = BOX2_X[0] + 2 * RJ < xc < BOX2_X[1] - 2 * RJ
    y1 = BOX_Y0 if in_well else W
    box(f"Roof_Joist_{i:02d}", C_ROOF, x0, x1, 0.0, y1, Z_RING_TOP, Z_ROOF_JOIST_TOP)
box("Well_Header_a", C_ROOF, BOX2_X[0] + 2 * RJ, BOX2_X[1] - 2 * RJ, BOX_Y0, BOX_Y0 + RJ, Z_RING_TOP, Z_ROOF_JOIST_TOP)
box("Well_Header_b", C_ROOF, BOX2_X[0] + 2 * RJ, BOX2_X[1] - 2 * RJ, BOX_Y0 + RJ, BOX_Y0 + 2 * RJ, Z_RING_TOP, Z_ROOF_JOIST_TOP)
box("Hatch_Header_S", C_ROOF, HATCH_X[0], HATCH_X[1], HATCH_Y[0] - RJ, HATCH_Y[0], Z_RING_TOP, Z_ROOF_JOIST_TOP)
box("Hatch_Header_N", C_ROOF, HATCH_X[0], HATCH_X[1], HATCH_Y[1], HATCH_Y[1] + RJ, Z_RING_TOP, Z_ROOF_JOIST_TOP)

C_RDECK = "Floors/Roof_Deck"
well_x0, well_x1 = BOX2_X[0] + BOX_STUD_D, BOX2_X[1] - BOX_STUD_D
well_y0, well_y1 = BOX_Y0 + BOX_STUD_D, W - BOX_STUD_D
deck_rects = [
    (0.0, L, 0.0, BOX_Y0),                                   # front strip
    (0.0, HATCH_X[0], BOX_Y0, W),                            # box 1 west of hatch
    (HATCH_X[0], HATCH_X[1], BOX_Y0, HATCH_Y[0]),
    (HATCH_X[0], HATCH_X[1], HATCH_Y[1], W),
    (HATCH_X[1], well_x0, BOX_Y0, W),                        # box 1 east of hatch + gap
    (well_x0, well_x1, BOX_Y0, well_y0),                     # under box 2 front wall
    (well_x0, well_x1, well_y1, W),                          # under box 2 back wall
    (well_x1, L, BOX_Y0, W),
]
for k, (x0, x1, y0, y1) in enumerate(deck_rects):
    tile_sheets(f"Roof_Deck_R{k}", C_RDECK, x0, x1, y0, y1, Z_ROOF_JOIST_TOP, Z_ROOF_DECK)

# ------------------------------------------------------------------
# 7. LOFT BOXES: stud walls 50x100 on the roof deck, rim joists on top,
#    glazed roof in three panes, plywood cladding on four sides

C_BOX = "Structure/Loft_Boxes"
C_SHE = "Facade/Sheathing"


def loft_box(prefix, x0, x1, windows=()):
    """windows = [(xa, xb, z_sill, z_head)] in the front (south) wall."""
    y0, y1 = BOX_Y0, W
    d = BOX_STUD_D
    stud_wall(f"{prefix}_Wall_W", C_BOX, "y", y0, y1, x0, x0 + d, Z_ROOF_DECK, Z_BOX_RIM_BOT)
    stud_wall(f"{prefix}_Wall_E", C_BOX, "y", y0, y1, x1 - d, x1, Z_ROOF_DECK, Z_BOX_RIM_BOT)
    stud_wall(f"{prefix}_Wall_S", C_BOX, "x", x0 + d, x1 - d, y0, y0 + d, Z_ROOF_DECK, Z_BOX_RIM_BOT,
              openings=windows)
    stud_wall(f"{prefix}_Wall_N", C_BOX, "x", x0 + d, x1 - d, y1 - d, y1, Z_ROOF_DECK, Z_BOX_RIM_BOT)
    box(f"{prefix}_Rim_W", C_BOX, x0, x0 + PLATE, y0, y1, Z_BOX_RIM_BOT, Z_BOX_TOP)
    box(f"{prefix}_Rim_E", C_BOX, x1 - PLATE, x1, y0, y1, Z_BOX_RIM_BOT, Z_BOX_TOP)
    box(f"{prefix}_Rim_S", C_BOX, x0 + PLATE, x1 - PLATE, y0, y0 + PLATE, Z_BOX_RIM_BOT, Z_BOX_TOP)
    box(f"{prefix}_Rim_N", C_BOX, x0 + PLATE, x1 - PLATE, y1 - PLATE, y1, Z_BOX_RIM_BOT, Z_BOX_TOP)
    xs = [x0 + PLATE]
    for k in (1, 2):
        xc = x0 + (x1 - x0) * k / 3
        box(f"{prefix}_Rim_Bearer_{k}", C_BOX, xc - PLATE / 2, xc + PLATE / 2, y0 + PLATE, y1 - PLATE, Z_BOX_RIM_BOT, Z_BOX_TOP)
        xs += [xc - PLATE / 2, xc + PLATE / 2]
    xs.append(x1 - PLATE)
    for k in range(3):
        box(f"{prefix}_Skylight_{k}", C_GLASS, xs[2 * k], xs[2 * k + 1], y0 + PLATE, y1 - PLATE,
            Z_BOX_TOP - 0.04 - GLASS, Z_BOX_TOP - 0.04)
    tile_wall_y(f"{prefix}_Clad_W", C_SHE, x0 - PLY, x0, y0 - PLY, y1 + PLY, Z_ROOF_DECK, Z_BOX_TOP)
    tile_wall_y(f"{prefix}_Clad_E", C_SHE, x1, x1 + PLY, y0 - PLY, y1 + PLY, Z_ROOF_DECK, Z_BOX_TOP)
    clad_x(f"{prefix}_Clad_S", C_SHE, x0, x1, y0 - PLY, y0, Z_ROOF_DECK, Z_BOX_TOP,
           holes=[(xa, xb, zs, zh) for xa, xb, zs, zh in windows])
    for k, (xa, xb, zs, zh) in enumerate(windows):
        box(f"{prefix}_Window_{k}", C_GLASS, xa, xb, y0 + d / 2 - GLASS / 2, y0 + d / 2 + GLASS / 2, zs, zh)
    tile_wall_x(f"{prefix}_Clad_N", C_SHE, x0, x1, y1, y1 + PLY, Z_ROOF_DECK, Z_BOX_TOP)


loft_box("Box1", *BOX1_X)
BOX2_WINDOW = (BOX2_X[1] - 1.95, BOX2_X[1] - 0.55, Z_ROOF_DECK + 1.05, Z_ROOF_DECK + 1.65)
loft_box("Box2", *BOX2_X, windows=[BOX2_WINDOW])

# ------------------------------------------------------------------
# 8. GROUND FLOOR EXTERIOR SHEATHING: solid end wall, floor and roof
#    fascia bands around the glazed sides

tile_wall_y("End_Wall_Clad", C_SHE, -PLY, 0.0, -PLY, W + PLY, POST_H, Z_ROOF_DECK)
for tag, (y0, y1) in {"S": (-PLY, 0.0), "N": (W, W + PLY)}.items():
    tile_wall_x(f"Floor_Band_{tag}", C_SHE, 0.0, L, y0, y1, POST_H, FFL)
    tile_wall_x(f"Roof_Band_{tag}", C_SHE, 0.0, L, y0, y1, Z_RING_BOT, Z_ROOF_DECK)
tile_wall_y("Floor_Band_E", C_SHE, L, L + PLY, -PLY, W + PLY, POST_H, FFL)
tile_wall_y("Roof_Band_E", C_SHE, L, L + PLY, -PLY, W + PLY, Z_RING_BOT, Z_ROOF_DECK)

print("VIPP shelter v02 generated:", len([o for o in bpy.data.objects if o.type == "MESH"]), "elements")
