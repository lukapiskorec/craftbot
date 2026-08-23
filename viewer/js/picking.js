// Hover highlight + element selection. Selection opens an inspector panel:
// an inset viewport with the isolated element auto-rotating, dimension lines
// with DOM labels, and the element's numbers.

import * as THREE from "three";
import { LAYERS, TIMBER_DENSITY } from "./model-data.js";

const HIGHLIGHT = new THREE.Color(0x33ff66);

export function makePicking(canvas, getCamera, getSceneApi, getModel, onSelect) {
  const raycaster = new THREE.Raycaster();
  const pointer = new THREE.Vector2();
  let hovered = null;
  let queued = null;

  function pick(ev) {
    const api = getSceneApi();
    if (!api) return null;
    const rect = canvas.getBoundingClientRect();
    pointer.x = ((ev.clientX - rect.left) / rect.width) * 2 - 1;
    pointer.y = -((ev.clientY - rect.top) / rect.height) * 2 + 1;
    raycaster.setFromCamera(pointer, getCamera());
    const hits = raycaster.intersectObjects(api.pickables(), false);
    return hits.length ? api.elementOf(hits[0]) : null;
  }

  function setHover(eid) {
    const api = getSceneApi();
    if (!api || eid === hovered) return;
    if (hovered !== null) api.highlight(hovered, null);
    hovered = eid;
    if (eid !== null) {
      api.highlight(eid, HIGHLIGHT);
      canvas.style.cursor = "pointer";
    } else {
      canvas.style.cursor = "";
    }
  }

  // Raycast at most once per frame
  canvas.addEventListener("pointermove", (ev) => {
    queued = ev;
  });
  function tick() {
    if (queued) {
      setHover(pick(queued));
      queued = null;
    }
  }

  let downAt = null;
  canvas.addEventListener("pointerdown", (ev) => { downAt = [ev.clientX, ev.clientY]; });
  canvas.addEventListener("pointerup", (ev) => {
    if (!downAt) return;
    const moved = Math.hypot(ev.clientX - downAt[0], ev.clientY - downAt[1]);
    downAt = null;
    if (moved > 4) return; // was an orbit drag
    onSelect(pick(ev));
  });

  return {
    tick,
    clearHover() { setHover(null); },
    resetAfterModelChange() { hovered = null; },
  };
}

// ------------------------------------------------------------------
// Element inspector
// ------------------------------------------------------------------

