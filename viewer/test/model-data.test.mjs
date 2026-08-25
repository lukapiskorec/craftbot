import test from "node:test";
import assert from "node:assert/strict";
import {
  classifyLayer, classifyGlass, parseModel, computeStats, computeSpawnTimes,
  orientedBox, LAYERS, TIMBER_DENSITY,
} from "../js/model-data.js";

const M = {
  format: "craftbot-model", version: 1, source: "s",
  collections: ["", "Timber_Framing/Posts"],
  boxes: [
    ["Post_01", 1, 0.05, 0, 0, 0, 0, 0.05, 0, 0, 0, 0, 1.5, 1.5], // 0.1x0.1x3.0 post
    ["Roof_Beam_01", 0, 1, 0, 0, 0, 0, 0.1, 0, 0, 0, 0, 0.1, 3.2],
  ],
  meshes: [
    {
      name: "Footing_01", collection: 0,
      verts: [0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1],
      faces: [[0, 3, 2, 1], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]],
    },
  ],
};

test("classifyLayer: collection wins over name", () => {
  assert.equal(LAYERS[classifyLayer("Roof_Beam_01", "Timber_Framing/Posts")], "frame");
});

test("classifyLayer: name keywords", () => {
  assert.equal(LAYERS[classifyLayer("Roof_Beam_01", "")], "roof");
  assert.equal(LAYERS[classifyLayer("Footing_01", "")], "foundations");
  assert.equal(LAYERS[classifyLayer("Mystery_01", "")], "other");
});

test("classifyGlass: only glazing, not the timber around an opening", () => {
  assert.equal(classifyGlass("Glass_S_L1_1.35", ""), 1);
  assert.equal(classifyGlass("Window_S0_1_Glass", ""), 1);
  assert.equal(classifyGlass("Pane_04", "Openings/Glazing"), 1);
  assert.equal(classifyGlass("Window_Sill_S", ""), 0);
  assert.equal(classifyGlass("DN1_WindowHeader", "Roof_Framing/RF_Dormers"), 0);
  assert.equal(classifyGlass("Jamb_2", "Facade/FA_Windows"), 0);
  assert.equal(classifyGlass("Post_01", "Timber_Framing/Posts"), 0);
});

test("parseModel: isGlass flags follow element order", () => {
  const m = parseModel({
    ...M,
    collections: ["", "Openings/Glazing"],
    boxes: [["Pane_01", 1, 0.05, 0, 0, 0, 0, 0.05, 0, 0, 0, 0, 1.5, 1.5],
      ["Post_02", 0, 0.05, 0, 0, 0, 0, 0.05, 0, 0, 0, 0, 1.5, 1.5]],
  });
  assert.deepEqual([...m.isGlass], [1, 0, 0]);
});

test("parseModel: counts, dims, volumes", () => {
  const m = parseModel(M);
  assert.equal(m.count, 3);
  assert.equal(m.boxes.elementIds.length, 2);
  assert.equal(m.meshes.length, 1);
  // dims are sorted longest first (length x width x thickness)
  const d0 = [m.dims[0], m.dims[1], m.dims[2]];
  assert.ok(Math.abs(d0[0] - 3.0) < 1e-4 && Math.abs(d0[2] - 0.1) < 1e-4);
  assert.ok(Math.abs(m.volumes[0] - 0.03) < 1e-4);
  assert.ok(Math.abs(m.volumes[2] - 1.0) < 1e-4); // unit cube mesh
  assert.equal(m.meshes[0].index.length, 6 * 2 * 3); // 6 quads fan-triangulated
  assert.ok(Math.abs(m.centers[6] - 0.5) < 1e-4); // mesh center x
});

test("parseModel: instance matrix is column-major with translation last", () => {
  const m = parseModel(M);
  const k = 0; // Post_01
  assert.ok(Math.abs(m.boxes.matrices[k + 0] - 0.05) < 1e-6);
  assert.equal(m.boxes.matrices[k + 12], 0); // tx
  assert.equal(m.boxes.matrices[k + 14], 1.5); // tz
  assert.equal(m.boxes.matrices[k + 15], 1);
});

test("parseModel: rejects unknown format", () => {
  assert.throws(() => parseModel({ format: "nope", version: 1 }));
});

test("computeStats: totals and visibility", () => {
  const m = parseModel(M);
  const all = computeStats(m, [true, true, true, true, true, true]);
  const frame = all.find((r) => r.layer === "frame");
  assert.equal(frame.count, 1);
  assert.ok(Math.abs(frame.lengthM - 3.0) < 1e-3);
  assert.ok(Math.abs(frame.weightKg - 0.03 * TIMBER_DENSITY) < 1e-2);
  const none = computeStats(m, [false, false, false, false, false, false]);
  assert.equal(none.reduce((s, r) => s + r.count, 0), 0);
});

test("computeSpawnTimes: sequence is monotonic, ends at 80% of duration", () => {
  const m = parseModel(M);
  const t = computeSpawnTimes(m, "sequence", 3.0);
  assert.ok(t[0] < t[1] && t[1] < t[2]);
  assert.ok(Math.abs(t[2] - 2.4) < 1e-5);
});

