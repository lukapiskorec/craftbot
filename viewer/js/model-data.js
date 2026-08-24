// Pure model-data logic for the CraftBot viewer: parsing the craftbot-model
// JSON, layer classification, material stats, spawn ordering.
// No DOM or three.js imports - unit-tested with `node --test viewer/test/`.

export const LAYERS = ["foundations", "floors", "frame", "roof", "cladding", "other"];
// Desaturated warm greys/tans matching the Blender Workbench OBJECT colours
// used by the headless renders (see experiments/*/Fable/render_fable.py).
export const LAYER_COLORS = [0xa3a39c, 0xd0b98f, 0xb08d63, 0xc2a173, 0x8c8c85, 0xb4b4ac];
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

// Order matters: first match wins ("Roof_Beam" is roof, not frame).
// Collection path is checked before the element name.
const RULES = [
  ["foundations", ["found", "footing", "pad", "pier", "plinth", "podium", "ground"]],
  ["floors", ["floor", "slab", "deck", "joist", "ceiling", "landing", "stair", "tread"]],
  ["roof", ["roof", "rafter", "ridge", "hip", "purlin", "eave", "fascia", "dormer", "sheath", "batten"]],
  ["cladding", ["clad", "board", "siding", "panel", "wall", "window", "door", "glaz"]],
  ["frame", ["frame", "post", "beam", "column", "stud", "brace", "truss", "girt",
    "plate", "sill", "lintel", "chord", "strut", "king", "collar"]],
];

function matchRules(text) {
  const t = text.toLowerCase();
  for (let i = 0; i < RULES.length; i++) {
    for (const kw of RULES[i][1]) {
      if (t.includes(kw)) return LAYERS.indexOf(RULES[i][0]);
    }
  }
  return -1;
}

export function classifyLayer(name, collectionPath) {
  if (collectionPath) {
    const m = matchRules(collectionPath);
    if (m >= 0) return m;
  }
  const m = matchRules(name || "");
  return m >= 0 ? m : LAYERS.indexOf("other");
}

// Fan-triangulate a polygon face into `out` (array of vertex indices).
function triangulate(face, out) {
  for (let i = 1; i + 1 < face.length; i++) {
    out.push(face[0], face[i], face[i + 1]);
  }
}

/**
 * Parse a craftbot-model JSON into typed arrays.
 * Element order: all boxes (creation order), then all meshes (creation order);
 * this is the construction sequence used by entry animations.
 *
 * Returns {count, names, collections, layer, kinds, isGlass, dims, centers,
 *          volumes, boxes: {elementIds, matrices},
 *          meshes: [{elementId, name, verts, index}]}
 */
