# ------------------------------------------------------------------
# CRAFT BOT - EXPERIMENT 13 - FABLE - V02
# HIP ROOF WITH CLOSED-METHOD WOOD-BOARD SHEATHING
#
# Requires `craftbot_lib.py` and `experiment_11_chatgpt51_v18.py` on sys.path.
#
# Sheathing follows CMHC "Canadian Wood-Frame House Construction" Fig. 98,
# closed method: 19 x 184 mm boards laid edge to edge, running parallel to
# the eaves (at right angles to the rafters), every joint over a rafter,
# joints staggered row to row, boards trimmed tight at hips, valleys and
# ridges.
# ------------------------------------------------------------------

import bpy
import math
from mathutils import Vector, Matrix
import importlib

import craftbot_lib as craftbot
import experiment_11_chatgpt51_v18 as base

importlib.reload(craftbot)
importlib.reload(base)


# ---------------------------------------------------------------------------
# PARAMETERS
# ---------------------------------------------------------------------------

BOARD_WIDTH = 0.184      # 8 in. nominal (CMHC: <= 286 mm)
BOARD_THICK = 0.019      # 3/4 in. nominal
BOARD_LEN = 3.6          # nominal stock length between joints
MIN_BOARD = 0.5          # never cut a board shorter than this
STAGGER = 0.5 * BOARD_LEN
DROP_CLEARANCE = 0.002   # hip/valley top kept this far under the sheathing


# ---------------------------------------------------------------------------
# COLLECTIONS
# ---------------------------------------------------------------------------

def get_collection(name, parent=None):
    coll = bpy.data.collections.get(name)
    if coll is None:
        coll = bpy.data.collections.new(name)
        (parent or bpy.context.scene.collection).children.link(coll)
    return coll


def move_to_collection(obj, coll):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    coll.objects.link(obj)


def sort_framing_into_collections(frame_names, colls):
    for name in frame_names:
        obj = bpy.data.objects.get(name)
        if obj is None:
            continue
        if "_Dormer_" in name or name.startswith("DormerSupport"):
            move_to_collection(obj, colls["frame_dormers"])
        elif name.startswith("Wing_") or name.startswith("Valley_"):
            move_to_collection(obj, colls["frame_wing"])
        else:
            move_to_collection(obj, colls["frame_main"])


# ---------------------------------------------------------------------------
# PLANE GEOMETRY
# ---------------------------------------------------------------------------

class Facet:
    """
    One planar roof surface.

    O : a point on the rafter centre-plane (normally on the eave plate line)
    U : horizontal in-plane unit vector  -> board length direction
    V : up-slope in-plane unit vector    -> board width direction
    N : outward (upward) unit normal
    underside : distance from the centre-plane to the sheathing underside
                (= half the rafter depth, boards sit on the rafter tops)
    """

    def __init__(self, name, O, U, V, underside):
        self.name = name
        self.O = Vector(O)
        self.V = Vector(V).normalized()
        U = Vector(U).normalized()
        N = U.cross(self.V)
        if N.z < 0.0:
            U = -U
            N = -N
        self.U = U
        self.N = N.normalized()
        self.underside = underside
        self.top = underside + BOARD_THICK

    def plane(self, offset=0.0):
        """Plane parallel to the centre-plane, shifted by `offset` along N."""
        return (self.N.copy(), self.N.dot(self.O) + offset)

    def uv(self, P):
        d = Vector(P) - self.O
        return (d.dot(self.U), d.dot(self.V))

    def xyz(self, u, v, h):
        return self.O + u * self.U + v * self.V + h * self.N


def vplane(axis, value):
    """Vertical plane x = value ('x') or y = value ('y')."""
    n = Vector((1.0, 0.0, 0.0)) if axis == "x" else Vector((0.0, 1.0, 0.0))
    return (n, value)


def isect(p1, p2, p3):
    """Intersection point of three planes given as (normal, d) with n.P = d."""
    M = Matrix((p1[0], p2[0], p3[0]))
    return M.inverted() @ Vector((p1[1], p2[1], p3[1]))


# ---------------------------------------------------------------------------
# BOARD LAYOUT (2D, in facet u/v coordinates)
# ---------------------------------------------------------------------------

