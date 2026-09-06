// Hover highlight (tint + name/layer tag at the cursor) and element
// selection. Selection opens an inspector panel:
// the isolated element auto-rotating in a viewport of the main canvas (so it
// is drawn by the active style, AO/dither included), dimension lines with
// DOM labels, and the element's numbers.

import * as THREE from "three";
import { LAYERS, TIMBER_DENSITY } from "./model-data.js";

// getPickCamera(clientX, clientY) -> {camera, x, y} (NDC in that camera's viewport)
// getModel() -> parsed model (names/layers for the hover tag)
// getClipPlanes() -> active section planes; hits on their clipped side are skipped
export function makePicking(canvas, getPickCamera, getSceneApi, getStyles, onSelect,
  { getModel, getClipPlanes }) {
  const raycaster = new THREE.Raycaster();
  const pointer = new THREE.Vector2();
  let hovered = null;
  let queued = null;
  let enabled = true; // off while the elements are in flight (raycasts hit the model pose)
  // Elements settled in a grid (knolling.js layout): every one is an
  // axis-aligned box of its own dims at positions[e], picked by slab test
  let arranged = null;

  function pickArranged(api, planes) {
    const model = getModel();
    const o = raycaster.ray.origin, d = raycaster.ray.direction;
    const oc = [o.x, o.y, o.z], dc = [d.x, d.y, d.z];
    let best = Infinity, hit = null;
    for (let e = 0; e < model.count; e++) {
      if (!api.buckets[model.layer[e]].layerGroup.visible) continue;
      let tmin = -Infinity, tmax = Infinity;
      for (let k = 0; k < 3 && tmin <= tmax; k++) {
        const c = arranged.positions[e * 3 + k], h = model.dims[e * 3 + k] / 2;
        if (Math.abs(dc[k]) < 1e-9) {
          if (oc[k] < c - h || oc[k] > c + h) tmin = Infinity;
          continue;
        }
        let t1 = (c - h - oc[k]) / dc[k], t2 = (c + h - oc[k]) / dc[k];
        if (t1 > t2) { const s = t1; t1 = t2; t2 = s; }
        if (t1 > tmin) tmin = t1;
        if (t2 < tmax) tmax = t2;
      }
      if (tmin > tmax || tmax < 0 || tmin >= best) continue;
      const p = o.clone().addScaledVector(d, tmin);
      if (planes.every((pl) => pl.distanceToPoint(p) >= 0)) { best = tmin; hit = e; }
    }
    return hit;
  }

  // Name + layer next to the cursor while an element is hovered
  const tag = document.createElement("div");
  tag.id = "hover-tag";
  tag.hidden = true;
  document.body.appendChild(tag);

  function placeTag(ev) {
    const pad = 16;
    const w = tag.offsetWidth, h = tag.offsetHeight;
    const x = ev.clientX + pad + w > window.innerWidth ? ev.clientX - pad - w : ev.clientX + pad;
    const y = ev.clientY + pad + h > window.innerHeight ? ev.clientY - pad - h : ev.clientY + pad;
    tag.style.left = `${x}px`;
    tag.style.top = `${y}px`;
  }

  function pick(ev) {
    const api = getSceneApi();
    if (!api) return null;
    const { camera, x, y } = getPickCamera(ev.clientX, ev.clientY);
    pointer.set(x, y);
    raycaster.setFromCamera(pointer, camera);
    const planes = getClipPlanes();
    if (arranged) return pickArranged(api, planes);
    const hits = raycaster.intersectObjects(api.pickables(), false);
    // Nearest hit that is not cut away by a section plane
    for (const hit of hits) {
      if (planes.every((p) => p.distanceToPoint(hit.point) >= 0)) return api.elementOf(hit);
    }
    return null;
  }

  function setHover(eid) {
    const api = getSceneApi();
    if (!api || eid === hovered) return;
    if (hovered !== null) api.highlight(hovered, null);
    hovered = eid;
    if (eid !== null) {
      api.highlight(eid, getStyles().hoverColor);
      canvas.style.cursor = "pointer";
      const model = getModel();
      const name = document.createElement("b");
      name.textContent = model.names[eid];
      tag.replaceChildren(name, document.createElement("br"), LAYERS[model.layer[eid]]);
      tag.hidden = false;
    } else {
      canvas.style.cursor = "";
      tag.hidden = true;
    }
  }

  // Raycast at most once per frame
  canvas.addEventListener("pointermove", (ev) => {
    queued = ev;
  });
  canvas.addEventListener("pointerleave", () => {
    queued = null;
    setHover(null);
  });
  function tick() {
    if (queued && !enabled) queued = null;
    if (queued) {
      setHover(pick(queued));
      if (hovered !== null) placeTag(queued);
      queued = null;
    }
  }

  let downAt = null;
  canvas.addEventListener("pointerdown", (ev) => { downAt = [ev.clientX, ev.clientY]; });
  canvas.addEventListener("pointerup", (ev) => {
    if (!downAt) return;
    const moved = Math.hypot(ev.clientX - downAt[0], ev.clientY - downAt[1]);
    downAt = null;
    if (moved > 4 || !enabled) return; // was an orbit drag, or elements are knolled
    onSelect(pick(ev));
  });

  return {
    tick,
    clearHover() { setHover(null); },
    setEnabled(on) {
      enabled = on;
      if (!on) { queued = null; setHover(null); }
    },
    // layout ({positions} per element) while the elements sit in a grid, null otherwise
    setArranged(layout) { arranged = layout; },
    resetAfterModelChange() { hovered = null; tag.hidden = true; },
    // Testing: ?hover=eid - hover an element with the tag at a client position
    debugHover(eid, clientX, clientY) { setHover(eid); placeTag({ clientX, clientY }); },
    // Re-tint the hovered element after a style change
    refreshHover() {
      const eid = hovered;
      hovered = null;
      setHover(eid);
    },
  };
}

