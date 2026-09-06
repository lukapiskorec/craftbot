// Knolling: rearranging every element of a model onto a grid. Pure logic, no
// DOM or three.js - unit-tested with `node --test viewer/test/*.test.mjs`.
//
// A layout is a pose per element: a quaternion that rotates the element's
// model-space offsets about its own centre, and the new centre position.
// The vertex patch in animations.js blends two layouts per vertex, so a
// transition is just "from" and "to" plus a start delay per element.
//
// Three arrangements exist. "model" is where the export put the elements.
// "flat" lies every element on its widest face, long axis along X, one band
// of shelves per layer in build order (a Knoll photograph). "stacked" bundles
// elements of the same layer and size into palette-style blocks (columns
// across, courses high) and shelf-packs the blocks per layer band.

import { LAYERS } from "./model-data.js";

export const ARRANGEMENTS = ["model", "flat", "stacked"];

// Layer order of the bands, ground up (same as the entry animation's order)
const BUILD_ORDER = ["foundations", "frame", "floors", "roof", "cladding ext",
  "cladding int", "interior", "fixtures", "other"];
const BAND_LAYERS = BUILD_ORDER.map((n) => LAYERS.indexOf(n));

const POSE_CHUNK = 256; // elements posed between two progress reports

function median(values) {
  if (!values.length) return 0;
  const s = Float64Array.from(values).sort();
  return s[s.length >> 1];
}

// Quaternion (x, y, z, w) of a rotation matrix given by rows
function quatFromRows(r0, r1, r2) {
  const m00 = r0[0], m01 = r0[1], m02 = r0[2];
  const m10 = r1[0], m11 = r1[1], m12 = r1[2];
  const m20 = r2[0], m21 = r2[1], m22 = r2[2];
  const trace = m00 + m11 + m22;
  let x, y, z, w;
  if (trace > 0) {
    const s = 0.5 / Math.sqrt(trace + 1);
    w = 0.25 / s; x = (m21 - m12) * s; y = (m02 - m20) * s; z = (m10 - m01) * s;
  } else if (m00 > m11 && m00 > m22) {
    const s = 2 * Math.sqrt(1 + m00 - m11 - m22);
    w = (m21 - m12) / s; x = 0.25 * s; y = (m01 + m10) / s; z = (m02 + m20) / s;
  } else if (m11 > m22) {
    const s = 2 * Math.sqrt(1 + m11 - m00 - m22);
    w = (m02 - m20) / s; x = (m01 + m10) / s; y = 0.25 * s; z = (m12 + m21) / s;
  } else {
    const s = 2 * Math.sqrt(1 + m22 - m00 - m11);
    w = (m10 - m01) / s; x = (m02 + m20) / s; y = (m12 + m21) / s; z = 0.25 * s;
  }
  const l = Math.hypot(x, y, z, w) || 1;
  return [x / l, y / l, z / l, w / l];
}

// Rotation that lays element e flat: its length axis onto +X or -X, width
// onto Y, thickness onto Z. Of the sign choices that keep the frame
// right-handed, the one closest to no rotation at all (largest trace). Two
// equal dims (a square post, a square sheet) make the axis order arbitrary,
// so the swapped pair is tried as well - a 90 degree turn instead of 120.
const SIGNS = [[1, 1, 1], [-1, -1, 1], [-1, 1, -1], [1, -1, -1]];
const neg = (v) => [-v[0], -v[1], -v[2]];
export function flatQuaternion(model, e) {
  const f = model.frames;
  const q = e * 9;
  const a0 = [f[q], f[q + 1], f[q + 2]];
  const a1 = [f[q + 3], f[q + 4], f[q + 5]];
  const a2 = [f[q + 6], f[q + 7], f[q + 8]];
  const d = model.dims;
  const same = (i, j) => Math.abs(d[e * 3 + i] - d[e * 3 + j]) <= 0.01 * d[e * 3 + i];
  const frames = [[a0, a1, a2]];
  if (same(1, 2)) frames.push([a0, a2, neg(a1)]);
  if (same(0, 1)) frames.push([a1, a0, neg(a2)]);
  let best = null, bestTrace = -Infinity;
  for (const fr of frames) {
    for (const s of SIGNS) {
      const trace = s[0] * fr[0][0] + s[1] * fr[1][1] + s[2] * fr[2][2];
      if (trace > bestTrace) {
        bestTrace = trace;
        best = fr.map((row, k) => row.map((c) => c * s[k]));
      }
    }
  }
  return quatFromRows(best[0], best[1], best[2]);
}