test("computeSpawnTimes: layers mode builds foundations before roof", () => {
  const m = parseModel(M);
  const t = computeSpawnTimes(m, "layers", 3.0);
  // element 2 = Footing (foundations), 1 = Roof_Beam (roof), 0 = Post (frame)
  assert.ok(t[2] < t[0] && t[0] < t[1]);
});

test("elementForFace maps triangles to elements", async () => {
  const { elementForFace } = await import("../js/model-data.js");
  const map = Uint32Array.from([5, 5, 7, 7, 7, 9]);
  assert.equal(elementForFace(map, 0), 5);
  assert.equal(elementForFace(map, 4), 7);
  assert.equal(elementForFace(map, 5), 9);
});

// A 3.0 x 0.2 x 0.1 member rotated 30 deg about Z and tilted 20 deg about Y,
// as a triangulated closed mesh.
function rotatedMember() {
  const L = 3.0, W = 0.2, T = 0.1;
  const corners = [];
  for (const sx of [-1, 1]) for (const sy of [-1, 1]) for (const sz of [-1, 1]) {
    corners.push([sx * L / 2, sy * W / 2, sz * T / 2]);
  }
  const cz = Math.cos(Math.PI / 6), sz = Math.sin(Math.PI / 6);
  const cy = Math.cos(Math.PI / 9), sy = Math.sin(Math.PI / 9);
  const verts = [];
  for (const [x, y, z] of corners) {
    const x1 = x * cy + z * sy, z1 = -x * sy + z * cy; // about Y
    const x2 = x1 * cz - y * sz, y2 = x1 * sz + y * cz; // about Z
    verts.push(x2 + 5, y2 - 2, z1 + 1);
  }
  // corner index = sx*4 + sy*2 + sz (0/1 flags)
  const quads = [
    [0, 1, 3, 2], [4, 6, 7, 5], [0, 4, 5, 1], [2, 3, 7, 6], [0, 2, 6, 4], [1, 5, 7, 3],
  ];
  const index = [];
  for (const q of quads) index.push(q[0], q[1], q[2], q[0], q[2], q[3]);
  return { verts: Float32Array.from(verts), index: Uint32Array.from(index) };
}

test("orientedBox: recovers true member size and centre of a rotated box", () => {
  const { verts, index } = rotatedMember();
  const ob = orientedBox(verts, index);
  assert.ok(Math.abs(ob.dims[0] - 3.0) < 1e-3, `L ${ob.dims[0]}`);
  assert.ok(Math.abs(ob.dims[1] - 0.2) < 1e-3, `W ${ob.dims[1]}`);
  assert.ok(Math.abs(ob.dims[2] - 0.1) < 1e-3, `T ${ob.dims[2]}`);
  assert.ok(Math.abs(ob.center[0] - 5) < 1e-3 && Math.abs(ob.center[1] + 2) < 1e-3
    && Math.abs(ob.center[2] - 1) < 1e-3);
  // axes are unit, right-handed, and axis 0 is the length direction
  const a = ob.axes;
  const dot = (i, j) => a[i * 3] * a[j * 3] + a[i * 3 + 1] * a[j * 3 + 1] + a[i * 3 + 2] * a[j * 3 + 2];
  assert.ok(Math.abs(dot(0, 0) - 1) < 1e-6 && Math.abs(dot(0, 1)) < 1e-6);
  const cross = [a[1] * a[5] - a[2] * a[4], a[2] * a[3] - a[0] * a[5], a[0] * a[4] - a[1] * a[3]];
  assert.ok(Math.abs(cross[0] - a[6]) < 1e-6 && Math.abs(cross[1] - a[7]) < 1e-6
    && Math.abs(cross[2] - a[8]) < 1e-6);
  const expectedLen = [Math.cos(Math.PI / 9) * Math.cos(Math.PI / 6),
    Math.cos(Math.PI / 9) * Math.sin(Math.PI / 6), -Math.sin(Math.PI / 9)];
  const along = Math.abs(a[0] * expectedLen[0] + a[1] * expectedLen[1] + a[2] * expectedLen[2]);
  assert.ok(Math.abs(along - 1) < 1e-4, `axis0 not along member: ${along}`);
});

test("parseModel: mesh dims are oriented, box frames match matrix columns", () => {
  const { verts, index } = rotatedMember();
  const faces = [];
  for (let i = 0; i < index.length; i += 3) faces.push([index[i], index[i + 1], index[i + 2]]);
  const m = parseModel({ ...M, meshes: [{ name: "Rafter_01", collection: 0,
    verts: Array.from(verts), faces }] });
  const e = 2;
  assert.ok(Math.abs(m.dims[e * 3] - 3.0) < 1e-3);
  assert.ok(Math.abs(m.dims[e * 3 + 1] - 0.2) < 1e-3);
  assert.ok(Math.abs(m.centers[e * 3] - 5) < 1e-3);
  // Post_01: 0.1 x 0.1 x 3.0 along world Z -> frame axis 0 is +-Z
  assert.ok(Math.abs(Math.abs(m.frames[2]) - 1) < 1e-6);
  assert.equal(m.frames.length, 9 * m.count);
});
