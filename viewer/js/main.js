// CraftBot viewer entry point: wiring, model loading, GUI, render loop.

import * as THREE from "three";
import { parseModel, computeStats, matchElements, LAYERS } from "./model-data.js";
import { buildModelGroup } from "./scene.js";
import { makeViews, VIEWS } from "./views.js";
import { makePanel, makeTable, fmtBytes, isMobile } from "./gui.js";
import { makeStyles, STYLES } from "./styles.js";
import { makeAnimations, ANIMS, ORDERS } from "./animations.js";
import { makeSections } from "./sections.js";
import { makePicking, makeInspector } from "./picking.js";
import { makeViewCube } from "./viewcube.js";
import { makeDocPanel } from "./rationale.js";
import { makeCallouts } from "./callouts.js";

// Always revalidate data files (304 when unchanged): local http.server and
// GitHub Pages both let the browser serve stale JSON otherwise.
export const FETCH_OPTS = { cache: "no-cache" };

const canvas = document.getElementById("view");
const banner = document.getElementById("banner");

const renderer = new THREE.WebGLRenderer({
  canvas, antialias: true, powerPreference: "high-performance",
});
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.localClippingEnabled = true;

const scene = new THREE.Scene();
scene.background = new THREE.Color(0xffffff);

const hemi = new THREE.HemisphereLight(0xffffff, 0x666a70, 1.1);
hemi.position.set(0, 0, 1);
scene.add(hemi);
const dir = new THREE.DirectionalLight(0xffffff, 1.6);
dir.position.set(3, -2, 6);
scene.add(dir);

const views = makeViews(renderer, canvas);
const anims = makeAnimations();
const sections = makeSections();

let sceneApi = null;
let currentModel = null;
let currentStyle = "mono";
let inspector = null;
let selected = null;
const layerVisible = LAYERS.map(() => true);

const styles = makeStyles(renderer, scene, {
  onMaterials: (mats) => {
    for (const m of mats) anims.patchMaterial(m);
    sections.refresh();
    if (selected !== null && sceneApi) sceneApi.setSelected(selected, styles.selectColor);
    picking.refreshHover();
    if (inspector) inspector.refresh();
  },
  onTheme: (theme) => {
    viewCube.setTheme(theme);
    if (inspector) inspector.setTheme(theme);
    cutSwatches.set(styles.cutColors, styles.cutIndex);
  },
});

const picking = makePicking(canvas, (x, y) => views.pickCamera(x, y), () => sceneApi,
  () => styles, (eid) => {
    if (!inspector) return;
    selected = eid;
    if (eid === null) {
      inspector.hide();
      if (sceneApi) sceneApi.setSelected(null);
    } else {
      inspector.show(eid);
      if (sceneApi) sceneApi.setSelected(eid, styles.selectColor);
    }
  }, { getModel: () => currentModel, getClipPlanes: () => sections.activePlanes() });
window.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && inspector) {
    inspector.hide();
    selected = null;
    if (sceneApi) sceneApi.setSelected(null);
  }
});

const viewCube = makeViewCube(views);

function showError(msg) {
  banner.textContent = msg;
  banner.hidden = false;
}
window.addEventListener("error", (e) => showError(`Error: ${e.message}`));
window.addEventListener("unhandledrejection", (e) => showError(`Error: ${e.reason}`));

let loadSeq = 0; // the iteration slider can fire faster than fetches land