def scan_intervals(loops, v_s):
    """Even-odd intervals in u where the horizontal line v = v_s is inside."""
    us = []
    for loop in loops:
        n = len(loop)
        for i in range(n):
            u0, v0 = loop[i]
            u1, v1 = loop[(i + 1) % n]
            if (v0 <= v_s < v1) or (v1 <= v_s < v0):
                t = (v_s - v0) / (v1 - v0)
                us.append(u0 + t * (u1 - u0))
    us.sort()
    return [(us[i], us[i + 1]) for i in range(0, len(us) - 1, 2)]


def clip_poly_u(poly, c, keep_left):
    """Sutherland-Hodgman clip of a convex polygon against the line u = c."""
    out = []
    n = len(poly)
    for i in range(n):
        P = poly[i]
        Q = poly[(i + 1) % n]
        inP = (P[0] <= c) if keep_left else (P[0] >= c)
        inQ = (Q[0] <= c) if keep_left else (Q[0] >= c)
        if inP:
            out.append(P)
        if inP != inQ:
            t = (c - P[0]) / (Q[0] - P[0])
            out.append((c, P[1] + t * (Q[1] - P[1])))
    return out


def poly_area(poly):
    a = 0.0
    n = len(poly)
    for i in range(n):
        u0, v0 = poly[i]
        u1, v1 = poly[(i + 1) % n]
        a += u0 * v1 - u1 * v0
    return abs(a) * 0.5


def board_cuts(a, b, joints, row):
    """
    Joint positions (u) for a board run from a to b. Joints land on rafters
    (the `joints` list); odd rows start with a half-length board so joints
    stagger between neighbouring rows.
    """
    cuts = []
    pos = a
    allowed = BOARD_LEN if row % 2 == 0 else STAGGER
    while b - pos > allowed + 1e-6:
        cands = [j for j in joints if pos + MIN_BOARD <= j <= pos + allowed]
        if not cands:
            break
        c = max(cands)
        if b - c < MIN_BOARD:
            break
        cuts.append(c)
        pos = c
        allowed = BOARD_LEN
    return cuts


def split_piece(piece, joints, row):
    us = [p[0] for p in piece]
    cuts = board_cuts(min(us), max(us), joints, row)
    out = []
    rest = piece
    for c in cuts:
        out.append(clip_poly_u(rest, c, True))
        rest = clip_poly_u(rest, c, False)
    out.append(rest)
    return out


def make_board(name, facet, poly, coll):
    """Extrude a 2D board outline (facet u/v) into a board-thick solid."""
    n = len(poly)
    verts = [facet.xyz(u, v, facet.underside) for (u, v) in poly]
    verts += [facet.xyz(u, v, facet.top) for (u, v) in poly]
    faces = [tuple(reversed(range(n))), tuple(range(n, 2 * n))]
    for i in range(n):
        j = (i + 1) % n
        faces.append((i, j, n + j, n + i))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    coll.objects.link(obj)
    return obj


def sheathe_facet(facet, loops, joint_points, coll, prefix):
    """
    Cover the region described by `loops` (outer loop + hole loops, in facet
    u/v coordinates, even-odd rule) with rows of boards starting at the eave.
    """
    joints = sorted(set(round(facet.uv(p)[0], 4) for p in joint_points))
    vmin = min(v for loop in loops for (_, v) in loop)
    vmax = max(v for loop in loops for (_, v) in loop)

    idx = 0
    row = 0
    v0 = vmin
    while v0 < vmax - 1e-4:
        v1 = min(v0 + BOARD_WIDTH, vmax)
        if vmax - v1 < 0.04:          # rip the last board instead of a sliver
            v1 = vmax
        lo = scan_intervals(loops, v0 + 1e-4)
        hi = scan_intervals(loops, v1 - 1e-4)
        if len(lo) == len(hi):
            pieces = [[(a0, v0), (b0, v0), (b1, v1), (a1, v1)]
                      for (a0, b0), (a1, b1) in zip(lo, hi)]
        else:
            # a polygon vertex lies inside this row: fall back to square ends
            mid = scan_intervals(loops, 0.5 * (v0 + v1))
            pieces = [[(a, v0), (b, v0), (b, v1), (a, v1)] for (a, b) in mid]
        for piece in pieces:
            for board in split_piece(piece, joints, row):
                if len(board) < 3 or poly_area(board) < 1e-4:
                    continue
                make_board(f"{prefix}_{idx:03d}", facet, board, coll)
                idx += 1
        row += 1
        v0 = v1
    return idx


# ---------------------------------------------------------------------------
# FRAME CORRECTIONS
# ---------------------------------------------------------------------------

