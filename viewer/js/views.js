// Orthographic camera rig. Scene is Z-up (camera.up = +Z).
// Presets: top / front / side / axo, plus a 4-viewport quad mode
// (top, front, side fixed; axo interactive).

import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";

export const VIEWS = ["top", "front", "side", "axo", "quad"];

const DIRS = {
  top: { offset: [0, 0, 1], up: [0, 1, 0] },
  front: { offset: [0, -1, 0], up: [0, 0, 1] },
  side: { offset: [1, 0, 0], up: [0, 0, 1] },
  axo: { offset: [1, -1, 0.8], up: [0, 0, 1] },
};

export function makeViews(renderer, canvas) {
  const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.01, 1000);
  camera.up.set(0, 0, 1);
  const controls = new OrbitControls(camera, canvas);
  controls.enableDamping = true;
  controls.dampingFactor = 0.12;

  // Fixed cameras for the quad view (top-left, bottom-left, bottom-right)
  const fixedCams = {
    top: new THREE.OrthographicCamera(-1, 1, 1, -1, 0.01, 1000),
    front: new THREE.OrthographicCamera(-1, 1, 1, -1, 0.01, 1000),
    side: new THREE.OrthographicCamera(-1, 1, 1, -1, 0.01, 1000),
  };

  let radius = 10;
  let center = new THREE.Vector3();
  let quad = false;
  const quadLines = document.getElementById("quad-lines");

  function frustum(cam, w, h) {
    const aspect = w / h;
    const half = radius * 1.2;
    cam.left = -half * Math.max(aspect, 1);
    cam.right = half * Math.max(aspect, 1);
    cam.top = half * Math.max(1 / aspect, 1);
    cam.bottom = -half * Math.max(1 / aspect, 1);
    cam.near = 0.01;
    cam.far = radius * 40;
    cam.updateProjectionMatrix();
  }

  function place(cam, name) {
    const d = DIRS[name];
    const dir = new THREE.Vector3(...d.offset).normalize();
    cam.up.set(...d.up);
    cam.position.copy(center).addScaledVector(dir, radius * 4);
    cam.lookAt(center);
  }

  function updateFrustums() {
    const w = canvas.clientWidth || 1;
    const h = canvas.clientHeight || 1;
    frustum(camera, w, h);
    for (const cam of Object.values(fixedCams)) frustum(cam, w, h);
  }

  const api = {
    camera, controls,
    get quad() { return quad; },

    fit(bounds) {
      const sphere = bounds.getBoundingSphere(new THREE.Sphere());
      radius = Math.max(sphere.radius, 0.001);
      center = sphere.center.clone();
      controls.target.copy(center);
      api.setPreset("axo");
      for (const name of Object.keys(fixedCams)) place(fixedCams[name], name);
      updateFrustums();
    },

    setPreset(name) {
      place(camera, name);
      camera.zoom = 1;
      camera.updateProjectionMatrix();
      controls.target.copy(center);
      controls.update();
    },

    setQuad(on) {
      quad = on;
      if (quadLines) quadLines.classList.toggle("on", on);
      if (on) {
        api.setPreset("axo"); // interactive quadrant shows axo
        for (const name of Object.keys(fixedCams)) place(fixedCams[name], name);
      }
    },

    // styleRender(camera, viewportDevicePx|null)
    render(styleRender) {
      if (!quad) {
        styleRender(camera, null);
        return;
      }
      const size = renderer.getDrawingBufferSize(new THREE.Vector2());
      const w = Math.floor(size.x / 2);
      const h = Math.floor(size.y / 2);
      styleRender(fixedCams.top, { x: 0, y: h, w, h });               // top-left
      styleRender(camera, { x: w, y: h, w: size.x - w, h });          // top-right: axo
      styleRender(fixedCams.front, { x: 0, y: 0, w, h });             // bottom-left
      styleRender(fixedCams.side, { x: w, y: 0, w: size.x - w, h });  // bottom-right
    },

    onResize() { updateFrustums(); },

    tick() { controls.update(); },
  };
  return api;
}
