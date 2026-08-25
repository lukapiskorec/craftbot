// Blender-style navigation cube in the top-right corner. Renders in its own
// small canvas so it never fights the main renderer's viewport/post passes.
//
// Picking: raycast the six face planes, then snap each local axis of the hit
// point to -1 / 0 / +1. That yields all 26 regions - 6 faces, 12 edges, 8
// corners - and the snapped vector IS the view direction to fly to.

import * as THREE from "three";
import { isMobile } from "./gui.js";

const SIZE = isMobile() ? 88 : 118; // css px
const CUBE = 1.7; // cube edge in world units of the widget scene
const SNAP = 0.62; // |coord| above this counts as "on that side"

// normal, up: the up vector fixes which way the label reads. Sides stand on
// world +Z (the scene is Z-up); the caps read along +Y.
const FACES = [
  { label: "RIGHT", normal: [1, 0, 0], up: [0, 0, 1] },
  { label: "LEFT", normal: [-1, 0, 0], up: [0, 0, 1] },
  { label: "BACK", normal: [0, 1, 0], up: [0, 0, 1] },
  { label: "FRONT", normal: [0, -1, 0], up: [0, 0, 1] },
  { label: "TOP", normal: [0, 0, 1], up: [0, 1, 0] },
  { label: "BOTTOM", normal: [0, 0, -1], up: [0, 1, 0] },
];

// Opaque face tile in the page colour, so the cube reads as solid whatever
// the style is.
function labelTexture(text, theme) {
  const c = document.createElement("canvas");
  c.width = c.height = 128;
  const g = c.getContext("2d");
  g.fillStyle = theme.bg;
  g.fillRect(0, 0, 128, 128);
  g.fillStyle = theme.ink;
  g.textAlign = "center";
  g.textBaseline = "middle";
  // A face is only ~40 screen px wide, so size the label to fill the tile -
  // anything smaller turns to mush once the texture is minified.
  let size = 34;
  g.font = `600 ${size}px MEK-Mono, monospace`;
  const maxWidth = 100;
  const w = g.measureText(text).width;
  if (w > maxWidth) {
    size = Math.floor(size * maxWidth / w);
    g.font = `600 ${size}px MEK-Mono, monospace`;
  }
  g.fillText(text, 64, 67);
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.minFilter = THREE.LinearFilter; // no mipmaps: keeps the label crisp
  tex.generateMipmaps = false;
  tex.anisotropy = 4;
  return tex;
}

// Orient a face plane: local X -> right, Y -> up, Z -> outward normal.
function orientFace(mesh, normal, up) {
  const n = new THREE.Vector3(...normal);
  const u = new THREE.Vector3(...up);
  const right = new THREE.Vector3().crossVectors(u, n);
  mesh.matrixAutoUpdate = false;
  mesh.matrix.makeBasis(right, u, n);
  mesh.matrix.setPosition(n.clone().multiplyScalar(CUBE / 2));
}

