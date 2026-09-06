import test from "node:test";
import assert from "node:assert/strict";
import { parseModel, LAYERS } from "../js/model-data.js";
import {
  flatQuaternion, rotate, modelLayout, computeLayouts, layoutSteps, transitionDelays,
  interpolateLayout, elementProgress, unionBounds,
} from "../js/knolling.js";

// Axis-aligned box row: half extents hx, hy, hz at centre c, layer index li
function box(name, li, [hx, hy, hz], [cx, cy, cz]) {
  return [name, 0, hx, 0, 0, cx, 0, hy, 0, cy, 0, 0, hz, cz, li];
}
// Box rotated 90 degrees about Z (its long side along Y)
function boxRotZ(name, li, [hx, hy, hz], [cx, cy, cz]) {
  return [name, 0, 0, -hy, 0, cx, hx, 0, 0, cy, 0, 0, hz, cz, li];
}

const LAYER_NAMES = ["frame", "roof", "foundations", "cladding ext"];
function model(boxes) {
  return parseModel({
    format: "craftbot-model", version: 1, source: "s", collections: [""],
    layers: LAYER_NAMES, boxes, meshes: [],
  });
}
const li = (name) => LAYER_NAMES.indexOf(name);

// A small house: 6 identical vertical posts, 4 beams lying along X, 3 along
// Y, 2 footings, 1 roof sheet
function house() {
  const rows = [];
  for (let i = 0; i < 6; i++) rows.push(box(`Post_${i}`, li("frame"), [0.05, 0.05, 1.5], [i * 2, i % 2 * 4, 1.5]));
  for (let i = 0; i < 4; i++) rows.push(box(`Beam_${i}`, li("frame"), [2.4, 0.1, 0.06], [2, i, 3.1]));
  for (let i = 0; i < 3; i++) rows.push(boxRotZ(`Purlin_${i}`, li("roof"), [2.0, 0.04, 0.08], [i, 2, 3.3]));
  for (let i = 0; i < 2; i++) rows.push(box(`Footing_${i}`, li("foundations"), [0.3, 0.3, 0.2], [i * 4, 0, -0.2]));
  rows.push(box("Roof_Sheet", li("roof"), [2.5, 2.2, 0.01], [2, 2, 3.5]));
  return model(rows);
}

function aabbOf(m, layout, e) {
  const p = layout.positions.subarray(e * 3, e * 3 + 3);
  const h = [m.dims[e * 3] / 2, m.dims[e * 3 + 1] / 2, m.dims[e * 3 + 2] / 2];
  return { lo: [p[0] - h[0], p[1] - h[1], p[2] - h[2]], hi: [p[0] + h[0], p[1] + h[1], p[2] + h[2]] };
}
function overlaps(a, b, axes, eps = 1e-6) {
  return axes.every((k) => a.lo[k] < b.hi[k] - eps && b.lo[k] < a.hi[k] - eps);
}
function bounds(m) {
  return modelLayout(m).bounds;
}

test("flatQuaternion: length axis lands on X, thickness on Z, smallest turn wins", () => {
  const m = house();
  for (let e = 0; e < m.count; e++) {
    const q = flatQuaternion(m, e);
    const f = m.frames.subarray(e * 9, e * 9 + 9);
    // Each rotated frame axis lands on a world axis, and the size measured
    // along world X / Y / Z is the length / width / thickness (tied dims may
    // swap, which changes nothing visible).
    const dims = [m.dims[e * 3], m.dims[e * 3 + 1], m.dims[e * 3 + 2]];
    for (let k = 0; k < 3; k++) {
      const axis = rotate(q, [f[k * 3], f[k * 3 + 1], f[k * 3 + 2]]);
      const world = axis.findIndex((c) => Math.abs(Math.abs(c) - 1) < 1e-5);
      assert.ok(world >= 0, `element ${e} axis ${k} -> ${axis} is not world-aligned`);
      assert.ok(Math.abs(dims[k] - dims[world]) <= 0.01 * dims[k] + 1e-6,
        `element ${e} axis ${k} (${dims[k]}) landed on world ${world} (${dims[world]})`);
    }
  }
  // A beam already lying along X keeps its orientation (identity quaternion)
  const beam = 6;
  const qb = flatQuaternion(m, beam);
  assert.ok(Math.abs(qb[3]) > 0.999, `beam quaternion ${qb} should be identity`);
  // A vertical post turns by 90 degrees, no more
  const post = 0;
  const qp = flatQuaternion(m, post);
  assert.ok(Math.abs(Math.abs(qp[3]) - Math.SQRT1_2) < 1e-4, `post quaternion ${qp} should be a quarter turn`);
});