// Rotate v by quaternion q (x, y, z, w)
export function rotate(q, v) {
  const [qx, qy, qz, qw] = q;
  const tx = 2 * (qy * v[2] - qz * v[1]);
  const ty = 2 * (qz * v[0] - qx * v[2]);
  const tz = 2 * (qx * v[1] - qy * v[0]);
  return [
    v[0] + qw * tx + (qy * tz - qz * ty),
    v[1] + qw * ty + (qz * tx - qx * tz),
    v[2] + qw * tz + (qx * ty - qy * tx),
  ];
}

function emptyBounds() {
  return { min: [Infinity, Infinity, Infinity], max: [-Infinity, -Infinity, -Infinity] };
}
function growBounds(b, lo, hi) {
  for (let k = 0; k < 3; k++) {
    if (lo[k] < b.min[k]) b.min[k] = lo[k];
    if (hi[k] > b.max[k]) b.max[k] = hi[k];
  }
}
export function unionBounds(a, b) {
  const out = emptyBounds();
  growBounds(out, a.min, a.max);
  growBounds(out, b.min, b.max);
  return out;
}

function makeLayout(n) {
  const quats = new Float32Array(n * 4);
  for (let e = 0; e < n; e++) quats[e * 4 + 3] = 1;
  return { quats, positions: new Float32Array(n * 3), bounds: emptyBounds() };
}

// The export's own placement: identity rotation, oriented-box centres.
export function modelLayout(model) {
  const n = model.count;
  const layout = makeLayout(n);
  layout.positions.set(model.centers.subarray(0, n * 3));
  for (let e = 0; e < n; e++) {
    // axis-aligned box of the oriented box: sum of |half-dim * axis| per axis
    const half = [0, 0, 0];
    for (let k = 0; k < 3; k++) {
      const h = model.dims[e * 3 + k] / 2;
      for (let i = 0; i < 3; i++) half[i] += h * Math.abs(model.frames[e * 9 + k * 3 + i]);
    }
    const c = [model.centers[e * 3], model.centers[e * 3 + 1], model.centers[e * 3 + 2]];
    growBounds(layout.bounds, c.map((v, i) => v - half[i]), c.map((v, i) => v + half[i]));
  }
  return layout;
}

// Shelf packing: items ({w, h, z?}) in the given order, left to right along
// X until a row reaches targetWidth, then a new row further down (-Y). Rows
// of one band start at y0 and the band's bottom edge is returned. Tall items
// (stacks, z) push the next row further away so rows read apart in axo.
// place(item, x0, yTop) receives the item's left edge and top edge.
function packBand(items, targetWidth, gap, y0, place) {
  let x = 0, y = y0, rowH = 0, rowZ = 0;
  for (const it of items) {
    if (x > 0 && x + it.w > targetWidth) {
      y -= rowH + gap + ROW_CLEARANCE * rowZ;
      x = 0; rowH = 0; rowZ = 0;
    }
    place(it, x, y);
    x += it.w + gap;
    if (it.h > rowH) rowH = it.h;
    if ((it.z ?? 0) > rowZ) rowZ = it.z;
  }
  return y - rowH;
}
const ROW_CLEARANCE = 0.6; // extra row spacing per unit of stack height

// One entry per layer with elements, in band order: element ids, count,
// axis-aligned bounds of the band and its length range - for the labels
// the viewer shows next to each band.
function bandStats(model, layout) {
  const bands = [];
  for (const li of BAND_LAYERS) {
    const ids = [];
    for (let e = 0; e < model.count; e++) if (model.layer[e] === li) ids.push(e);
    if (!ids.length) continue;
    const b = emptyBounds();
    let minLen = Infinity, maxLen = 0;
    for (const e of ids) {
      const p = layout.positions, d = model.dims;
      growBounds(b,
        [p[e * 3] - d[e * 3] / 2, p[e * 3 + 1] - d[e * 3 + 1] / 2, p[e * 3 + 2] - d[e * 3 + 2] / 2],
        [p[e * 3] + d[e * 3] / 2, p[e * 3 + 1] + d[e * 3 + 1] / 2, p[e * 3 + 2] + d[e * 3 + 2] / 2]);
      if (d[e * 3] < minLen) minLen = d[e * 3];
      if (d[e * 3] > maxLen) maxLen = d[e * 3];
    }
    bands.push({ layer: li, ids, count: ids.length, min: b.min, max: b.max, minLen, maxLen });
  }
  return bands;
}

// Items grouped into one list per band layer, in band order
function bandLists(model, items) {
  const perLayer = LAYERS.map(() => []);
  for (const it of items) perLayer[model.layer[it.e]].push(it);
  return BAND_LAYERS.map((li) => perLayer[li]).filter((list) => list.length);
}

