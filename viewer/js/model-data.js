// Pure model-data logic for the CraftBot viewer: parsing the craftbot-model
// JSON (layers baked by tools/layers.py), material stats, spawn ordering,
// element matching across iterations.
// No DOM or three.js imports - unit-tested with `node --test viewer/test/`.

// Layer set of the viewer. Elements carry a layer index baked by
// tools/layers.py (model JSON "layers" names the baked set; parseModel maps
// those names onto this list, so the two may be reordered independently).
export const LAYERS = ["frame", "cladding ext", "cladding int", "interior", "roof",
  "floors", "foundations", "fixtures", "other"];
// Desaturated warm greys/tans matching the Blender Workbench OBJECT colours
// used by the headless renders (see experiments/*/Fable/render_fable.py).
export const LAYER_COLORS = [0xb08d63, 0x8c8c85, 0x9c9a8e, 0xb9b3a4, 0xc2a173,
  0xd0b98f, 0xa3a39c, 0x7d8a8f, 0xb4b4ac];
export const TIMBER_DENSITY = 500; // kg/m3

// Elements whose name or collection matches these are drawn semi-transparent.
// Deliberately NOT "window": the exports name the timber around an opening
// Window_Sill / Window_Head / FA_Windows, and those are solid members. The
// Blender scripts name the pane itself Glass_* or file it under a Glazing
// collection, which is what actually wants to be see-through.
const GLASS_KEYWORDS = ["glass", "glaz"];

export function classifyGlass(name, collectionPath) {
  const t = `${collectionPath || ""} ${name || ""}`.toLowerCase();
  return GLASS_KEYWORDS.some((kw) => t.includes(kw)) ? 1 : 0;
}

// Baked layer index -> viewer layer index (unknown names -> "other")
function layerIndexMap(names) {
  if (!Array.isArray(names)) {
    throw new Error("model has no baked layers - run python tools/layers.py --bake");
  }
  const other = LAYERS.indexOf("other");
  return names.map((n) => { const i = LAYERS.indexOf(n); return i >= 0 ? i : other; });
}

// Fan-triangulate a polygon face into `out` (array of vertex indices).
function triangulate(face, out) {
  for (let i = 1; i + 1 < face.length; i++) {
    out.push(face[0], face[i], face[i + 1]);
  }
}