def drop_member(name, facets):
    """
    Lower a hip/valley member along its own depth axis until its top edge sits
    DROP_CLEARANCE under the sheathing underside of every adjacent facet
    ("dropping the hip"). Returns the applied drop.
    """
    obj = bpy.data.objects.get(name)
    if obj is None:
        return 0.0
    M = obj.matrix_world
    axes = [M.col[i].xyz for i in range(3)]
    drop = 0.0
    for facet in facets:
        n = facet.N
        protrusion = sum(abs(a.dot(n)) for a in axes)
        excess = protrusion - facet.underside + DROP_CLEARANCE
        if excess <= 0.0:
            continue
        depth_axis = max(axes, key=lambda a: abs(a.normalized().dot(n))).normalized()
        if depth_axis.dot(n) < 0.0:
            depth_axis = -depth_axis
        drop = max(drop, excess / depth_axis.dot(n))
        drop_dir = depth_axis
    if drop > 0.0:
        obj.matrix_world = Matrix.Translation(-drop * drop_dir) @ obj.matrix_world
    return drop


def dormer_geom(main_geom, ox, oy, depth, wall_height, roof_pitch_deg,
                stud_width, stud_depth, plate_thickness, rafter_width,
                rafter_depth, overhang, rafter_spacing):
    """Replicates the derived dimensions of base.build_dormer_on_north_slope."""
    half_W = main_geom["half_W"]
    ridge_height = main_geom["ridge_height"]
    plate_z = main_geom["plate_z"]
    main_spacing = main_geom["rafter_spacing"]
    main_tan = (ridge_height - plate_z) / half_W

    support_half = 1.5 * main_spacing
    width = stud_width + 2.0 * support_half
    half_w = width * 0.5
    top_plate_z = wall_height + plate_thickness * 0.5
    m = math.tan(math.radians(roof_pitch_deg))
    run = half_w + overhang
    ridge_z = top_plate_z + run * m
    y_ridge_back = -(ridge_z - ridge_height) / main_tan
    front_y = oy
    back_y = oy - depth

    num_rafters = max(3, int(depth / rafter_spacing) + 2)
    rafter_ys = [front_y - min(i * rafter_spacing, depth) for i in range(num_rafters)]

    return dict(
        ox=ox, front_y=front_y, back_y=back_y, depth=depth,
        x_left=ox - support_half, x_right=ox + support_half,
        half_w=half_w, run=run, ridge_z=ridge_z, top_plate_z=top_plate_z,
        y_ridge_back=y_ridge_back, stud_width=stud_width, stud_depth=stud_depth,
        plate_thickness=plate_thickness, rafter_width=rafter_width,
        rafter_depth=rafter_depth, rafter_ys=rafter_ys, main_tan=main_tan,
    )


def collar_half_len(dg, facet, z_top, margin=0.01):
    """Half-length of a horizontal tie at height z_top that stays under the
    dormer sheathing underside on both slopes."""
    m = (dg["ridge_z"] - dg["top_plate_z"]) / dg["run"]
    z_under_ridge = dg["ridge_z"] + facet.underside / facet.N.z
    return max(0.0, (z_under_ridge - z_top) / m - margin)


