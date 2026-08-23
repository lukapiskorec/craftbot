import test from "node:test";
import assert from "node:assert/strict";
import {
  classifyLayer, parseModel, computeStats, computeSpawnTimes,
  LAYERS, TIMBER_DENSITY,
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

test("parseModel: counts, dims, volumes", () => {
  const m = parseModel(M);
  assert.equal(m.count, 3);
  assert.equal(m.boxes.elementIds.length, 2);
  assert.equal(m.meshes.length, 1);
  const d0 = [m.dims[0], m.dims[1], m.dims[2]];
  assert.ok(Math.abs(d0[0] - 0.1) < 1e-4 && Math.abs(d0[2] - 3.0) < 1e-4);
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
