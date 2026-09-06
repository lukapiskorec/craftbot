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
  // In-flight camera move (view cube click, knolling): orientation slerps so
  // the up vector never flips mid-way, while the look-at point and the
  // framing radius ease along with it. Orbit controls are paused until it
  // lands. bump widens the framing mid-flight (elements in transit need more
  // room than either end state).
  let fly = null; // {q0, q1, up, c0, c1, r0, r1, bump, t0, dur}
  const FLY_SECONDS = 0.5;
  const FRAME_MARGIN = 1.15; // framing: the bounds fill the canvas up to this

  // Straight down/up has no meaningful +Z up vector - fall back to +Y
  function upFor(dir) {
    return Math.abs(dir.z) > 0.999 ? new THREE.Vector3(0, 1, 0) : new THREE.Vector3(0, 0, 1);
  }

  // Frustum radius (see frustum()) at which `bounds` seen from `dir` fills
  // the canvas within the margin, and the point to look at: the bounds
  // centre moved to the middle of the projected extent. insets: CSS px of
  // canvas covered by panels on the left and right - the bounds are framed
  // into, and centred on, the strip between them.
  function framing(bounds, dir, insets = { left: 0, right: 0 }) {
    const z = dir.clone().normalize();
    const x = new THREE.Vector3().crossVectors(upFor(z), z).normalize();
    const y = new THREE.Vector3().crossVectors(z, x);
    let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
    const corner = new THREE.Vector3();
    for (let i = 0; i < 8; i++) {
      corner.set(i & 1 ? bounds.max.x : bounds.min.x, i & 2 ? bounds.max.y : bounds.min.y,
        i & 4 ? bounds.max.z : bounds.min.z);
      const px = corner.dot(x), py = corner.dot(y);
      if (px < minX) minX = px; if (px > maxX) maxX = px;
      if (py < minY) minY = py; if (py > maxY) maxY = py;
    }
    const cw = canvas.clientWidth || 1, ch = canvas.clientHeight || 1;
    const aspect = cw / ch;
    const freeW = Math.max(cw - insets.left - insets.right, cw * 0.3);
    const half = Math.max((maxX - minX) / 2 * (cw / freeW) / Math.max(aspect, 1),
      (maxY - minY) / 2 / Math.max(1 / aspect, 1)) * FRAME_MARGIN;
    const c = bounds.getCenter(new THREE.Vector3());
    c.addScaledVector(x, (minX + maxX) / 2 - c.dot(x)).addScaledVector(y, (minY + maxY) / 2 - c.dot(y));
    // Look left of the content by the strip's offset so it sits in the strip
    const worldPerPx = (2 * half * Math.max(aspect, 1)) / cw;
    c.addScaledVector(x, -((insets.left - insets.right) / 2) * worldPerPx);
    return { radius: Math.max(half / 1.2, 0.001), center: c };
  }

  // Begin a flight to look from dir at c1 with framing radius r1. The
  // current zoom is folded into the start radius so the view does not jump
  // and the flight always lands on zoom 1.
  function startFlight(dir, c1, r1, seconds, bump = 0) {
    const d = dir.clone().normalize();
    const up = upFor(d);
    const endPos = c1.clone().addScaledVector(d, r1 * 4);
    const q1 = new THREE.Quaternion().setFromRotationMatrix(
      new THREE.Matrix4().lookAt(endPos, c1, up));
    radius /= camera.zoom;
    camera.zoom = 1;
    updateFrustums();
    fly = {
      q0: camera.quaternion.clone(), q1, up, c0: center.clone(), c1: c1.clone(),
      r0: radius, r1, bump, t0: performance.now(), dur: seconds * 1000,
    };
    controls.enabled = false;
    if (seconds <= 0) endFlight();
  }
  // One zoom shared by the three fixed 4-view cameras so they stay on grid
  let fixedZoom = 1;

  function applyFixedZoom() {
    for (const cam of Object.values(fixedCams)) {
      cam.zoom = fixedZoom;
      cam.updateProjectionMatrix();
    }
  }

  // Which camera owns a client-space point, with its viewport in CSS px.
  // 4-view layout: top | axo over front | side.
  function quadrantAt(clientX, clientY) {
    const r = canvas.getBoundingClientRect();
    if (!quad) return { camera, x0: r.left, y0: r.top, w: r.width, h: r.height };
    const w = r.width / 2, h = r.height / 2;
    const right = clientX >= r.left + w, bottom = clientY >= r.top + h;
    const cam = bottom ? (right ? fixedCams.side : fixedCams.front)
      : (right ? camera : fixedCams.top);
    return { camera: cam, x0: r.left + (right ? w : 0), y0: r.top + (bottom ? h : 0), w, h };
  }

  // Wheel over a fixed quadrant zooms the fixed views; registered in the
  // capture phase so OrbitControls (which would zoom axo) never sees it.
  canvas.addEventListener("wheel", (ev) => {
    if (!quad || quadrantAt(ev.clientX, ev.clientY).camera === camera) return;
    ev.preventDefault();
    ev.stopImmediatePropagation();
    fixedZoom = Math.min(50, Math.max(0.1, fixedZoom * Math.pow(0.95, ev.deltaY * 0.01)));
    applyFixedZoom();
  }, { capture: true, passive: false });

  // Two-finger pinch over a fixed quadrant zooms the fixed views (touch
  // counterpart of the wheel above). OrbitControls still sees the pointers
  // but its own dolly/pan is switched off for the gesture.
  const fixedTouches = new Map(); // pointerId -> {x, y}
  let pinchDist = 0;
  function pinchEnd(ev) {
    if (!fixedTouches.delete(ev.pointerId)) return;
    pinchDist = 0;
    if (fixedTouches.size === 0) { controls.enableZoom = true; controls.enablePan = true; }
  }
  canvas.addEventListener("pointerdown", (ev) => {
    if (!quad || ev.pointerType !== "touch") return;
    if (quadrantAt(ev.clientX, ev.clientY).camera === camera) return;
    fixedTouches.set(ev.pointerId, { x: ev.clientX, y: ev.clientY });
    pinchDist = 0;
    if (fixedTouches.size >= 2) { controls.enableZoom = false; controls.enablePan = false; }
  }, { capture: true });
  canvas.addEventListener("pointermove", (ev) => {
    if (!fixedTouches.has(ev.pointerId)) return;
    fixedTouches.set(ev.pointerId, { x: ev.clientX, y: ev.clientY });
    if (fixedTouches.size !== 2) return;
    const [a, b] = [...fixedTouches.values()];
    const d = Math.hypot(a.x - b.x, a.y - b.y);
    if (pinchDist > 0 && d > 0) {
      fixedZoom = Math.min(50, Math.max(0.1, fixedZoom * d / pinchDist));
      applyFixedZoom();
    }
    pinchDist = d;
  }, { capture: true });
  canvas.addEventListener("pointerup", pinchEnd, { capture: true });
  canvas.addEventListener("pointercancel", pinchEnd, { capture: true });

  function endFlight() {
    if (!fly) return;
    camera.quaternion.copy(fly.q1);
    camera.up.copy(fly.up);
    radius = fly.r1;
    center.copy(fly.c1);
    camera.position.copy(center).add(
      new THREE.Vector3(0, 0, 1).applyQuaternion(camera.quaternion).multiplyScalar(radius * 4));
    controls.target.copy(center);
    for (const name of Object.keys(fixedCams)) place(fixedCams[name], name);
    updateFrustums();
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
        fixedZoom = 1;
        applyFixedZoom();
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

    // Fly to look at the model from an arbitrary unit direction (view cube),
    // keeping the current framing.
    flyTo(dir) {
      endFlight();
      startFlight(dir, center, radius / camera.zoom, FLY_SECONDS);
    },

    // Fly to look from dir at bounds, framed to fit exactly, over `seconds`
    // (0 = at once). midBounds: what has to stay in view half-way. insets:
    // canvas px covered by panels left and right (see framing()).
    frameTo(bounds, dir, seconds, { midBounds = null, insets = undefined } = {}) {
      endFlight();
      const end = framing(bounds, dir, insets);
      let bump = 0;
      if (midBounds) {
        const mid = framing(midBounds, dir, insets).radius;
        bump = Math.max(0, mid - (radius / camera.zoom + end.radius) / 2);
      }
      startFlight(dir, end.center, end.radius, seconds, bump);
    },

    // Camera + normalised device coords for picking at a client point;
    // honours the 4-view quadrants.
    pickCamera(clientX, clientY) {
      const q = quadrantAt(clientX, clientY);
      return {
        camera: q.camera,
        x: ((clientX - q.x0) / q.w) * 2 - 1,
        y: -((clientY - q.y0) / q.h) * 2 + 1,
      };
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
      center.lerpVectors(fly.c0, fly.c1, e);
      radius = fly.r0 + (fly.r1 - fly.r0) * e + fly.bump * Math.sin(Math.PI * e);
      camera.position.copy(center).add(
        new THREE.Vector3(0, 0, 1).applyQuaternion(camera.quaternion).multiplyScalar(radius * 4));
      updateFrustums();
      if (t >= 1) endFlight();
    },
  };
  return api;
}
