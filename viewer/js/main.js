// CraftBot viewer entry point: wiring, model loading, GUI, render loop.

import * as THREE from "three";
import { parseModel, computeStats, LAYERS, LAYER_COLORS } from "./model-data.js";
import { buildModelGroup } from "./scene.js";
import { makeViews } from "./views.js";
import { makePanel, fmtBytes } from "./gui.js";
import { makeStyles, STYLES } from "./styles.js";
import { makeAnimations, ANIMS, ORDERS } from "./animations.js";

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
const anims = makeAnimations();
const styles = makeStyles(renderer, scene, grid, {
  onMaterials: (fill, line) => {
    anims.patchMaterial(fill);
    anims.patchMaterial(line);
  },
});

let sceneApi = null;
let currentModel = null;
let currentStyle = "solid";
const layerVisible = LAYERS.map(() => true);

function showError(msg) {
  banner.textContent = msg;
  banner.hidden = false;
}

async function loadModel(file) {
  try {
    const res = await fetch(file);
    if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
    const json = await res.json();
    const model = parseModel(json);
    if (sceneApi) sceneApi.dispose();
    currentModel = model;
    sceneApi = buildModelGroup(model);
    for (let li = 0; li < LAYERS.length; li++) sceneApi.setLayerVisible(li, layerVisible[li]);
    scene.add(sceneApi.group);
    styles.apply(currentStyle, sceneApi, model);
    anims.play(model, sceneApi);
    views.fit(sceneApi.bounds);
    const size = sceneApi.bounds.getSize(new THREE.Vector3());
    const span = Math.ceil(Math.max(size.x, size.y) * 1.6) || 10;
    grid.scale.setScalar(span / 40);
    grid.position.set(
      (sceneApi.bounds.min.x + sceneApi.bounds.max.x) / 2,
      (sceneApi.bounds.min.y + sceneApi.bounds.max.y) / 2,
      sceneApi.bounds.min.z - 0.01,
    );
    banner.hidden = true;
    const url = new URL(location);
    url.searchParams.set("model", file);
    history.replaceState(null, "", url);
    document.dispatchEvent(new CustomEvent("craftbot:model", {
      detail: { model, sceneApi, file },
    }));
  } catch (err) {
    showError(`Failed to load ${file}: ${err.message}`);
  }
}

// ------------------------------------------------------------------
// GUI
// ------------------------------------------------------------------

const panel = makePanel(document.getElementById("gui"));
const secModel = panel.section("MODEL");
const secStyle = panel.section("STYLE");
const secLayers = panel.section("LAYERS");

const styleButtons = secStyle.addButtons(STYLES, (name) => {
  currentStyle = name;
  if (sceneApi) styles.apply(name, sceneApi, currentModel);
}, { radio: true, active: currentStyle });

const secAnim = panel.section("ANIMATION");
const selAnim = secAnim.addSelect("Entry", ANIMS.map((a) => ({ value: a, label: a })),
  (v) => anims.setAnim(v));
const selOrder = secAnim.addSelect("Order", ORDERS.map((o) => ({ value: o, label: o })),
  (v) => anims.setOrder(v));
secAnim.addButtons(["replay"], () => {
  if (currentModel) anims.play(currentModel, sceneApi);
});

let index = null;
const pick = { exp: null, agent: null, v: null };

function currentRuns() {
  return index.experiments.find((e) => e.id === pick.exp)?.runs ?? [];
}
function currentVersions() {
  return currentRuns().find((r) => r.agent === pick.agent)?.versions ?? [];
}
function currentEntry() {
  return currentVersions().find((x) => x.v === pick.v) ?? null;
}

const selExp = secModel.addSelect("Model", [], (v) => {
  pick.exp = v;
  pick.agent = currentRuns()[0]?.agent ?? null;
  refreshPickers();
  loadPicked();
});
const selAgent = secModel.addSelect("Agent", [], (v) => {
  pick.agent = v;
  refreshPickers();
  loadPicked();
});
const selVersion = secModel.addSelect("Version", [], (v) => {
  pick.v = v;
  loadPicked();
});
const modelInfo = secModel.addInfo();