// Width the shelves aim for: a squarish sheet, never narrower than the
// longest piece.
function targetWidth(items, gap) {
  let area = 0, maxW = 0;
  for (const it of items) {
    area += (it.w + gap) * (it.h + gap);
    if (it.w > maxW) maxW = it.w;
  }
  return Math.max(Math.sqrt(area) * 1.3, maxW + gap);
}

// Move every position so the layout's XY centre lands on (cx, cy)
function centreOn(layout, cx, cy) {
  const b = layout.bounds;
  const dx = cx - (b.min[0] + b.max[0]) / 2;
  const dy = cy - (b.min[1] + b.max[1]) / 2;
  for (let e = 0; e < layout.positions.length / 3; e++) {
    layout.positions[e * 3] += dx;
    layout.positions[e * 3 + 1] += dy;
  }
  b.min[0] += dx; b.max[0] += dx; b.min[1] += dy; b.max[1] += dy;
}

function placeFlat(layout, e, quat, x, y, z, L, W, T) {
  layout.quats.set(quat, e * 4);
  layout.positions[e * 3] = x;
  layout.positions[e * 3 + 1] = y;
  layout.positions[e * 3 + 2] = z;
  growBounds(layout.bounds, [x - L / 2, y - W / 2, z - T / 2], [x + L / 2, y + W / 2, z + T / 2]);
}

const dimKey = (model, e) => [0, 1, 2].map((k) => Math.round(model.dims[e * 3 + k] * 200)).join("x");

/**
 * Generator computing the flat and stacked layouts of a model. Yields a
 * progress fraction (0..1) between chunks so a caller can keep a progress
 * bar moving; its return value is {model, flat, stacked}.
 * modelBounds: {min, max} of the model (the grids sit on its ground plane,
 * centred on its footprint).
 */
export function* layoutSteps(model, modelBounds) {
  const n = model.count;
  const quats = new Array(n);
  for (let e = 0; e < n; e++) {
    quats[e] = flatQuaternion(model, e);
    if ((e + 1) % POSE_CHUNK === 0) yield (0.6 * (e + 1)) / n;
  }
  const lengths = new Float64Array(n);
  for (let e = 0; e < n; e++) lengths[e] = model.dims[e * 3];
  const gap = Math.max(0.02, 0.04 * median(lengths));
  const bandGap = gap * 4;
  const z0 = modelBounds.min[2];
  const cx = (modelBounds.min[0] + modelBounds.max[0]) / 2;
  const cy = (modelBounds.min[1] + modelBounds.max[1]) / 2;
  const dims = (e) => [model.dims[e * 3], model.dims[e * 3 + 1], model.dims[e * 3 + 2]];

  // ---- flat: one item per element, longest first inside each band ----
  const flat = makeLayout(n);
  {
    const items = [];
    for (let e = 0; e < n; e++) {
      const [L, W, T] = dims(e);
      items.push({ e, w: L, h: W, t: T });
    }
    const byLength = (a, b) => (b.w - a.w) || (b.h - a.h) || (a.e - b.e);
    const width = targetWidth(items, gap);
    let y = 0;
    for (const band of bandLists(model, items)) {
      band.sort(byLength);
      y = packBand(band, width, gap, y, (it, x0, yTop) =>
        placeFlat(flat, it.e, quats[it.e], x0 + it.w / 2, yTop - it.h / 2, z0 + it.t / 2, it.w, it.h, it.t));
      y -= bandGap;
    }
    centreOn(flat, cx, cy);
    flat.bands = bandStats(model, flat);
  }
  yield 0.8;

  // ---- stacked: bundles of identical elements, then shelf-packed ----
  const stacked = makeLayout(n);
  {
    const groups = new Map(); // layer|dims -> [e]
    for (let e = 0; e < n; e++) {
      const key = `${model.layer[e]}|${dimKey(model, e)}`;
      if (!groups.has(key)) groups.set(key, []);
      groups.get(key).push(e);
    }
    const maxHeight = Math.max(0.6 * median(lengths), 0.3);
    const blocks = [];
    for (const members of groups.values()) {
      const [L, W, T] = dims(members[0]);
      const count = members.length;
      const courseCap = Math.max(1, Math.floor((maxHeight + gap) / (T + gap)));
      let courses = Math.min(Math.ceil(Math.sqrt((count * W) / T)), courseCap);
      const across = Math.ceil(count / courses);
      courses = Math.ceil(count / across); // drop courses the last column left empty
      blocks.push({
        e: members[0], members, L, W, T, across, courses,
        w: L, h: across * W + (across - 1) * gap, z: courses * T + (courses - 1) * gap,
      });
    }
    const byFootprint = (a, b) => (b.w - a.w) || (b.h - a.h) || (a.e - b.e);
    const stackGap = gap * 2; // stacks stand further apart than single pieces
    const width = targetWidth(blocks, stackGap);
    let y = 0;
    for (const band of bandLists(model, blocks)) {
      band.sort(byFootprint);
      y = packBand(band, width, stackGap, y, (blk, x0, yTop) => {
        for (let i = 0; i < blk.members.length; i++) {
          const course = Math.floor(i / blk.across);
          const col = i % blk.across;
          placeFlat(stacked, blk.members[i], quats[blk.members[i]],
            x0 + blk.L / 2,
            yTop - col * (blk.W + gap) - blk.W / 2,
            z0 + course * (blk.T + gap) + blk.T / 2,
            blk.L, blk.W, blk.T);
        }
      });
      y -= bandGap;
    }
    centreOn(stacked, cx, cy);
    stacked.bands = bandStats(model, stacked);
  }
  yield 1;
  return { model: modelLayout(model), flat, stacked };
}