export function parseModel(json) {
  if (json.format !== "craftbot-model" || json.version !== 1) {
    throw new Error(`Unsupported model format: ${json.format} v${json.version}`);
  }
  const colls = json.collections;
  const nb = json.boxes.length;
  const nm = json.meshes.length;
  const count = nb + nm;

  const names = new Array(count);
  const layer = new Uint8Array(count);
  const kinds = new Uint8Array(count); // 0 = box, 1 = mesh
  const isGlass = new Uint8Array(count); // 1 = drawn semi-transparent
  const dims = new Float32Array(3 * count);
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
    layer[b] = classifyLayer(name, coll);
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
    // Sizes: 2 x column norms of the 3x3 part (unit cube is 2x2x2)
    const dx = 2 * Math.hypot(m[o + 0], m[o + 4], m[o + 8]);
    const dy = 2 * Math.hypot(m[o + 1], m[o + 5], m[o + 9]);
    const dz = 2 * Math.hypot(m[o + 2], m[o + 6], m[o + 10]);
    dims[b * 3] = dx; dims[b * 3 + 1] = dy; dims[b * 3 + 2] = dz;
    centers[b * 3] = m[o + 3]; centers[b * 3 + 1] = m[o + 7]; centers[b * 3 + 2] = m[o + 11];
    volumes[b] = dx * dy * dz;
  }

  const meshes = [];
  for (let j = 0; j < nm; j++) {
    const src = json.meshes[j];
    const e = nb + j;
    names[e] = src.name;
    layer[e] = classifyLayer(src.name, colls[src.collection]);
    isGlass[e] = classifyGlass(src.name, colls[src.collection]);
    kinds[e] = 1;
    const verts = Float32Array.from(src.verts);
    const idx = [];
    for (const face of src.faces) triangulate(face, idx);
    const index = Uint32Array.from(idx);
    // World AABB
    let minx = Infinity, miny = Infinity, minz = Infinity;
    let maxx = -Infinity, maxy = -Infinity, maxz = -Infinity;
    for (let i = 0; i < verts.length; i += 3) {
      minx = Math.min(minx, verts[i]); maxx = Math.max(maxx, verts[i]);
      miny = Math.min(miny, verts[i + 1]); maxy = Math.max(maxy, verts[i + 1]);
      minz = Math.min(minz, verts[i + 2]); maxz = Math.max(maxz, verts[i + 2]);
    }
    dims[e * 3] = maxx - minx; dims[e * 3 + 1] = maxy - miny; dims[e * 3 + 2] = maxz - minz;
    centers[e * 3] = (minx + maxx) / 2;
    centers[e * 3 + 1] = (miny + maxy) / 2;
    centers[e * 3 + 2] = (minz + maxz) / 2;
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
    volumes[e] = Math.abs(vol);
    meshes.push({ elementId: e, name: src.name, verts, index });
  }

  return {
    count, names, collections: colls, layer, kinds, isGlass, dims, centers, volumes,
    boxes: { elementIds, matrices }, meshes,
  };
}

/**
 * Per-layer material stats for the currently visible layers.
 * visible: bool[6] indexed like LAYERS. Length = longest element dimension.
 * Returns [{layer, count, lengthM, volumeM3, weightKg}] for all 6 layers.
 */
export function computeStats(model, visible) {
  const rows = LAYERS.map((layer) => ({ layer, count: 0, lengthM: 0, volumeM3: 0, weightKg: 0 }));
  for (let e = 0; e < model.count; e++) {
    const li = model.layer[e];
    if (!visible[li]) continue;
    const r = rows[li];
    r.count += 1;
    r.lengthM += Math.max(model.dims[e * 3], model.dims[e * 3 + 1], model.dims[e * 3 + 2]);
    r.volumeM3 += model.volumes[e];
  }
  for (const r of rows) r.weightKg = r.volumeM3 * TIMBER_DENSITY;
  return rows;
}

// Layer build order for the "layers" spawn mode.
const BUILD_ORDER = ["foundations", "floors", "frame", "roof", "cladding", "other"];

/**
 * Per-element spawn times (seconds) for entry animations.
 * orderMode "sequence": element order (construction sequence).
 * orderMode "layers": foundations -> floors -> frame -> roof -> cladding -> other,
 * elements staggered within each layer.
 */
export function computeSpawnTimes(model, orderMode, totalDuration = 3.0) {
  const n = model.count;
  const times = new Float32Array(n);
  const span = totalDuration * 0.8;
  if (n <= 1) return times;
  if (orderMode === "layers") {
    const order = [];
    for (const name of BUILD_ORDER) {
      const li = LAYERS.indexOf(name);
      for (let e = 0; e < n; e++) if (model.layer[e] === li) order.push(e);
    }
    for (let i = 0; i < order.length; i++) times[order[i]] = (i / (n - 1)) * span;
  } else {
    for (let e = 0; e < n; e++) times[e] = (e / (n - 1)) * span;
  }
  return times;
}

// Element id for a triangle of the merged mesh geometry (used by picking).
export function elementForFace(faceElement, faceIndex) {
  return faceElement[faceIndex];
}