// Minimum-volume oriented bounding box of a triangulated mesh (world verts,
// triangle index). Candidate frames: every triangle normal paired with each
// of that triangle's edges - exact for boxes and prisms, a close fit for
// anything else. Returns dims sorted longest first, the matching unit axes
// (row-major 3x3, right-handed) and the box centre.
export function orientedBox(verts, index) {
  const nv = verts.length / 3;
  const seen = new Set();
  let best = null;
  const extent = (ax, ay, az) => {
    let lo = Infinity, hi = -Infinity;
    for (let i = 0; i < nv; i++) {
      const d = verts[i * 3] * ax + verts[i * 3 + 1] * ay + verts[i * 3 + 2] * az;
      if (d < lo) lo = d;
      if (d > hi) hi = d;
    }
    return [lo, hi];
  };
  const tryFrame = (u, v, n) => {
    // Canonical key: sign-normalise so (u, n) and (-u, -n) dedupe
    const key = [n, u].map((a) => {
      const s = Math.sign(Math.abs(a[0]) > 1e-6 ? a[0] : Math.abs(a[1]) > 1e-6 ? a[1] : a[2]) || 1;
      return a.map((c) => (s * c).toFixed(3)).join(",");
    }).join("|");
    if (seen.has(key)) return;
    seen.add(key);
    const eu = extent(...u), ev = extent(...v), en = extent(...n);
    const vol = (eu[1] - eu[0]) * (ev[1] - ev[0]) * (en[1] - en[0]);
    if (!best || vol < best.vol - 1e-12) best = { vol, axes: [u, v, n], ext: [eu, ev, en] };
  };
  const norm = (a) => {
    const l = Math.hypot(a[0], a[1], a[2]);
    return l > 1e-9 ? [a[0] / l, a[1] / l, a[2] / l] : null;
  };
  const crossV = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
  const P = (i) => [verts[i * 3], verts[i * 3 + 1], verts[i * 3 + 2]];
  const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
  for (let t = 0; t < index.length; t += 3) {
    const a = P(index[t]), b = P(index[t + 1]), c = P(index[t + 2]);
    const edges = [sub(b, a), sub(c, b), sub(a, c)];
    const n = norm(crossV(edges[0], sub(c, a)));
    if (!n) continue;
    for (const e of edges) {
      const u = norm(e);
      if (!u) continue;
      tryFrame(u, crossV(n, u), n);
    }
  }
  if (!best) { // degenerate mesh: world-aligned box
    tryFrame([1, 0, 0], [0, 1, 0], [0, 0, 1]);
  }
  const order = [0, 1, 2].sort((i, j) =>
    (best.ext[j][1] - best.ext[j][0]) - (best.ext[i][1] - best.ext[i][0]));
  const axes = order.map((i) => best.axes[i]);
  const ext = order.map((i) => best.ext[i]);
  // Centre from the axes the extents were measured on - before re-handing
  // the frame below, which may negate axis 2.
  const center = [0, 0, 0];
  for (let k = 0; k < 3; k++) {
    const mid = (ext[k][0] + ext[k][1]) / 2;
    center[0] += mid * axes[k][0]; center[1] += mid * axes[k][1]; center[2] += mid * axes[k][2];
  }
  axes[2] = crossV(axes[0], axes[1]); // keep the frame right-handed
  return {
    dims: ext.map((e) => e[1] - e[0]),
    axes: Float32Array.from(axes.flat()),
    center,
  };
}

/**
 * Parse a craftbot-model JSON into typed arrays.
 * Element order: all boxes (creation order), then all meshes (creation order);
 * this is the construction sequence used by entry animations.
 *
 * dims are each element's own (oriented) size, longest first; frames holds the
 * matching unit axes (row-major 3x3 per element) so the element can be shown
 * axis-aligned. centers is the oriented-box centre.
 *
 * Returns {count, names, collections, collection (index per element), layer,
 *          kinds, isGlass, dims, frames, centers, volumes, boxes: {elementIds, matrices},
 *          meshes: [{elementId, name, verts, index}]}
 */
