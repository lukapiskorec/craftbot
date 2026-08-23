// CraftBot viewer entry point: wiring, model loading, render loop.

import * as THREE from "three";
import { parseModel } from "./model-data.js";
import { buildModelGroup } from "./scene.js";
import { makeViews } from "./views.js";

const canvas = document.getElementById("view");
const banner = document.getElementById("banner");

const renderer = new THREE.WebGLRenderer({
  canvas, antialias: true, powerPreference: "high-performance",
});
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.localClippingEnabled = true;

const scene = new THREE.Scene();
scene.background = new THREE.Color(0xdfe6ea);

const hemi = new THREE.HemisphereLight(0xffffff, 0x666a70, 1.1);
hemi.position.set(0, 0, 1);
scene.add(hemi);
const dir = new THREE.DirectionalLight(0xffffff, 1.6);
dir.position.set(3, -2, 6);
scene.add(dir);

const grid = new THREE.GridHelper(40, 40, 0x8899aa, 0xb8c4cc);
grid.rotation.x = Math.PI / 2; // XY ground plane (Z-up scene)
scene.add(grid);

const views = makeViews(renderer, canvas);

let sceneApi = null;
let currentModel = null;

function showError(msg) {
  banner.textContent = msg;
  banner.hidden = false;
}

export async function loadModel(file) {
  try {
    const res = await fetch(file);
    if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
    const json = await res.json();
    const model = parseModel(json);
    if (sceneApi) sceneApi.dispose();
    currentModel = model;
    sceneApi = buildModelGroup(model);
    scene.add(sceneApi.group);
    views.fit(sceneApi.bounds);
    // Ground grid sized/positioned under the model
    const size = sceneApi.bounds.getSize(new THREE.Vector3());
    const span = Math.ceil(Math.max(size.x, size.y) * 1.6) || 10;
    grid.scale.setScalar(span / 40);
    grid.position.set(
      (sceneApi.bounds.min.x + sceneApi.bounds.max.x) / 2,
      (sceneApi.bounds.min.y + sceneApi.bounds.max.y) / 2,
      sceneApi.bounds.min.z - 0.01,
    );
    banner.hidden = true;
    document.dispatchEvent(new CustomEvent("craftbot:model", {
      detail: { model, sceneApi, file },
    }));
  } catch (err) {
    showError(`Failed to load ${file}: ${err.message}`);
  }
}

function resize() {
  renderer.setSize(canvas.clientWidth, canvas.clientHeight, false);
  views.onResize();
}
new ResizeObserver(resize).observe(canvas);

renderer.setAnimationLoop(() => {
  views.tick();
  renderer.render(scene, views.camera);
});
resize();

// Boot: load model from ?model= or the first index entry
const params = new URLSearchParams(location.search);
const requested = params.get("model");
if (requested) {
  loadModel(requested);
} else {
  fetch("models/index.json")
    .then((r) => r.json())
    .then((idx) => {
      const first = idx.experiments[0].runs[0].versions[0].file;
      loadModel(`models/${first}`);
    })
    .catch((e) => showError(`Failed to load models/index.json: ${e.message}`));
}

export { renderer, scene, views, grid };
export function getSceneApi() { return sceneApi; }
export function getModel() { return currentModel; }