def fix_dormer_frame(d_id, dg, main_geom, facet_N, facet_L, facet_R):
    """
    Re-create the dormer members that depend on the valley line so that the
    valley rafters lie exactly on the intersection of the dormer roof plane and
    the main roof plane, seated on the doubled rafters at x_left / x_right.
    """
    ox = dg["ox"]
    ridge_z = dg["ridge_z"]
    y_rb = dg["y_ridge_back"]
    ridge_height = main_geom["ridge_height"]
    raf_w, raf_d = main_geom["rafter_size"]

    N0 = facet_N.plane(0.0)
    valley_top = Vector((ox, y_rb, ridge_z))
    feet = {}
    for side, facet, x_seat in (("L", facet_L, dg["x_left"]), ("R", facet_R, dg["x_right"])):
        foot = isect(facet.plane(0.0), N0, vplane("x", x_seat))
        feet[side] = foot
        base.rafter_between(
            name=f"D{d_id}_Dormer_Valley_{side}",
            E=foot, R=valley_top, section_y=raf_w, section_z=raf_d,
        )

        # valley jacks + their top braces, feet on the corrected valley line
        n_jacks = 3
        for j in range(n_jacks):
            t = (j + 1) / (n_jacks + 1.0)
            y_j = foot.y + t * (y_rb - foot.y)
            P_valley = foot.lerp(valley_top, (y_j - foot.y) / (valley_top.y - foot.y))
            base.rafter_between(
                name=f"D{d_id}_Dormer_Valley_Jack_{side}_{j}",
                E=P_valley, R=Vector((ox, y_j, ridge_z)),
                section_y=dg["rafter_width"], section_z=dg["rafter_depth"],
            )
            if side == "R":
                P_L = feet["L"].lerp(valley_top, (y_j - feet["L"].y) / (valley_top.y - feet["L"].y))
                z_b = P_L.z + 0.6 * (ridge_z - P_L.z)
                half_len = min(abs(P_valley.x - P_L.x) * 0.24,
                               collar_half_len(dg, facet_L, z_b + dg["plate_thickness"] * 0.5))
                base.box(
                    name=f"D{d_id}_Dormer_ValleyTopBrace_{j}",
                    center=(ox, y_j - dg["stud_depth"], z_b),
                    size=(2.0 * half_len, dg["stud_depth"], dg["plate_thickness"]),
                )

    # collar ties between the dormer rafters, trimmed clear of the boards
    z_b = ridge_z - (ridge_z - dg["top_plate_z"]) * 0.3
    half_len = min(0.225 * (2.0 * dg["half_w"] - 2.0 * dg["stud_width"]),
                   collar_half_len(dg, facet_L, z_b + dg["plate_thickness"] * 0.5))
    for i, y_pos in enumerate(dg["rafter_ys"]):
        brace_y = max(min(y_pos - dg["stud_depth"], dg["front_y"]), y_rb)
        base.box(
            name=f"D{d_id}_Dormer_TopBrace_{i}",
            center=(ox, brace_y, z_b),
            size=(2.0 * half_len, dg["stud_depth"], dg["plate_thickness"]),
        )

    # trimmed main rafters: ridge -> corrected valley
    spacing = main_geom["rafter_spacing"]
    ridge_half = main_geom["ridge_half"]
    grid = [-ridge_half + i * spacing for i in range(int(main_geom["ridge_len"] / spacing) + 1)]
    interior = [x for x in grid if dg["x_left"] < x < dg["x_right"]]
    for idx, x_r in enumerate(interior):
        foot = feet["L"] if x_r < ox else feet["R"]
        t = (x_r - foot.x) / (valley_top.x - foot.x)
        P_valley = foot.lerp(valley_top, t)
        base.create_prismatic_member(
            name=f"D{d_id}_Dormer_TrimmedTop_{idx}",
            start=Vector((x_r, 0.0, ridge_height)), end=P_valley,
            width=raf_w, depth=raf_d,
        )

    # side top plates: start where the main sheathing top passes under them
    z_plate_bottom = dg["top_plate_z"] - dg["plate_thickness"] * 0.5
    z_top_at_ridge = ridge_height + facet_N.top / facet_N.N.z
    y_clear = (z_top_at_ridge - z_plate_bottom) / dg["main_tan"]
    y_back = max(dg["back_y"], y_clear)
    for i, x_val in enumerate((dg["x_left"], dg["x_right"])):
        base.box(
            name=f"D{d_id}_Dormer_TopPlate_Side_{i}",
            center=(x_val, 0.5 * (dg["front_y"] + y_back), dg["top_plate_z"]),
            size=(dg["stud_width"], dg["front_y"] - y_back, dg["plate_thickness"]),
        )


# ---------------------------------------------------------------------------
# CONSISTENCY CHECK
# ---------------------------------------------------------------------------

def point_in_loops(u, v, loops):
    inside = False
    for loop in loops:
        n = len(loop)
        for i in range(n):
            u0, v0 = loop[i]
            u1, v1 = loop[(i + 1) % n]
            if (v0 <= v < v1) or (v1 <= v < v0):
                if u < u0 + (v - v0) / (v1 - v0) * (u1 - u0):
                    inside = not inside
    return inside