function refreshPickers() {
  selExp.setOptions(index.experiments.map((e) => ({ value: e.id, label: e.title })), pick.exp);
  selAgent.setOptions(currentRuns().map((r) => ({ value: r.agent, label: r.agent })), pick.agent);
  const versions = currentVersions();
  if (!versions.some((x) => x.v === pick.v)) pick.v = versions[versions.length - 1]?.v ?? null;
  selVersion.setOptions(versions.map((x) => ({ value: x.v, label: x.v })), pick.v);
}

function loadPicked() {
  const entry = currentEntry();
  if (!entry) return;
  modelInfo.set(`<b>${entry.elements}</b> elements &middot; <b>${fmtBytes(entry.bytes)}</b>`);
  loadModel(`models/${entry.file}`);
}

// LAYERS section
const layerToggles = LAYERS.map((name, li) =>
  secLayers.addToggle(name, true, (on) => {
    layerVisible[li] = on;
    if (sceneApi) sceneApi.setLayerVisible(li, on);
    refreshStats();
  }, `#${LAYER_COLORS[li].toString(16).padStart(6, "0")}`),
);
const statsTable = secLayers.addTable(["layer", "n", "len m", "m³", "kg"]);

function refreshStats() {
  if (!currentModel) return;
  const rows = computeStats(currentModel, layerVisible);
  const shown = rows.filter((r) => r.count > 0);
  const total = shown.reduce((a, r) => ({
    count: a.count + r.count, lengthM: a.lengthM + r.lengthM,
    volumeM3: a.volumeM3 + r.volumeM3, weightKg: a.weightKg + r.weightKg,
  }), { count: 0, lengthM: 0, volumeM3: 0, weightKg: 0 });
  statsTable.set([
    ...shown.map((r) => ({
      cells: [r.layer, r.count, r.lengthM.toFixed(1), r.volumeM3.toFixed(2),
        r.weightKg.toFixed(0)],
    })),
    { cells: ["total", total.count, total.lengthM.toFixed(1),
      total.volumeM3.toFixed(2), total.weightKg.toFixed(0)], total: true },
  ]);
}

document.addEventListener("craftbot:model", refreshStats);

// ------------------------------------------------------------------
// Render loop + boot
// ------------------------------------------------------------------

function resize() {
  renderer.setSize(canvas.clientWidth, canvas.clientHeight, false);
  views.onResize();
}
new ResizeObserver(resize).observe(canvas);

const clock = new THREE.Clock();
renderer.setAnimationLoop(() => {
  anims.tick(Math.min(clock.getDelta(), 0.1));
  views.tick();
  styles.render(views.camera);
});
resize();

const bootParams = new URLSearchParams(location.search);
const requested = bootParams.get("model");
if (STYLES.includes(bootParams.get("style"))) {
  currentStyle = bootParams.get("style");
  styleButtons.setActive(currentStyle);
}
if (ANIMS.includes(bootParams.get("anim"))) {
  anims.setAnim(bootParams.get("anim"));
  selAnim.set(anims.anim);
}
if (ORDERS.includes(bootParams.get("order"))) {
  anims.setOrder(bootParams.get("order"));
  selOrder.set(anims.order);
}
const freezeAt = parseFloat(bootParams.get("freeze"));
if (!Number.isNaN(freezeAt)) {
  document.addEventListener("craftbot:model", () => anims.freeze(freezeAt));
}
fetch("models/index.json")
  .then((r) => r.json())
  .then((idx) => {
    index = idx;
    // Resolve the requested file back to picker state, else first entry
    let found = null;
    for (const e of idx.experiments) {
      for (const r of e.runs) {
        for (const x of r.versions) {
          if (requested && `models/${x.file}` === requested) found = { e, r, x };
        }
      }
    }
    const e = found?.e ?? idx.experiments[0];
    const r = found?.r ?? e.runs[0];
    const x = found?.x ?? r.versions[r.versions.length - 1];
    pick.exp = e.id; pick.agent = r.agent; pick.v = x.v;
    refreshPickers();
    loadPicked();
  })
  .catch((e) => {
    showError(`Failed to load models/index.json: ${e.message}`);
    if (requested) loadModel(requested);
  });

export { renderer, scene, views, grid, loadModel };
export function getSceneApi() { return sceneApi; }
export function getModel() { return currentModel; }