// keepView: another iteration of the same model - keep the camera, keep the
// unchanged elements in place (only changed ones animate in) and carry the
// selection over if its element survived.
async function loadModel(file, { keepView = false } = {}) {
  const seq = ++loadSeq;
  try {
    const res = await fetch(file, FETCH_OPTS);
    if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
    const json = await res.json();
    if (seq !== loadSeq) return; // a newer load superseded this one
    const model = parseModel(json);
    let kept = null;
    let carried = null;
    if (keepView && currentModel) {
      const map = matchElements(currentModel, model);
      kept = new Uint8Array(model.count);
      for (let e = 0; e < model.count; e++) {
        if (map[e] < 0) continue;
        kept[e] = 1;
        if (map[e] === selected) carried = e;
      }
    }
    if (sceneApi) sceneApi.dispose();
    currentModel = model;
    selected = null;
    sceneApi = buildModelGroup(model);
    sceneApi.setOutlineResolution(canvas.clientWidth, canvas.clientHeight);
    for (let li = 0; li < LAYERS.length; li++) sceneApi.setLayerVisible(li, layerVisible[li]);
    scene.add(sceneApi.group);
    const sphere = sceneApi.bounds.getBoundingSphere(new THREE.Sphere());
    styles.setSceneRadius(sphere.radius);
    styles.apply(currentStyle, sceneApi, model);
    sections.refresh(sceneApi, sceneApi.bounds);
    anims.play(model, sceneApi, { kept });
    picking.resetAfterModelChange();
    if (inspector) inspector.destroy();
    inspector = makeInspector(model, styles.theme,
      { getSceneApi: () => sceneApi, styles, renderer, mainCanvas: canvas });
    if (carried !== null) {
      selected = carried;
      inspector.show(carried);
      sceneApi.setSelected(carried, styles.selectColor);
    }
    views.fit(sceneApi.bounds, { keepView });
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

const panel = makePanel(document.getElementById("gui"), undefined, { exclusive: isMobile() });
const secModel = panel.section("MODEL");
const secStyle = panel.section("STYLE");
const secLayers = panel.section("LAYERS", true, "layers");


// Clicking the active style again advances its mode (mono/wireframe) or
// re-seeds the palette (random).
const styleButtons = secStyle.addButtons(STYLES, (name) => {
  const advance = name === currentStyle;
  currentStyle = name;
  styles.apply(name, sceneApi, currentModel, { advance });
}, { radio: true, active: currentStyle });

const secAnim = panel.section("ANIMATION", false);
const animRow = secAnim.addRow();
const selAnim = secAnim.addStepper("Entry", ANIMS, (v) => anims.setAnim(v), animRow);
const selOrder = secAnim.addStepper("Order", ORDERS, (v) => anims.setOrder(v), animRow);
secAnim.addButtons(["replay"], () => {
  if (currentModel) anims.play(currentModel, sceneApi);
});

const secSection = panel.section("SECTION", false);
const cutToggles = [];
for (let axis = 0; axis < 3; axis++) {
  const name = ["X", "Y", "Z"][axis];
  const cutRow = secSection.addRow(); // toggle and slider share one line
  cutToggles.push(secSection.addToggle(`cut ${name}`, false,
    (on) => sections.set(axis, { enabled: on }), cutRow));
  secSection.addSlider(null, 0, 1, 1, (t) => {
    sections.set(axis, { t, enabled: true });
    cutToggles[axis].set(true);
  }, { host: cutRow });
}
secSection.addButtons(["flip x", "flip y", "flip z", "reset"], (label) => {
  if (label === "reset") { sections.reset(); return; }
  const axis = { "flip x": 0, "flip y": 1, "flip z": 2 }[label];
  sections.set(axis, { flip: !sections.getState(axis).flip });
});
// Cut-face colour: the style's highlight, black or white. Each style mode
// starts on its own (styles.js), so the row is re-read on every theme change.
const cutSwatches = secSection.addSwatches("color", styles.cutColors,
  (i) => styles.setCut(i), styles.cutIndex);

let index = null;
const pick = { exp: null, agent: null, v: null };
let loadedExp = null; // experiment of the model currently in the scene

function currentRuns() {
  return index?.experiments.find((e) => e.id === pick.exp)?.runs ?? [];
}
function currentVersions() {
  return currentRuns().find((r) => r.agent === pick.agent)?.versions ?? [];
}
function currentRun() {
  return currentRuns().find((r) => r.agent === pick.agent) ?? null;
}
function currentEntry() {
  return currentVersions().find((x) => x.v === pick.v) ?? null;
}
const last = (arr) => arr[arr.length - 1];

const selExp = secModel.addSelect("Model", [], (v) => {
  pick.exp = v;
  pick.agent = last(currentRuns())?.agent ?? null;
  refreshPickers({ newest: true });
  loadPicked();
});
const selAgent = secModel.addSelect("Agent", [], (v) => {
  pick.agent = v;
  refreshPickers({ newest: true });
  loadPicked();
});
// Iterations as a slider: 1..n over the versions of the picked run
const iterSlider = secModel.addSlider("Iteration", 1, 1, 1, (i) => {
  pick.v = currentVersions()[i - 1]?.v ?? pick.v;
  loadPicked();
}, { step: 1, readout: (i) => currentVersions()[i - 1]?.v ?? "" });
const modelInfo = secModel.addInfo();
// Rationale callouts: shown only while this is on. Expanding the DESIGN
// RATIONALE panel switches it off (the panel covers the model on phones).
const calloutToggle = secModel.addToggle("callouts", false, (on) => callouts.setVisible(on));

// newest: land on the last iteration of the picked run. Switching model or
// agent always does - without it a run that happens to have the same version
// name (v03 -> v03) would keep the old slider position instead of the newest.
function refreshPickers({ newest = false } = {}) {
  selExp.setOptions(index.experiments.map((e) => ({ value: e.id, label: e.title })), pick.exp);
  selAgent.setOptions(currentRuns().map((r) => ({ value: r.agent, label: r.agent })), pick.agent);
  const versions = currentVersions();
  if (newest || !versions.some((x) => x.v === pick.v)) pick.v = last(versions)?.v ?? null;
  iterSlider.setRange(1, Math.max(versions.length, 1));
  iterSlider.set(versions.findIndex((x) => x.v === pick.v) + 1);
}

function loadPicked() {
  const entry = currentEntry();
  if (!entry) return;
  modelInfo.set(`<b>${entry.elements}</b> elements &middot; <b>${fmtBytes(entry.bytes)}</b>`);
  loadRunDocs(currentRun());
  loadModel(`models/${entry.file}`, { keepView: loadedExp === pick.exp });
  loadedExp = pick.exp;
}

// Rationale document + its callouts for a run (Fable runs only)
let docSeq = 0;
async function loadRunDocs(run) {
  const seq = ++docSeq;
  let data = null;
  if (run?.callouts) {
    try {
      const res = await fetch(`models/${run.callouts}`, FETCH_OPTS);
      if (res.ok) data = await res.json();
    } catch (err) {
      console.warn(`callouts: ${run.callouts}: ${err.message}`);
    }
  }
  if (seq !== docSeq) return; // another run was picked meanwhile
  callouts.setData(data);
  docPanel.show(run?.rationale ? `models/${run.rationale}` : null, data);
}

// LAYERS section - visibility only; the takeoff numbers live in #stats
LAYERS.forEach((name, li) =>
  secLayers.addToggle(name, true, (on) => {
    layerVisible[li] = on;
    if (sceneApi) sceneApi.setLayerVisible(li, on);
    refreshStats();
  }));

// Always-visible material takeoff, top of the screen next to the panel
const statsTable = makeTable(document.getElementById("stats"),
  ["layer", "n", "len m", "m³", "kg"]);
const docPanel = makeDocPanel(document.body);
const callouts = makeCallouts(document.body, {
  views, canvas, getSceneApi: () => sceneApi, getStyles: () => styles, docPanel,
});
docPanel.onExpand(() => {
  calloutToggle.set(false);
  callouts.setVisible(false);
});
docPanel.onSectionHover((section) => callouts.highlightSection(section));
document.addEventListener("craftbot:model", (ev) => callouts.setModel(ev.detail.model));

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
  if (sceneApi) sceneApi.setOutlineResolution(canvas.clientWidth, canvas.clientHeight);
}
new ResizeObserver(resize).observe(canvas);

const clock = new THREE.Clock();
renderer.setAnimationLoop(() => {
  anims.tick(Math.min(clock.getDelta(), 0.1));
  if (sceneApi) sceneApi.setCapsPaused(anims.playing);
  views.tick();
  picking.tick();
  callouts.tick();
  views.render(styles.render);
  viewCube.render();
  if (inspector) inspector.render(clock.elapsedTime);
});
resize();

const SHOWCASE = ["02", "03", "04", "06", "07", "08", "09", "11"];
const bootParams = new URLSearchParams(location.search);
const requested = bootParams.get("model");
if (STYLES.includes(bootParams.get("style"))) {
  currentStyle = bootParams.get("style");
  styleButtons.setActive(currentStyle);
}
// Testing: ?open=ANIMATION,SECTION expands GUI sections
for (const name of (bootParams.get("open") || "").split(",").filter(Boolean)) panel.open(name);
// Testing: ?mode=1 picks the second variant of a two-mode style
const modeParam = parseInt(bootParams.get("mode"), 10);
if (ANIMS.includes(bootParams.get("anim"))) {
  anims.setAnim(bootParams.get("anim"));
  selAnim.set(anims.anim);
}
if (ORDERS.includes(bootParams.get("order"))) {
  anims.setOrder(bootParams.get("order"));
  selOrder.set(anims.order);
}
const viewParam = bootParams.get("view");
if (VIEWS.includes(viewParam)) {
  document.addEventListener("craftbot:model", () => {
    if (viewParam === "quad") {
      views.setQuad(true);
      viewCube.setQuadActive(true);
    } else {
      views.setPreset(viewParam);
    }
  });
}
if (!Number.isNaN(modeParam) && modeParam > 0) {
  document.addEventListener("craftbot:model", () => {
    for (let i = 0; i < modeParam; i++) {
      styles.apply(currentStyle, sceneApi, currentModel, { advance: true });
    }
  });
}
// Testing: ?cut=axis,t e.g. cut=1,0.5 sections the model on load
const cutParam = (bootParams.get("cut") || "").split(",");
if (cutParam.length === 2) {
  document.addEventListener("craftbot:model", () =>
    sections.set(parseInt(cutParam[0], 10), { t: parseFloat(cutParam[1]), enabled: true }));
}
// Testing: ?select=elementId opens the inspector on load
const selectParam = parseInt(bootParams.get("select"), 10);
if (!Number.isNaN(selectParam)) {
  document.addEventListener("craftbot:model", () => {
    selected = selectParam;
    inspector.show(selectParam);
    sceneApi.setSelected(selectParam, styles.selectColor);
  });
}
// Testing: ?callouts=1 switches the rationale callouts on after load,
// ?pin=calloutId then clicks that tag open
if (bootParams.get("callouts") === "1") {
  document.addEventListener("craftbot:model", () => {
    calloutToggle.set(true);
    callouts.setVisible(true);
    // the click has to land after the rationale document itself
    const pin = bootParams.get("pin");
    if (pin) setTimeout(() =>
      document.querySelector(`.callout[data-callout="${CSS.escape(pin)}"]`)?.click(), 300);
  }, { once: true });
}
// Testing: ?hover=elementId shows the hover tag at the canvas centre
const hoverParam = parseInt(bootParams.get("hover"), 10);
if (!Number.isNaN(hoverParam)) {
  document.addEventListener("craftbot:model", () =>
    picking.debugHover(hoverParam, canvas.clientWidth / 2, canvas.clientHeight / 2));
}
const freezeAt = parseFloat(bootParams.get("freeze"));
if (!Number.isNaN(freezeAt)) {
  document.addEventListener("craftbot:model", () => anims.freeze(freezeAt));
}
fetch("models/index.json", FETCH_OPTS)
  .then((r) => r.json())
  .then((idx) => {
    index = idx;
    // Resolve the requested file back to picker state, else newest of the last agent
    let found = null;
    for (const e of idx.experiments) {
      for (const r of e.runs) {
        for (const x of r.versions) {
          if (requested && `models/${x.file}` === requested) found = { e, r, x };
        }
      }
    }
    // No ?model: open a random Fable showcase at its final iteration
    const showcase = idx.experiments.filter((exp) =>
      SHOWCASE.includes(exp.id.slice(0, 2)) && exp.runs.some((run) => run.agent === "Fable"));
    const e = found?.e ?? showcase[Math.floor(Math.random() * showcase.length)] ?? idx.experiments[0];
    const r = found?.r ?? e.runs.find((run) => run.agent === "Fable") ?? last(e.runs);
    const x = found?.x ?? last(r.versions);
    pick.exp = e.id; pick.agent = r.agent; pick.v = x.v;
    refreshPickers();
    loadPicked();
  })
  .catch((e) => {
    showError(`Failed to load models/index.json: ${e.message}`);
    if (requested) loadModel(requested);
  });

export { renderer, scene, views, loadModel };
export function getSceneApi() { return sceneApi; }
export function getModel() { return currentModel; }
