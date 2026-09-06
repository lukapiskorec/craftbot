import test from "node:test";
import assert from "node:assert/strict";
import { buildCaps, boxCrossings, meshCrossings, orderPolygon }
  from "../js/section-caps.js";

// Column-major 4x4 for a box of size sx,sy,sz centred at c (the unit cube is
// 2x2x2, so the scale is half the size).
function boxMatrix([sx, sy, sz], [cx, cy, cz] = [0, 0, 0]) {
  return [sx / 2, 0, 0, 0, 0, sy / 2, 0, 0, 0, 0, sz / 2, 0, cx, cy, cz, 1];
}

// One box element, as parseModel would hand it over
function boxModel(size, center = [0, 0, 0]) {
  return {
    dims: Float32Array.from(size),
    centers: Float32Array.from(center),
    boxes: { elementIds: Uint32Array.from([0]), matrices: Float32Array.from(boxMatrix(size, center)) },
    meshes: [],
  };
}

// Same box as a triangulated mesh element
function meshBox(size, center = [0, 0, 0]) {
  const [hx, hy, hz] = size.map((s) => s / 2);
  const verts = [];
  for (const sz of [-1, 1]) for (const sy of [-1, 1]) for (const sx of [-1, 1]) {
    verts.push(center[0] + sx * hx, center[1] + sy * hy, center[2] + sz * hz);
  }
  // faces of the 000..111 corner order above
  const quads = [[0, 1, 3, 2], [4, 6, 7, 5], [0, 4, 5, 1], [2, 3, 7, 6],
    [0, 2, 6, 4], [1, 5, 7, 3]];
  const index = [];
  for (const [a, b, c, d] of quads) index.push(a, b, c, a, c, d);
  return {
    dims: Float32Array.from(size),
    centers: Float32Array.from(center),
    boxes: { elementIds: new Uint32Array(0), matrices: new Float32Array(0) },
    meshes: [{ elementId: 0, verts: Float32Array.from(verts), index: Uint32Array.from(index) }],
  };
}

// Total area of a triangle soup
function area(tris) {
  let sum = 0;
  for (let i = 0; i < tris.length; i += 9) {
    const ux = tris[i + 3] - tris[i], uy = tris[i + 4] - tris[i + 1], uz = tris[i + 5] - tris[i + 2];
    const vx = tris[i + 6] - tris[i], vy = tris[i + 7] - tris[i + 1], vz = tris[i + 8] - tris[i + 2];
    sum += 0.5 * Math.hypot(uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx);
  }
  return sum;
}

const onPlane = (tris, pl) => tris.every((_, i) => i % 3 ||
  Math.abs(pl[0] * tris[i] + pl[1] * tris[i + 1] + pl[2] * tris[i + 2] + pl[3]) < 1e-6);

test("a box cut across its length caps with its cross section", () => {
  const model = boxModel([4, 0.2, 0.4]);
  const tris = buildCaps(model, [[-1, 0, 0, 0]]); // keep x <= 0, cut at x = 0
  assert.equal(tris.length, 18); // a quad, two triangles
  assert.ok(Math.abs(area(tris) - 0.2 * 0.4) < 1e-6);
  assert.ok(onPlane(tris, [-1, 0, 0, 0]));
});

test("the cap of a mesh element matches the cap of the same box", () => {
  const plane = [0, 0, -1, 0.05];
  const fromBox = buildCaps(boxModel([2, 0.5, 1], [0.3, -0.2, 0]), [plane]);
  const fromMesh = buildCaps(meshBox([2, 0.5, 1], [0.3, -0.2, 0]), [plane]);
  assert.ok(fromBox.length > 0 && fromMesh.length > 0);
  assert.ok(Math.abs(area(fromBox) - area(fromMesh)) < 1e-6);
  assert.ok(Math.abs(area(fromBox) - 2 * 0.5) < 1e-6);
});

test("a diagonal cut caps the full slanted section", () => {
  const s = Math.SQRT1_2;
  const plane = [-s, 0, -s, 0]; // 45 degrees through the origin
  const tris = buildCaps(boxModel([1, 1, 1]), [plane]);
  // The diagonal section of a unit cube through its centre is 1 x sqrt(2)
  assert.ok(Math.abs(area(tris) - Math.SQRT2) < 1e-5);
  assert.ok(onPlane(tris, plane));
});

test("a second plane clips the cap of the first", () => {
  const model = boxModel([2, 2, 0.5]);
  const one = buildCaps(model, [[-1, 0, 0, 0]]);
  const two = buildCaps(model, [[-1, 0, 0, 0], [0, -1, 0, 0]]);
  assert.ok(Math.abs(area(one) - 2 * 0.5) < 1e-6);
  // Each plane now caps half of its own section, so the total is unchanged
  assert.ok(Math.abs(area(two) - 2 * (0.5 * 2 * 0.5)) < 1e-6);
});

test("elements the plane misses cap nothing", () => {
  assert.equal(buildCaps(boxModel([1, 1, 1], [10, 0, 0]), [[-1, 0, 0, 0]]).length, 0);
  assert.equal(buildCaps(meshBox([1, 1, 1], [0, 0, 5]), [[0, 0, -1, 0]]).length, 0);
});

test("hidden layers cap nothing", () => {
  const model = boxModel([2, 1, 1]);
  assert.equal(buildCaps(model, [[-1, 0, 0, 0]], () => false).length, 0);
  assert.ok(buildCaps(model, [[-1, 0, 0, 0]], () => true).length > 0);
});

test("a plane through a corner does not produce a degenerate polygon", () => {
  const s = 1 / Math.sqrt(3);
  const pts = [];
  boxCrossings(Float32Array.from(boxMatrix([2, 2, 2])), 0, [-s, -s, -s, 3 * s], pts);
  // The corner (1,1,1) is touched by three edges: one point after ordering
  assert.equal(orderPolygon(pts, [-s, -s, -s, 3 * s]).length, 3);
});

test("crossings land on the plane and on the element", () => {
  const plane = [0, -1, 0, 0.1];
  const pts = [];
  const m = meshBox([1, 2, 3]);
  meshCrossings(m.meshes[0].verts, m.meshes[0].index, plane, pts);
  assert.ok(pts.length >= 12);
  for (let i = 0; i < pts.length; i += 3) {
    assert.ok(Math.abs(-pts[i + 1] + 0.1) < 1e-6);
    assert.ok(Math.abs(pts[i]) <= 0.5 + 1e-6 && Math.abs(pts[i + 2]) <= 1.5 + 1e-6);
  }
});
