// Section planes: three axis-aligned clipping planes with position + flip.
// Planes are assigned to the current materials, so call refresh() after a
// style change.

import * as THREE from "three";

const AXES = [
  new THREE.Vector3(-1, 0, 0),
  new THREE.Vector3(0, -1, 0),
  new THREE.Vector3(0, 0, -1),
];

export function makeSections() {
  const state = [0, 1, 2].map(() => ({ enabled: false, t: 1, flip: false }));
  const planes = [0, 1, 2].map(() => new THREE.Plane());
  let bounds = null;
  let sceneApi = null;

  function update() {
    if (!bounds || !sceneApi) return;
    const min = bounds.min, max = bounds.max;
    const active = [];
    for (let axis = 0; axis < 3; axis++) {
      const s = state[axis];
      if (!s.enabled) continue;
      const axisName = ["x", "y", "z"][axis];
      const lo = min[axisName], hi = max[axisName];
      const pad = (hi - lo) * 0.02 + 0.01;
      const pos = lo - pad + (hi - lo + 2 * pad) * s.t;
      const normal = AXES[axis].clone();
      if (s.flip) normal.negate();
      // plane: normal . p + constant >= 0 kept
      planes[axis].setFromNormalAndCoplanarPoint(normal, new THREE.Vector3(
        axis === 0 ? pos : 0, axis === 1 ? pos : 0, axis === 2 ? pos : 0));
      active.push(planes[axis]);
    }
    sceneApi.forEachMaterial((mat) => {
      mat.clippingPlanes = active.length ? active : null;
      mat.clipShadows = true;
    });
  }

  return {
    // Re-target after model load or style change
    refresh(newSceneApi, newBounds) {
      if (newSceneApi) sceneApi = newSceneApi;
      if (newBounds) bounds = newBounds;
      update();
    },

    set(axis, patch) {
      Object.assign(state[axis], patch);
      update();
    },

    reset() {
      for (const s of state) { s.enabled = false; s.t = 1; s.flip = false; }
      update();
    },

    getState(axis) { return { ...state[axis] }; },
  };
}