export function parseModel(json) {
  if (json.format !== "craftbot-model" || json.version !== 1) {
    throw new Error(`Unsupported model format: ${json.format} v${json.version}`);
  }
  const colls = json.collections;
  const toLayer = layerIndexMap(json.layers);
  const nb = json.boxes.length;
  const nm = json.meshes.length;
  const count = nb + nm;

  const names = new Array(count);
  const collection = new Uint16Array(count);
  const layer = new Uint8Array(count);
  const kinds = new Uint8Array(count); // 0 = box, 1 = mesh
  const isGlass = new Uint8Array(count); // 1 = drawn semi-transparent
  const dims = new Float32Array(3 * count);
  const frames = new Float32Array(9 * count);
  const centers = new Float32Array(3 * count);
  const volumes = new Float32Array(count);

  const matrices = new Float32Array(16 * nb);
  const elementIds = new Uint32Array(nb);

  for (let b = 0; b < nb; b++) {
    const row = json.boxes[b];
    const name = row[0];
    const coll = colls[row[1]];
    // row-major 3x4: m[2 + r*4 + c]
    const m = row;
    const o = 2;
    names[b] = name;
    collection[b] = row[1];
    layer[b] = toLayer[row[14]];
    isGlass[b] = classifyGlass(name, coll);
    kinds[b] = 0;
    elementIds[b] = b;
    // Column-major 4x4 for three.js instanceMatrix
    const M = matrices;
    const k = b * 16;
    M[k + 0] = m[o + 0]; M[k + 1] = m[o + 4]; M[k + 2] = m[o + 8]; M[k + 3] = 0;
    M[k + 4] = m[o + 1]; M[k + 5] = m[o + 5]; M[k + 6] = m[o + 9]; M[k + 7] = 0;
    M[k + 8] = m[o + 2]; M[k + 9] = m[o + 6]; M[k + 10] = m[o + 10]; M[k + 11] = 0;
    M[k + 12] = m[o + 3]; M[k + 13] = m[o + 7]; M[k + 14] = m[o + 11]; M[k + 15] = 1;
    // Sizes: 2 x column norms of the 3x3 part (unit cube is 2x2x2); the
    // normalised columns are the box's own axes.
    const cols = [0, 1, 2].map((c) => [m[o + c], m[o + 4 + c], m[o + 8 + c]]);
    const lens = cols.map((v) => 2 * Math.hypot(v[0], v[1], v[2]));
    const order = [0, 1, 2].sort((i, j) => lens[j] - lens[i]);
    for (let k = 0; k < 3; k++) {
      const c = order[k];
      dims[b * 3 + k] = lens[c];
      for (let i = 0; i < 3; i++) frames[b * 9 + k * 3 + i] = cols[c][i] / (lens[c] / 2 || 1);
    }
    // Re-derive the third axis so the frame stays right-handed after sorting
    const f = frames, q = b * 9;
    f[q + 6] = f[q + 1] * f[q + 5] - f[q + 2] * f[q + 4];
    f[q + 7] = f[q + 2] * f[q + 3] - f[q + 0] * f[q + 5];
    f[q + 8] = f[q + 0] * f[q + 4] - f[q + 1] * f[q + 3];
    centers[b * 3] = m[o + 3]; centers[b * 3 + 1] = m[o + 7]; centers[b * 3 + 2] = m[o + 11];
    volumes[b] = lens[0] * lens[1] * lens[2];
  }

  const meshes = [];
  for (let j = 0; j < nm; j++) {
    const src = json.meshes[j];
    const e = nb + j;
    names[e] = src.name;
    collection[e] = src.collection;
    layer[e] = toLayer[src.layer];
    isGlass[e] = classifyGlass(src.name, colls[src.collection]);
    kinds[e] = 1;
    const verts = Float32Array.from(src.verts);
    const idx = [];
    for (const face of src.faces) triangulate(face, idx);
    const index = Uint32Array.from(idx);
    const ob = orientedBox(verts, index);
    dims.set(ob.dims, e * 3);
    frames.set(ob.axes, e * 9);
    centers.set(ob.center, e * 3);
    // Volume: sum of signed tetra volumes over triangles (divergence theorem)
    let vol = 0;
    for (let i = 0; i < index.length; i += 3) {
      const a = index[i] * 3, b2 = index[i + 1] * 3, c = index[i + 2] * 3;
      const ax = verts[a], ay = verts[a + 1], az = verts[a + 2];
      const bx = verts[b2], by = verts[b2 + 1], bz = verts[b2 + 2];
      const cx = verts[c], cy = verts[c + 1], cz = verts[c + 2];
      vol += (ax * (by * cz - bz * cy)
        + ay * (bz * cx - bx * cz)
        + az * (bx * cy - by * cx)) / 6;
    }
    // Some generators emit inside-out prisms (consistent but reversed
    // winding). Negative signed volume = inverted: flip every triangle so the
    // faces are front-facing again.
    if (vol < 0) {
      for (let i = 0; i < index.length; i += 3) {
        const t = index[i + 1]; index[i + 1] = index[i + 2]; index[i + 2] = t;
      }
    }
    volumes[e] = Math.abs(vol);
    meshes.push({ elementId: e, name: src.name, verts, index });
  }

  return {
    count, names, collections: colls, collection, layer, kinds, isGlass, dims, frames,
    centers, volumes,
    boxes: { elementIds, matrices }, meshes,
  };
}

/**
 * Per-layer material stats for the currently visible layers.
 * visible: bool[] indexed like LAYERS. Length = element's oriented length.
 * Returns [{layer, count, lengthM, volumeM3, weightKg}] for every layer.
 */
