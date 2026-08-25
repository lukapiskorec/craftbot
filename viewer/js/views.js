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
  // In-flight camera move (view cube click): slerp between orientations so the
  // up vector never flips mid-way. Orbit controls are paused until it lands.
  let fly = null; // {q0, q1, up, dist, t0, dur}
  const FLY_SECONDS = 0.5;

  function endFlight() {
    if (!fly) return;
    camera.quaternion.copy(fly.q1);
    camera.up.copy(fly.up);
    fly = null;
    controls.enabled = true;
    controls.update();
  }

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

    // keepView: re-centre on the new bounds but keep direction and zoom
    // (switching iterations of the same model must not jump the camera).
    fit(bounds, { keepView = false } = {}) {
      endFlight();
      const sphere = bounds.getBoundingSphere(new THREE.Sphere());
      radius = Math.max(sphere.radius, 0.001);
      const dir = api.getDirection(new THREE.Vector3());
      center = sphere.center.clone();
      controls.target.copy(center);
      if (keepView) {
        camera.position.copy(center).addScaledVector(dir, radius * 4);
        camera.lookAt(center);
        controls.update();
      } else {
        api.setPreset("axo");
      }
      for (const name of Object.keys(fixedCams)) place(fixedCams[name], name);
      updateFrustums();
    },

    setPreset(name) {
      endFlight();
      place(camera, name);
      camera.zoom = 1;
      camera.updateProjectionMatrix();
      controls.target.copy(center);
      controls.update();
    },

    // Fly to look at the model from an arbitrary unit direction (view cube).
    flyTo(dir) {
      const d = dir.clone().normalize();
      // Straight down/up has no meaningful +Z up vector - fall back to +Y
      const up = new THREE.Vector3(0, 0, 1);
      if (Math.abs(d.z) > 0.999) up.set(0, 1, 0);
      controls.target.copy(center);
      const dist = camera.position.distanceTo(center) || radius * 4;
      const endPos = center.clone().addScaledVector(d, dist);
      const q1 = new THREE.Quaternion().setFromRotationMatrix(
        new THREE.Matrix4().lookAt(endPos, center, up));
      fly = {
        q0: camera.quaternion.clone(), q1, up, dist,
        t0: performance.now(), dur: FLY_SECONDS * 1000,
      };
      controls.enabled = false;
    },

    // Camera direction from the model centre, for the view cube to mirror.
    getDirection(out) {
      return out.copy(camera.position).sub(controls.target).normalize();
    },

    // Orbit the interactive camera by screen-space drag deltas (radians).
    orbitBy(dAzimuth, dPolar) {
      const offset = camera.position.clone().sub(controls.target);
      const spherical = new THREE.Spherical().setFromVector3(
        new THREE.Vector3(offset.x, offset.z, -offset.y));
      spherical.theta -= dAzimuth;
      spherical.phi = Math.max(1e-4, Math.min(Math.PI - 1e-4, spherical.phi - dPolar));
      const v = new THREE.Vector3().setFromSpherical(spherical);
      camera.up.set(0, 0, 1);
      camera.position.copy(controls.target).add(new THREE.Vector3(v.x, -v.z, v.y));
      camera.lookAt(controls.target);
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

    tick() {
      if (!fly) { controls.update(); return; }
      const t = Math.min((performance.now() - fly.t0) / fly.dur, 1);
      const e = t * t * (3 - 2 * t);
      camera.quaternion.slerpQuaternions(fly.q0, fly.q1, e);
      camera.position.copy(center).add(
        new THREE.Vector3(0, 0, 1).applyQuaternion(camera.quaternion).multiplyScalar(fly.dist));
      if (t >= 1) endFlight();
    },
  };
  return api;
}