export function makeViewCube(views, onQuadToggle) {
  const root = document.createElement("div");
  root.id = "viewcube";
  const canvas = document.createElement("canvas");
  canvas.width = canvas.height = SIZE * Math.min(window.devicePixelRatio, 2);
  canvas.style.width = canvas.style.height = `${SIZE}px`;
  root.appendChild(canvas);
  const quadBtn = document.createElement("button");
  quadBtn.className = "quad-btn";
  quadBtn.textContent = "4-view";
  quadBtn.style.width = `${SIZE}px`;
  quadBtn.addEventListener("click", () => {
    const on = !views.quad;
    views.setQuad(on);
    quadBtn.classList.toggle("active", on);
    if (onQuadToggle) onQuadToggle(on);
  });
  root.appendChild(quadBtn);
  document.body.appendChild(root);

  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(SIZE, SIZE, false);

  const scene = new THREE.Scene();
  const camera = new THREE.OrthographicCamera(-1.7, 1.7, 1.7, -1.7, 0.1, 20);
  camera.up.set(0, 0, 1);

  const rig = new THREE.Group(); // holds the cube, rotated to mirror the main view
  scene.add(rig);

  const faceMaterials = FACES.map(() => new THREE.MeshBasicMaterial());
  const faces = FACES.map((f, i) => {
    const m = new THREE.Mesh(new THREE.PlaneGeometry(CUBE, CUBE), faceMaterials[i]);
    orientFace(m, f.normal, f.up);
    rig.add(m);
    return m;
  });

  const edges = new THREE.LineSegments(
    new THREE.EdgesGeometry(new THREE.BoxGeometry(CUBE, CUBE, CUBE)),
    new THREE.LineBasicMaterial({ color: 0x000000 }));
  rig.add(edges);

  // Highlight blob shown over the hovered face / edge / corner
  const marker = new THREE.Mesh(
    new THREE.SphereGeometry(0.26, 16, 12),
    new THREE.MeshBasicMaterial());
  marker.visible = false;
  rig.add(marker);

  const raycaster = new THREE.Raycaster();
  const pointer = new THREE.Vector2();
  const hovered = new THREE.Vector3();
  let hasHover = false;
  let dragging = false;
  let dragged = false;
  let last = null;

  function setTheme(t) {
    for (let i = 0; i < faceMaterials.length; i++) {
      if (faceMaterials[i].map) faceMaterials[i].map.dispose();
      faceMaterials[i].map = labelTexture(FACES[i].label, t);
      faceMaterials[i].needsUpdate = true;
    }
    edges.material.color.set(t.ink);
    marker.material.color.set(t.accent);
  }

  // Local-space hit point -> snapped view direction (-1/0/1 per axis)
  function snap(point) {
    const t = SNAP * (CUBE / 2);
    const v = new THREE.Vector3(
      Math.abs(point.x) > t ? Math.sign(point.x) : 0,
      Math.abs(point.y) > t ? Math.sign(point.y) : 0,
      Math.abs(point.z) > t ? Math.sign(point.z) : 0);
    return v.lengthSq() === 0 ? null : v;
  }

  function pickAt(ev) {
    const rect = canvas.getBoundingClientRect();
    pointer.x = ((ev.clientX - rect.left) / rect.width) * 2 - 1;
    pointer.y = -((ev.clientY - rect.top) / rect.height) * 2 + 1;
    raycaster.setFromCamera(pointer, camera);
    const hits = raycaster.intersectObjects(faces, false);
    if (!hits.length) return null;
    return snap(rig.worldToLocal(hits[0].point.clone()));
  }

  canvas.addEventListener("pointermove", (ev) => {
    if (dragging) {
      const dx = ev.clientX - last[0];
      const dy = ev.clientY - last[1];
      if (Math.hypot(dx, dy) > 0) dragged = true;
      views.orbitBy(dx * 0.012, dy * 0.012);
      last = [ev.clientX, ev.clientY];
      return;
    }
    const dir = pickAt(ev);
    hasHover = dir !== null;
    if (dir) hovered.copy(dir);
    canvas.style.cursor = dir ? "pointer" : "grab";
  });
  canvas.addEventListener("pointerleave", () => { hasHover = false; });
  canvas.addEventListener("pointerdown", (ev) => {
    dragging = true;
    dragged = false;
    last = [ev.clientX, ev.clientY];
    canvas.setPointerCapture(ev.pointerId);
  });
  canvas.addEventListener("pointerup", (ev) => {
    dragging = false;
    canvas.releasePointerCapture(ev.pointerId);
    if (dragged) return;
    const dir = pickAt(ev);
    if (dir) {
      views.setQuad(false);
      quadBtn.classList.remove("active");
      views.flyTo(dir);
    }
  });

  const camDir = new THREE.Vector3();
  const api = {
    el: root,
    setTheme,
    setQuadActive(on) { quadBtn.classList.toggle("active", on); },

    render() {
      // Mirror the main camera: place the cube camera on the same direction
      views.getDirection(camDir);
      camera.position.copy(camDir).multiplyScalar(6);
      camera.up.set(0, 0, 1);
      if (Math.abs(camDir.z) > 0.999) camera.up.set(0, 1, 0);
      camera.lookAt(0, 0, 0);
      marker.visible = hasHover;
      if (hasHover) marker.position.copy(hovered).multiplyScalar(CUBE / 2);
      renderer.render(scene, camera);
    },

    dispose() {
      renderer.dispose();
      root.remove();
    },
  };
  return api;
}