// Run the generator to completion (tests, and callers without a progress bar)
export function computeLayouts(model, modelBounds) {
  const steps = layoutSteps(model, modelBounds);
  for (;;) {
    const r = steps.next();
    if (r.done) return r.value;
  }
}

/**
 * Start delay per element (0..1, scaled by the stagger fraction in the
 * shader) for a transition from layout `from` to layout `to`. Stacks are
 * built bottom course first and taken apart from the top; within that,
 * leaving the model takes the building apart from the top layer down,
 * returning rebuilds it ground up, and between two grids the construction
 * sequence is used.
 */
export function transitionDelays(model, fromName, toName, from = null, to = null) {
  const n = model.count;
  const band = new Int32Array(n); // rank of the element's layer in build order
  for (let e = 0; e < n; e++) band[e] = BAND_LAYERS.indexOf(model.layer[e]);
  const course = (layout, e) => Math.round(layout.positions[e * 3 + 2] * 1000);
  let stack = () => 0;
  if (toName === "stacked" && to) stack = (a, b) => course(to, a) - course(to, b);
  else if (fromName === "stacked" && from) stack = (a, b) => course(from, b) - course(from, a);
  let sequence;
  if (fromName === "model") sequence = (a, b) => (band[b] - band[a]) || (b - a);
  else if (toName === "model") sequence = (a, b) => (band[a] - band[b]) || (a - b);
  else sequence = (a, b) => a - b;
  const order = Array.from({ length: n }, (_, e) => e);
  order.sort((a, b) => stack(a, b) || sequence(a, b));
  const delays = new Float32Array(n);
  for (let i = 0; i < n; i++) delays[order[i]] = n > 1 ? i / (n - 1) : 0;
  return delays;
}

// Per-element progress of a transition at global time t - the same curve as
// the vertex patch, so a layout interpolated here matches what is drawn.
export function elementProgress(t, delay, stagger) {
  const u = Math.min(1, Math.max(0, (t - delay * stagger) / (1 - stagger)));
  return u * u * (3 - 2 * u);
}

// The layout the elements are drawn in at time t of a transition - used as
// the "from" pose when a new arrangement is picked mid-flight, so the
// elements retarget from where they are instead of jumping.
export function interpolateLayout(from, to, delays, t, { stagger, lift }) {
  const n = delays.length;
  const out = makeLayout(n);
  for (let e = 0; e < n; e++) {
    const u = elementProgress(t, delays[e], stagger);
    const q = e * 4, p = e * 3;
    let dot = 0;
    for (let k = 0; k < 4; k++) dot += from.quats[q + k] * to.quats[q + k];
    const sign = dot < 0 ? -1 : 1;
    let len = 0;
    for (let k = 0; k < 4; k++) {
      out.quats[q + k] = from.quats[q + k] * (1 - u) + sign * to.quats[q + k] * u;
      len += out.quats[q + k] ** 2;
    }
    len = Math.sqrt(len) || 1;
    for (let k = 0; k < 4; k++) out.quats[q + k] /= len;
    for (let k = 0; k < 3; k++) out.positions[p + k] = from.positions[p + k] * (1 - u) + to.positions[p + k] * u;
    out.positions[p + 2] += lift * Math.sin(Math.PI * u);
  }
  out.bounds = unionBounds(from.bounds, to.bounds);
  return out;
}