test("modelLayout: identity poses, bounds enclose every element", () => {
  const m = house();
  const lay = modelLayout(m);
  assert.deepEqual([...lay.quats.subarray(0, 4)], [0, 0, 0, 1]);
  assert.ok(Math.abs(lay.positions[2] - 1.5) < 1e-6);
  assert.ok(lay.bounds.min[2] <= -0.4 + 1e-6 && lay.bounds.max[2] >= 3.51 - 1e-6);
  assert.ok(lay.bounds.max[0] >= 10.05 - 1e-6);
});

test("flat: every element lies on the ground, no two footprints overlap, layers form ordered bands", () => {
  const m = house();
  const { flat } = computeLayouts(m, bounds(m));
  const z0 = bounds(m).min[2];
  for (let e = 0; e < m.count; e++) {
    assert.ok(Math.abs(flat.positions[e * 3 + 2] - (z0 + m.dims[e * 3 + 2] / 2)) < 1e-5, `element ${e} on the ground`);
  }
  for (let a = 0; a < m.count; a++) {
    for (let b = a + 1; b < m.count; b++) {
      assert.ok(!overlaps(aabbOf(m, flat, a), aabbOf(m, flat, b), [0, 1]), `footprints ${a} and ${b} overlap`);
    }
  }
  // Bands: foundations above frame above roof (build order, top of the sheet first)
  const bandY = (name) => {
    const ids = [...Array(m.count).keys()].filter((e) => LAYERS[m.layer[e]] === name);
    return { lo: Math.min(...ids.map((e) => aabbOf(m, flat, e).lo[1])), hi: Math.max(...ids.map((e) => aabbOf(m, flat, e).hi[1])) };
  };
  assert.ok(bandY("foundations").lo > bandY("frame").hi);
  assert.ok(bandY("frame").lo > bandY("roof").hi);
  // Centred on the model footprint
  const mb = bounds(m);
  assert.ok(Math.abs((flat.bounds.min[0] + flat.bounds.max[0]) / 2 - (mb.min[0] + mb.max[0]) / 2) < 1e-4);
});

test("stacked: identical elements share a bundle, nothing intersects, bundles rise off the ground", () => {
  const m = house();
  const { stacked } = computeLayouts(m, bounds(m));
  for (let a = 0; a < m.count; a++) {
    for (let b = a + 1; b < m.count; b++) {
      assert.ok(!overlaps(aabbOf(m, stacked, a), aabbOf(m, stacked, b), [0, 1, 2]), `elements ${a} and ${b} intersect`);
    }
  }
  // The six posts form one block: same x, and at least two courses high
  const posts = [0, 1, 2, 3, 4, 5];
  const xs = new Set(posts.map((e) => stacked.positions[e * 3].toFixed(4)));
  assert.equal(xs.size, 1);
  const zs = new Set(posts.map((e) => stacked.positions[e * 3 + 2].toFixed(4)));
  assert.ok(zs.size >= 2, "posts stacked in courses");
  // Every element lies flat: its thickness extent is vertical
  for (let e = 0; e < m.count; e++) {
    const bb = aabbOf(m, stacked, e);
    assert.ok(bb.hi[2] - bb.lo[2] <= m.dims[e * 3 + 2] + 1e-6);
  }
  assert.ok(stacked.bounds.max[2] > bounds(m).min[2] + 0.2);
});

test("layoutSteps: progress climbs to 1 and the generator returns the layouts", () => {
  const rows = [];
  for (let i = 0; i < 600; i++) rows.push(box(`Stud_${i}`, li("frame"), [0.045, 0.02, 1.2], [i * 0.6, 0, 1.2]));
  const m = model(rows);
  const steps = layoutSteps(m, bounds(m));
  const seen = [];
  let r = steps.next();
  while (!r.done) { seen.push(r.value); r = steps.next(); }
  assert.ok(seen.length >= 3);
  for (let i = 1; i < seen.length; i++) assert.ok(seen[i] >= seen[i - 1]);
  assert.equal(seen[seen.length - 1], 1);
  assert.ok(r.value.flat && r.value.stacked && r.value.model);
  assert.equal(r.value.flat.quats.length, 600 * 4);
});