export function computeStats(model, visible) {
  const rows = LAYERS.map((layer) => ({ layer, count: 0, lengthM: 0, volumeM3: 0, weightKg: 0 }));
  for (let e = 0; e < model.count; e++) {
    const li = model.layer[e];
    if (!visible[li]) continue;
    const r = rows[li];
    r.count += 1;
    r.lengthM += model.dims[e * 3];
    r.volumeM3 += model.volumes[e];
  }
  for (const r of rows) r.weightKg = r.volumeM3 * TIMBER_DENSITY;
  return rows;
}

// Layer build order for the "layers" spawn mode.
const BUILD_ORDER = ["foundations", "frame", "floors", "roof", "cladding ext",
  "cladding int", "interior", "fixtures", "other"];

// Spawn time that keeps an element in place (see the vertex patch in animations.js)
export const STATIC_SPAWN = -1e9;

/**
 * Per-element spawn times (seconds) for entry animations.
 * orderMode "sequence": element order (construction sequence).
 * orderMode "layers": BUILD_ORDER, elements staggered within each layer.
 * kept (optional Uint8Array): elements flagged 1 stay static; only the rest
 * are staggered over the duration.
 */
export function computeSpawnTimes(model, orderMode, totalDuration = 3.0, kept = null) {
  const n = model.count;
  const times = new Float32Array(n);
  const span = totalDuration * 0.8;
  let order = [];
  if (orderMode === "layers") {
    for (const name of BUILD_ORDER) {
      const li = LAYERS.indexOf(name);
      for (let e = 0; e < n; e++) if (model.layer[e] === li) order.push(e);
    }
  } else {
    for (let e = 0; e < n; e++) order.push(e);
  }
  if (kept) {
    order = order.filter((e) => !kept[e]);
    for (let e = 0; e < n; e++) if (kept[e]) times[e] = STATIC_SPAWN;
  }
  const m = order.length;
  for (let i = 0; i < m; i++) times[order[i]] = m > 1 ? (i / (m - 1)) * span : 0;
  return times;
}

// Identity of an element across iterations of one model: name, kind and its
// placement/size (rounded so re-exports of unchanged code match exactly).
function elementKey(model, e, nb) {
  const r = (v, s) => Math.round(v * s) / s + 0; // + 0 folds -0 into 0
  const parts = [model.names[e], model.kinds[e]];
  for (let k = 0; k < 3; k++) parts.push(r(model.centers[e * 3 + k], 1e4), r(model.dims[e * 3 + k], 1e4));
  for (let k = 0; k < 9; k++) parts.push(r(model.frames[e * 9 + k], 1e3));
  if (model.kinds[e] === 1) {
    const v = model.meshes[e - nb].verts;
    let sum = 0;
    for (let i = 0; i < v.length; i++) sum += v[i];
    parts.push(v.length, r(sum, 1e3));
  }
  return parts.join("|");
}

/**
 * Pair the elements of `next` with unchanged elements of `prev`.
 * Returns Int32Array(next.count): previous element id, or -1 when the
 * element is new or moved. Equal keys pair one-to-one in element order.
 */
export function matchElements(prev, next) {
  const pool = new Map(); // key -> queue of prev ids
  const pnb = prev.boxes.elementIds.length;
  for (let e = 0; e < prev.count; e++) {
    const k = elementKey(prev, e, pnb);
    if (!pool.has(k)) pool.set(k, []);
    pool.get(k).push(e);
  }
  const map = new Int32Array(next.count).fill(-1);
  const nnb = next.boxes.elementIds.length;
  for (let e = 0; e < next.count; e++) {
    const ids = pool.get(elementKey(next, e, nnb));
    if (ids && ids.length) map[e] = ids.shift();
  }
  return map;
}

// Element id for a triangle of the merged mesh geometry (used by picking).
export function elementForFace(faceElement, faceIndex) {
  return faceElement[faceIndex];
}