// ------------------------------------------------------------------
// Element inspector
// ------------------------------------------------------------------

// The style materials carry the entry-animation vertex patch, which reads
// these attributes; a spawn time in the far past keeps the element static.
function addAnimAttributes(geom) {
  const n = geom.getAttribute("position").count;
  geom.setAttribute("aSpawn", new THREE.BufferAttribute(new Float32Array(n).fill(-1e9), 1));
  geom.setAttribute("aCenter", new THREE.BufferAttribute(new Float32Array(n * 3), 3));
  return geom;
}

const fmt = (m) => `${m.toFixed(3)} m`;

// deps: getSceneApi() -> model scene api (materials, base colours),
//       styles (render pipeline), renderer + mainCanvas (viewport placement)
export function makeInspector(model, theme, { getSceneApi, styles, renderer, mainCanvas }) {
  let root = document.getElementById("inspector");
  if (root) root.remove();
  root = document.createElement("div");
  root.id = "inspector";
  root.hidden = true;
  root.innerHTML = `<div class="text"><h3></h3><div class="dims"></div></div>
<div class="viewport"></div>`;
  document.body.appendChild(root);
  const viewport = root.querySelector(".viewport");

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(theme.bg);
  // Same rig as the main scene so shading matches
  const hemi = new THREE.HemisphereLight(0xffffff, 0x666a70, 1.1);
  hemi.position.set(0, 0, 1);
  scene.add(hemi);
  const dl = new THREE.DirectionalLight(0xffffff, 1.6);
  dl.position.set(3, -2, 6);
  scene.add(dl);
  const camera = new THREE.PerspectiveCamera(35, 276 / 200, 0.01, 100);
  camera.up.set(0, 0, 1);

  let group = null;
  let edges = null;
  let labels = [];
  let dimAnchors = []; // {mid: Vector3, text: string}
  let active = false;
  let currentEid = null;
  let ownMaterials = []; // unclipped copies of the style materials
  let radius = 1;

  function clearLabels() {
    for (const l of labels) l.remove();
    labels = [];
    dimAnchors = [];
  }

  function dispose() {
    if (group) {
      group.traverse((o) => o.geometry && o.geometry.dispose());
      scene.remove(group);
      group = null;
      edges = null;
    }
    for (const m of ownMaterials) m.dispose();
    ownMaterials = [];
    clearLabels();
  }

  // The inspector draws the element re-centred on the origin, where the
  // world-space section planes would clip it at random (and cut it away
  // entirely for half of the slider). So it renders with copies of the style
  // materials that carry no clipping planes.
  function unclipped(mat) {
    const copy = mat.clone();
    copy.onBeforeCompile = mat.onBeforeCompile; // clone() drops the animation patch
    copy.customProgramCacheKey = mat.customProgramCacheKey;
    copy.clippingPlanes = null;
    ownMaterials.push(copy);
    return copy;
  }

  // Geometry in the element's own frame: longest axis along X, centred.
  function buildGeometry(eid) {
    const d = [model.dims[eid * 3], model.dims[eid * 3 + 1], model.dims[eid * 3 + 2]];
    let geom;
    if (model.kinds[eid] === 0) {
      geom = new THREE.BoxGeometry(d[0], d[1], d[2]);
    } else {
      const mm = model.meshes.find((m) => m.elementId === eid);
      const f = model.frames.subarray(eid * 9, eid * 9 + 9);
      const c = model.centers.subarray(eid * 3, eid * 3 + 3);
      const verts = new Float32Array(mm.verts.length);
      for (let i = 0; i < mm.verts.length; i += 3) {
        const x = mm.verts[i] - c[0], y = mm.verts[i + 1] - c[1], z = mm.verts[i + 2] - c[2];
        for (let k = 0; k < 3; k++) {
          verts[i + k] = x * f[k * 3] + y * f[k * 3 + 1] + z * f[k * 3 + 2];
        }
      }
      geom = new THREE.BufferGeometry();
      geom.setAttribute("position", new THREE.BufferAttribute(verts, 3));
      geom.setIndex(new THREE.BufferAttribute(mm.index, 1));
      geom.computeVertexNormals();
    }
    const n = geom.getAttribute("position").count;
    const color = getSceneApi().baseColor(eid);
    const col = new Float32Array(n * 3);
    for (let i = 0; i < n; i++) { col[i * 3] = color.r; col[i * 3 + 1] = color.g; col[i * 3 + 2] = color.b; }
    geom.setAttribute("color", new THREE.BufferAttribute(col, 3));
    return { geom: addAnimAttributes(geom), dims: d };
  }

  function addDimLines(dims) {
    // Dimension lines just outside the box, one per axis, with tick marks.
    const [dx, dy, dz] = dims;
    const h = [dx / 2, dy / 2, dz / 2];
    const off = Math.max(dx, dy, dz) * 0.18;
    const pts = [];
    const axes = [
      { text: dx, a: [-h[0], h[1] + off, -h[2]], b: [h[0], h[1] + off, -h[2]], tick: [0, off * 0.2, 0] },
      { text: dy, a: [h[0] + off, -h[1], -h[2]], b: [h[0] + off, h[1], -h[2]], tick: [off * 0.2, 0, 0] },
      { text: dz, a: [-h[0] - off, -h[1], -h[2]], b: [-h[0] - off, -h[1], h[2]], tick: [off * 0.2, 0, 0] },
    ];
    for (const ax of axes) {
      pts.push(...ax.a, ...ax.b);
      for (const end of [ax.a, ax.b]) {
        pts.push(end[0] - ax.tick[0], end[1] - ax.tick[1], end[2] - ax.tick[2],
          end[0] + ax.tick[0], end[1] + ax.tick[1], end[2] + ax.tick[2]);
      }
      const mid = new THREE.Vector3(
        (ax.a[0] + ax.b[0]) / 2, (ax.a[1] + ax.b[1]) / 2, (ax.a[2] + ax.b[2]) / 2);
      dimAnchors.push({ mid, text: fmt(ax.text) });
    }
    const geom = new THREE.BufferGeometry();
    geom.setAttribute("position", new THREE.BufferAttribute(Float32Array.from(pts), 3));
    const lines = new THREE.LineSegments(geom,
      new THREE.LineBasicMaterial({ color: theme.accent }));
    lines.name = "dims";
    group.add(lines);
    for (const anchor of dimAnchors) {
      const el = document.createElement("div");
      el.className = "dim-label";
      el.textContent = anchor.text;
      document.body.appendChild(el);
      labels.push(el);
    }
  }

  const api = {
    show(eid) {
      const rotation = group ? group.rotation.z : 0;
      dispose();
      currentEid = eid;
      const { geom, dims } = buildGeometry(eid);
      const mats = getSceneApi().materials;
      group = new THREE.Group();
      group.rotation.z = rotation;
      group.add(new THREE.Mesh(geom, unclipped(model.isGlass[eid] ? mats.glass : mats.fill)));
      edges = new THREE.LineSegments(
        addAnimAttributes(new THREE.EdgesGeometry(geom, 10)), unclipped(mats.line));
      edges.visible = styles.edgesVisible;
      group.add(edges);
      addDimLines(dims);
      scene.add(group);

      radius = Math.max(dims[0], dims[1], dims[2]) * 0.55 + 0.01;
      camera.position.set(radius * 2.0, -radius * 2.0, radius * 1.4);
      camera.lookAt(0, 0, 0);

      const [dx, dy, dz] = dims;
      const vol = model.volumes[eid];
      root.querySelector("h3").textContent = model.names[eid];
      root.querySelector(".dims").innerHTML =
        `layer <b>${LAYERS[model.layer[eid]]}</b><br>` +
        `size <b>${dx.toFixed(3)} × ${dy.toFixed(3)} × ${dz.toFixed(3)} m</b><br>` +
        `volume <b>${vol.toFixed(3)} m³</b> · weight <b>${(vol * TIMBER_DENSITY).toFixed(1)} kg</b>`;
      root.hidden = false;
      active = true;
    },

    hide() {
      root.hidden = true;
      active = false;
      currentEid = null;
      dispose();
    },

    // Re-pick materials and colour after a style change
    refresh() {
      if (active && currentEid !== null) api.show(currentEid);
    },

    render(t) {
      if (!active || !group) return;
      group.rotation.z = t * 0.5;
      const rect = viewport.getBoundingClientRect();
      const main = mainCanvas.getBoundingClientRect();
      if (rect.width < 1 || rect.height < 1) return;
      const pr = renderer.getPixelRatio();
      camera.aspect = rect.width / rect.height;
      camera.updateProjectionMatrix();
      // GL viewport origin is bottom-left
      styles.render(camera, {
        x: Math.round((rect.left - main.left) * pr),
        y: Math.round((main.bottom - rect.bottom) * pr),
        w: Math.round(rect.width * pr),
        h: Math.round(rect.height * pr),
      }, { scene, radius });
      // Project dimension labels to screen space
      const v = new THREE.Vector3();
      for (let i = 0; i < dimAnchors.length; i++) {
        v.copy(dimAnchors[i].mid).applyAxisAngle(new THREE.Vector3(0, 0, 1), group.rotation.z);
        v.project(camera);
        labels[i].style.left = `${rect.left + (v.x * 0.5 + 0.5) * rect.width}px`;
        labels[i].style.top = `${rect.top + (-v.y * 0.5 + 0.5) * rect.height}px`;
        labels[i].style.display = v.z < 1 ? "block" : "none";
      }
    },

    // Follow the active style without rebuilding the panel
    setTheme(t) {
      theme = t;
      scene.background = new THREE.Color(t.bg);
      const dims = group?.getObjectByName("dims");
      if (dims) dims.material.color.set(t.accent);
    },

    destroy() {
      api.hide();
      root.remove();
    },
  };
  return api;
}