def report_protrusions(frame_names, facet_regions, tol=0.001):
    """Print every framing member whose corner pokes through a sheathed area."""
    hits = []
    for name in frame_names:
        obj = bpy.data.objects.get(name)
        if obj is None:
            continue
        corners = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
        for facet, loops in facet_regions:
            heights = [(P - facet.O).dot(facet.N) for P in corners]
            if min(heights) > facet.underside:
                continue          # entirely above the boards (e.g. dormer rafter tails)
            worst = 0.0
            for P, h in zip(corners, heights):
                if h > facet.underside + tol:
                    u, v = facet.uv(P)
                    if point_in_loops(u, v, loops):
                        worst = max(worst, h - facet.underside)
            if worst > 0.0:
                hits.append((name, facet.name, worst))
    print(f"[check] framing members poking through sheathing: {len(hits)}")
    for name, fname, h in sorted(hits, key=lambda x: -x[2]):
        print(f"[check]   {name:40s} {fname:10s} +{h * 1000:.1f} mm")
    return hits


# ---------------------------------------------------------------------------
# SCENE ASSEMBLY
# ---------------------------------------------------------------------------

def build_scene():
    # ---- parameters (identical to base.build_scene) ----
    length, width, plate_z = 18.0, 9.0, 0.0
    slope_rise, slope_run = 1.0, 2.0
    rafter_spacing = 0.6
    plate_size = (0.038, 0.140)
    rafter_size = (0.038, 0.184)
    ridge_size = (0.038, 0.184)
    hip_extra_depth = 0.050
    half_W = width * 0.5
    half_L = length * 0.5

    center_offsets = [-5.0 * rafter_spacing, 0.0, 5.0 * rafter_spacing]
    support_half = 1.5 * rafter_spacing
    clear_min = min(cx - support_half for cx in center_offsets) + 0.05
    clear_max = max(cx + support_half for cx in center_offsets) - 0.05

    wing_length, wing_width = 6.0, 6.0
    wing_half_x = wing_width * 0.5

    dormer_kwargs = dict(
        oy=half_W - 0.8, depth=1.6, wall_height=1.2, roof_pitch_deg=35.0,
        stud_width=0.08, stud_depth=0.04, plate_thickness=0.04,
        rafter_width=0.05, rafter_depth=0.08, overhang=0.20, rafter_spacing=0.40,
    )

    colls = dict(
        framing=get_collection("Timber_Framing"),
        sheathing=get_collection("Sheathing"),
    )
    colls["frame_main"] = get_collection("Framing_Main_Roof", colls["framing"])
    colls["frame_wing"] = get_collection("Framing_South_Wing", colls["framing"])
    colls["frame_dormers"] = get_collection("Framing_Dormers", colls["framing"])
    colls["sheath_main"] = get_collection("Sheathing_Main_Roof", colls["sheathing"])
    colls["sheath_wing"] = get_collection("Sheathing_South_Wing", colls["sheathing"])
    colls["sheath_dormers"] = get_collection("Sheathing_Dormers", colls["sheathing"])

    # ---- 1. timber frame from experiment 11 ----
    before = set(o.name for o in bpy.data.objects)
    main_geom = base.build_main_hip_roof(
        length=length, width=width, plate_z=plate_z,
        slope_rise=slope_rise, slope_run=slope_run, rafter_spacing=rafter_spacing,
        plate_size=plate_size, rafter_size=rafter_size,
        hip_extra_depth=hip_extra_depth, ridge_size=ridge_size,
        north_clear_range=(clear_min, clear_max), south_clear_half_x=wing_half_x,
    )
    base.build_T_wing_rotated(main_geom, wing_length=wing_length, wing_width=wing_width)
    dormers = []
    for d_id, cx in enumerate(center_offsets):
        base.build_dormer_on_north_slope(
            main_geom=main_geom, origin=(cx, dormer_kwargs["oy"], 0.0),
            width=dormer_kwargs["stud_width"] + 2.0 * support_half,
            depth=dormer_kwargs["depth"], wall_height=dormer_kwargs["wall_height"],
            roof_pitch_deg=dormer_kwargs["roof_pitch_deg"],
            stud_width=dormer_kwargs["stud_width"],
            rafter_spacing=dormer_kwargs["rafter_spacing"], dormer_id=d_id,
        )
        dormers.append(dormer_geom(main_geom, cx, **dormer_kwargs))
    gap_xs = [0.5 * (center_offsets[i] + center_offsets[i + 1])
              for i in range(len(center_offsets) - 1)]
    base.add_north_gap_rafters(main_geom, gap_xs)

    # ---- 2. roof facets ----
    ridge_h = main_geom["ridge_height"]
    under_main = rafter_size[1] * 0.5
    wing_ridge_h = plate_z + wing_half_x * (slope_rise / slope_run)
    y_wing_s = -half_W - wing_length

    F = {}
    F["N"] = Facet("N", (0, half_W, plate_z), (1, 0, 0), (0, -half_W, ridge_h), under_main)
    F["S"] = Facet("S", (0, -half_W, plate_z), (1, 0, 0), (0, half_W, ridge_h), under_main)
    F["E"] = Facet("E", (half_L, 0, plate_z), (0, 1, 0), (-half_W, 0, ridge_h), under_main)
    F["W"] = Facet("W", (-half_L, 0, plate_z), (0, 1, 0), (half_W, 0, ridge_h), under_main)
    F["WE"] = Facet("WingE", (wing_half_x, -half_W, plate_z), (0, 1, 0), (-wing_half_x, 0, wing_ridge_h), under_main)
    F["WW"] = Facet("WingW", (-wing_half_x, -half_W, plate_z), (0, 1, 0), (wing_half_x, 0, wing_ridge_h), under_main)
    F["WS"] = Facet("WingS", (0, y_wing_s, plate_z), (1, 0, 0), (0, wing_half_x, wing_ridge_h), under_main)
    for d_id, dg in enumerate(dormers):
        run, rise = dg["run"], dg["ridge_z"] - dg["top_plate_z"]
        F[f"D{d_id}L"] = Facet(f"D{d_id}L", (dg["ox"] - run, dg["front_y"], dg["top_plate_z"]),
                               (0, 1, 0), (run, 0, rise), dg["rafter_depth"] * 0.5)
        F[f"D{d_id}R"] = Facet(f"D{d_id}R", (dg["ox"] + run, dg["front_y"], dg["top_plate_z"]),
                               (0, 1, 0), (-run, 0, rise), dg["rafter_depth"] * 0.5)

    # ---- 3. frame corrections so the frame is sheathing-ready ----
    for d_id, dg in enumerate(dormers):
        fix_dormer_frame(d_id, dg, main_geom, F["N"], F[f"D{d_id}L"], F[f"D{d_id}R"])

    drops = {}
    for name, fs in (("Hip_NW", ("N", "W")), ("Hip_NE", ("N", "E")),
                     ("Hip_SW", ("S", "W")), ("Hip_SE", ("S", "E")),
                     ("Wing_Hip_SW", ("WW", "WS")), ("Wing_Hip_SE", ("WE", "WS")),
                     ("Valley_E", ("S", "WE")), ("Valley_W", ("S", "WW"))):
        drops[name] = drop_member(name, [F[k] for k in fs])
    for d_id in range(len(dormers)):
        for side in "LR":
            name = f"D{d_id}_Dormer_Valley_{side}"
            drops[name] = drop_member(name, [F["N"], F[f"D{d_id}{side}"]])
    print("[frame] dropped members (mm): " +
          ", ".join(f"{k}={v * 1000:.0f}" for k, v in drops.items()))

    frame_names = sorted(set(o.name for o in bpy.data.objects) - before)
    sort_framing_into_collections(frame_names, colls)

    # ---- 4. facet outlines (3D points -> facet u/v) ----
    P = lambda *planes: isect(*planes)
    c0 = {k: f.plane(0.0) for k, f in F.items()}       # centre-planes (ridges, hips)
    ct = {k: f.plane(f.top) for k, f in F.items()}     # top surfaces (valleys)

    y_n, y_s = vplane("y", half_W), vplane("y", -half_W)
    x_e, x_w = vplane("x", half_L), vplane("x", -half_L)

    regions = {}
    # main north slope, with one cutout per dormer
    loop_N = [P(c0["N"], c0["W"], y_n), P(c0["N"], c0["E"], y_n),
              P(c0["N"], c0["S"], c0["E"]), P(c0["N"], c0["S"], c0["W"])]
    holes_N = []
    for d_id, dg in enumerate(dormers):
        L, R = ct[f"D{d_id}L"], ct[f"D{d_id}R"]
        # dormer eaves overhang the doubled rafters, so the cutout is bounded
        # by the two eave lines, the front beam face and the two valley lines
        x_eL, x_eR = vplane("x", dg["ox"] - dg["run"]), vplane("x", dg["ox"] + dg["run"])
        y_f = vplane("y", dg["front_y"] + dg["rafter_width"] * 0.5)
        holes_N.append([
            P(c0["N"], x_eL, y_f), P(c0["N"], x_eR, y_f),
            P(R, ct["N"], x_eR), P(L, R, ct["N"]), P(L, ct["N"], x_eL),
        ])
    regions["N"] = [loop_N] + holes_N

    # main south slope, notched by the wing valleys
    regions["S"] = [[
        P(c0["S"], c0["W"], y_s), P(ct["S"], ct["WW"], y_s), P(ct["S"], ct["WW"], ct["WE"]),
        P(ct["S"], ct["WE"], y_s), P(c0["S"], c0["E"], y_s),
        P(c0["S"], c0["N"], c0["E"]), P(c0["S"], c0["N"], c0["W"]),
    ]]
    regions["E"] = [[P(c0["E"], c0["S"], x_e), P(c0["E"], c0["N"], x_e), P(c0["E"], c0["N"], c0["S"])]]
    regions["W"] = [[P(c0["W"], c0["S"], x_w), P(c0["W"], c0["N"], x_w), P(c0["W"], c0["N"], c0["S"])]]

    x_we, x_ww, y_ws = vplane("x", wing_half_x), vplane("x", -wing_half_x), vplane("y", y_wing_s)
    regions["WE"] = [[
        P(c0["WE"], c0["WS"], x_we), P(ct["WE"], ct["S"], y_s), P(ct["WE"], ct["WW"], ct["S"]),
        P(c0["WE"], c0["WW"], ct["S"]), P(c0["WE"], c0["WW"], c0["WS"]),
    ]]
    regions["WW"] = [[
        P(c0["WW"], c0["WS"], x_ww), P(ct["WW"], ct["S"], y_s), P(ct["WW"], ct["WE"], ct["S"]),
        P(c0["WW"], c0["WE"], ct["S"]), P(c0["WW"], c0["WE"], c0["WS"]),
    ]]
    regions["WS"] = [[P(c0["WS"], c0["WW"], y_ws), P(c0["WS"], c0["WE"], y_ws), P(c0["WS"], c0["WE"], c0["WW"])]]

    for d_id, dg in enumerate(dormers):
        y_f = vplane("y", dg["front_y"] + dg["rafter_width"] * 0.5)
        for side, sgn in (("L", -1.0), ("R", 1.0)):
            me, other = f"D{d_id}{side}", f"D{d_id}{'R' if side == 'L' else 'L'}"
            x_eave = vplane("x", dg["ox"] + sgn * dg["run"])
            regions[me] = [[
                P(c0[me], c0[other], y_f), P(c0[me], x_eave, y_f),
                P(ct[me], ct["N"], x_eave), P(ct[me], ct[other], ct["N"]),
                P(c0[me], c0[other], ct["N"]),
            ]]

    # ---- 5. rafter lines (joint positions) ----
    grid_x = [-half_L + 0.3 + 0.6 * k for k in range(int(length / 0.6))]  # -8.7 .. 8.7
    grid_y = [0.6 * k for k in range(-7, 8)]
    joints = {
        "N": [(x, half_W, plate_z) for x in grid_x],
        "S": [(x, -half_W, plate_z) for x in grid_x],
        "E": [(half_L, y, plate_z) for y in grid_y],
        "W": [(-half_L, y, plate_z) for y in grid_y],
        "WE": [(wing_half_x, -half_W - 0.6 * i, plate_z) for i in range(11)],
        "WW": [(-wing_half_x, -half_W - 0.6 * i, plate_z) for i in range(11)],
        "WS": [(-wing_half_x + 0.6 * k, y_wing_s, plate_z) for k in range(11)],
    }
    for d_id, dg in enumerate(dormers):
        for side in "LR":
            joints[f"D{d_id}{side}"] = [(dg["ox"], y, dg["ridge_z"]) for y in dg["rafter_ys"]]

    # ---- 6. boards ----
    facet_regions = []
    total = 0
    for key, loops3d in regions.items():
        facet = F[key]
        loops = [[facet.uv(p) for p in loop] for loop in loops3d]
        if key.startswith("D"):
            coll = colls["sheath_dormers"]
        elif key.startswith("W") and key != "W":
            coll = colls["sheath_wing"]
        else:
            coll = colls["sheath_main"]
        n = sheathe_facet(facet, loops, joints[key], coll, f"Board_{facet.name}")
        print(f"[sheathing] {facet.name:8s} {n:4d} boards")
        total += n
        facet_regions.append((facet, loops))
    print(f"[sheathing] total boards: {total}")

    report_protrusions(frame_names, facet_regions)


if __name__ == "__main__":
    build_scene()