export function makeInspector(model) {
  let root = document.getElementById("inspector");
  if (root) root.remove();
  root = document.createElement("div");
  root.id = "inspector";
  root.hidden = true;
  root.innerHTML = `<h3></h3><div class="dims"></div><canvas width="276" height="200"></canvas>`;
  document.body.appendChild(root);

  const canvas = root.querySelector("canvas");
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x0e120e);
  scene.add(new THREE.HemisphereLight(0xffffff, 0x445544, 1.2));
  const dl = new THREE.DirectionalLight(0xffffff, 1.4);
  dl.position.set(2, -3, 4);
  scene.add(dl);
  const camera = new THREE.PerspectiveCamera(35, 276 / 200, 0.01, 100);
  camera.up.set(0, 0, 1);

  let group = null;
  let labels = [];
  let dimAnchors = []; // {mid: Vector3, text: string}
  let active = false;

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
    }
    clearLabels();
  }

  function buildGeometry(eid) {
    const isBox = model.kinds[eid] === 0;
    if (isBox) {
      const d = [model.dims[eid * 3], model.dims[eid * 3 + 1], model.dims[eid * 3 + 2]];
      return { geom: new THREE.BoxGeometry(d[0], d[1], d[2]), dims: d };
    }
    const mm = model.meshes.find((m) => m.elementId === eid);
    const geom = new THREE.BufferGeometry();
    const verts = new Float32Array(mm.verts.length);
    for (let i = 0; i < mm.verts.length; i += 3) {
      verts[i] = mm.verts[i] - model.centers[eid * 3];
      verts[i + 1] = mm.verts[i + 1] - model.centers[eid * 3 + 1];
      verts[i + 2] = mm.verts[i + 2] - model.centers[eid * 3 + 2];
    }
    geom.setAttribute("position", new THREE.BufferAttribute(verts, 3));
    geom.setIndex(new THREE.BufferAttribute(mm.index, 1));
    geom.computeVertexNormals();
    return {
      geom,
      dims: [model.dims[eid * 3], model.dims[eid * 3 + 1], model.dims[eid * 3 + 2]],
    };
  }

  function addDimLines(dims) {
    // Dimension lines just outside the AABB, one per axis, with tick marks.
    const [dx, dy, dz] = dims;
    const h = [dx / 2, dy / 2, dz / 2];
    const off = Math.max(dx, dy, dz) * 0.18;
    const pts = [];
    const axes = [
      { text: dx, a: [-h[0], h[1] + off, -h[2]], b: [h[0], h[1] + off, -h[2]], tick: [0, off * 0.2, 0] },
      { text: dy, a: [h[0] + off, -h[1], -h[2]], b: [h[0] + off, h[1], -h[2]], tick: [off * 0.2, 0, 0] },
      { text: dz, a: [h[0] + off, h[1], -h[2]], b: [h[0] + off, h[1], h[2]], tick: [off * 0.2, 0, 0] },
    ];
    for (const ax of axes) {
      pts.push(...ax.a, ...ax.b);
      for (const end of [ax.a, ax.b]) {
        pts.push(end[0] - ax.tick[0], end[1] - ax.tick[1], end[2] - ax.tick[2],
          end[0] + ax.tick[0], end[1] + ax.tick[1], end[2] + ax.tick[2]);
      }
      const mid = new THREE.Vector3(
        (ax.a[0] + ax.b[0]) / 2, (ax.a[1] + ax.b[1]) / 2, (ax.a[2] + ax.b[2]) / 2);
      dimAnchors.push({ mid, text: `${ax.text.toFixed(2)} m` });
    }
    const geom = new THREE.BufferGeometry();
    geom.setAttribute("position", new THREE.BufferAttribute(Float32Array.from(pts), 3));
    const lines = new THREE.LineSegments(geom,
      new THREE.LineBasicMaterial({ color: 0x33ff66 }));
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
      dispose();
      const { geom, dims } = buildGeometry(eid);
      group = new THREE.Group();
      const mesh = new THREE.Mesh(geom, new THREE.MeshStandardMaterial({
        color: 0xe8e4dc, roughness: 0.9,
      }));
      group.add(mesh);
      group.add(new THREE.LineSegments(new THREE.EdgesGeometry(geom, 10),
        new THREE.LineBasicMaterial({ color: 0x234a2e })));
      addDimLines(dims);
      scene.add(group);

      const radius = Math.max(dims[0], dims[1], dims[2]) * 0.9 + 0.01;
      camera.position.set(radius * 2.2, -radius * 2.2, radius * 1.6);
      camera.lookAt(0, 0, 0);

      const [dx, dy, dz] = dims;
      const vol = model.volumes[eid];
      root.querySelector("h3").textContent = model.names[eid];
      root.querySelector(".dims").innerHTML =
        `layer <b>${LAYERS[model.layer[eid]]}</b><br>` +
        `size <b>${dx.toFixed(2)} × ${dy.toFixed(2)} × ${dz.toFixed(2)} m</b><br>` +
        `volume <b>${vol.toFixed(3)} m³</b> · weight <b>${(vol * TIMBER_DENSITY).toFixed(1)} kg</b>`;
      root.hidden = false;
      active = true;
    },

    hide() {
      root.hidden = true;
      active = false;
      dispose();
    },

    render(t) {
      if (!active || !group) return;
      group.rotation.z = t * 0.5;
      renderer.render(scene, camera);
      // Project dimension labels to screen space
      const rect = canvas.getBoundingClientRect();
      const v = new THREE.Vector3();
      for (let i = 0; i < dimAnchors.length; i++) {
        v.copy(dimAnchors[i].mid).applyAxisAngle(new THREE.Vector3(0, 0, 1), group.rotation.z);
        v.project(camera);
        labels[i].style.left = `${rect.left + (v.x * 0.5 + 0.5) * rect.width}px`;
        labels[i].style.top = `${rect.top + (-v.y * 0.5 + 0.5) * rect.height}px`;
        labels[i].style.display = v.z < 1 ? "block" : "none";
      }
    },

    destroy() {
      api.hide();
      renderer.dispose();
      root.remove();
    },
  };
  return api;
}