test("transitionDelays: leaving the model starts at the roof, returning starts at the foundations", () => {
  const m = house();
  const out = transitionDelays(m, "model", "flat");
  const back = transitionDelays(m, "flat", "model");
  const roof = 10, footing = 13;
  assert.ok(out[roof] < out[footing]);
  assert.ok(back[footing] < back[roof]);
  for (const d of [...out, ...back]) assert.ok(d >= 0 && d <= 1);
  const grid = transitionDelays(m, "flat", "stacked");
  assert.equal(grid[0], 0);
  assert.equal(grid[m.count - 1], 1);
});

test("transitionDelays: stacks build from the bottom course and come apart from the top", () => {
  const m = house();
  const { flat, stacked } = computeLayouts(m, bounds(m));
  const posts = [0, 1, 2, 3, 4, 5]; // one bundle, several courses
  const z = (e) => stacked.positions[e * 3 + 2];
  for (const [fromName, from] of [["model", null], ["flat", flat]]) {
    const d = transitionDelays(m, fromName, "stacked", from, stacked);
    for (const a of posts) for (const b of posts) {
      if (z(a) < z(b) - 1e-6) assert.ok(d[a] < d[b], `${fromName}->stacked: lower post ${a} before ${b}`);
    }
  }
  const leave = transitionDelays(m, "stacked", "flat", stacked, flat);
  for (const a of posts) for (const b of posts) {
    if (z(a) > z(b) + 1e-6) assert.ok(leave[a] < leave[b], `stacked->flat: upper post ${a} before ${b}`);
  }
});

test("bands: one per layer in build order, enclosing their elements", () => {
  const m = house();
  const { flat, stacked } = computeLayouts(m, bounds(m));
  for (const lay of [flat, stacked]) {
    assert.deepEqual(lay.bands.map((b) => LAYERS[b.layer]), ["foundations", "frame", "roof"]);
    assert.equal(lay.bands.reduce((s, b) => s + b.count, 0), m.count);
    for (const b of lay.bands) {
      for (const e of b.ids) {
        const bb = aabbOf(m, lay, e);
        for (let k = 0; k < 3; k++) {
          assert.ok(bb.lo[k] >= b.min[k] - 1e-6 && bb.hi[k] <= b.max[k] + 1e-6);
        }
      }
    }
    const frame = lay.bands[1];
    assert.ok(Math.abs(frame.maxLen - 4.8) < 1e-4 && Math.abs(frame.minLen - 3.0) < 1e-4);
  }
});

test("interpolateLayout: matches the endpoints, lifts in between", () => {
  const m = house();
  const { flat, stacked } = computeLayouts(m, bounds(m));
  const delays = transitionDelays(m, "flat", "stacked");
  const opts = { stagger: 0.6, lift: 2 };
  const at0 = interpolateLayout(flat, stacked, delays, 0, opts);
  const at1 = interpolateLayout(flat, stacked, delays, 1, opts);
  for (let i = 0; i < flat.positions.length; i++) {
    assert.ok(Math.abs(at0.positions[i] - flat.positions[i]) < 1e-6);
    assert.ok(Math.abs(at1.positions[i] - stacked.positions[i]) < 1e-6);
  }
  const e = 0;
  const u = elementProgress(0.5, delays[e], 0.6);
  const mid = interpolateLayout(flat, stacked, delays, 0.5, opts);
  const expectZ = flat.positions[e * 3 + 2] * (1 - u) + stacked.positions[e * 3 + 2] * u + 2 * Math.sin(Math.PI * u);
  assert.ok(Math.abs(mid.positions[e * 3 + 2] - expectZ) < 1e-6);
  const ub = unionBounds(flat.bounds, stacked.bounds);
  assert.deepEqual(mid.bounds, ub);
});

test("elementProgress: clamps and eases", () => {
  assert.equal(elementProgress(0, 0.5, 0.6), 0);
  assert.equal(elementProgress(1, 0.5, 0.6), 1);
  assert.equal(elementProgress(1, 1, 0.6), 1);
  const half = elementProgress(0.7, 0.5, 0.6); // u = (0.7 - 0.3) / 0.4 = 1
  assert.equal(half, 1);
});
