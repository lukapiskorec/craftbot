// Orthographic camera rig. Scene is Z-up (camera.up = +Z).
// Task 5: single camera + fit; presets and quad view arrive in Task 9.

import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";

export function makeViews(renderer, canvas) {
  const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.01, 1000);
  camera.up.set(0, 0, 1);
  const controls = new OrbitControls(camera, canvas);
  controls.enableDamping = true;
  controls.dampingFactor = 0.12;

  let radius = 10;
  let center = new THREE.Vector3();

  function updateFrustum() {
    const w = canvas.clientWidth || 1;
    const h = canvas.clientHeight || 1;
    const aspect = w / h;
    // Zoom-independent base frustum sized to the model bounding sphere
    const half = radius * 1.2;
    camera.left = -half * Math.max(aspect, 1);
    camera.right = half * Math.max(aspect, 1);
    camera.top = half * Math.max(1 / aspect, 1);
    camera.bottom = -half * Math.max(1 / aspect, 1);
    camera.near = 0.01;
    camera.far = radius * 40;
    camera.updateProjectionMatrix();
  }

  const api = {
    camera, controls,

    fit(bounds) {
      const sphere = bounds.getBoundingSphere(new THREE.Sphere());
      radius = Math.max(sphere.radius, 0.001);
      center = sphere.center.clone();
      controls.target.copy(center);
      const dir = new THREE.Vector3(1, -1, 0.8).normalize();
      camera.position.copy(center).addScaledVector(dir, radius * 4);
      camera.zoom = 1;
      updateFrustum();
      controls.update();
    },

    onResize() { updateFrustum(); },

    tick() { controls.update(); },
  };
  return api;
}
