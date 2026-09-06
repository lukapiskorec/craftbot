// GPU entry animations. Every material gets a vertex-shader patch that
// offsets elements in world space based on a per-element spawn time
// (aSpawn attribute; instanced boxes take their center from instanceMatrix,
// merged geometry carries an aCenter attribute). Zero per-frame CPU work.

import * as THREE from "three";
import { computeSpawnTimes } from "./model-data.js";

export const ANIMS = ["drop", "rise", "assemble", "pop", "none"];
export const ORDERS = ["sequence", "layers"];
const MODE_ID = { none: 0, drop: 1, rise: 2, assemble: 3, pop: 4 };

const HEADER = `
uniform float uTime;
uniform float uDur;
uniform int uMode;
uniform float uDrop;
uniform vec3 uFocus;
attribute float aSpawn;
#ifndef USE_INSTANCING
attribute vec3 aCenter;
#endif
`;

const PROJECT_CHUNK = `
vec4 mvPosition = vec4( transformed, 1.0 );
#ifdef USE_INSTANCING
  mvPosition = instanceMatrix * mvPosition;
  vec3 cbCenter = vec3(instanceMatrix[3]);
#else
  vec3 cbCenter = aCenter;
#endif
if (uMode != 0) {
  float cbT = clamp((uTime - aSpawn) / uDur, 0.0, 1.0);
  float cbE = 1.0 - pow(1.0 - cbT, 3.0);
  if (uMode == 1) {
    mvPosition.z += (1.0 - cbE) * uDrop;
  } else if (uMode == 2) {
    mvPosition.z -= (1.0 - cbE) * (cbCenter.z + uDrop * 0.25);
  } else if (uMode == 3) {
    vec3 cbDir = normalize(cbCenter - uFocus + vec3(1e-4));
    mvPosition.xyz += cbDir * (1.0 - cbE) * uDrop;
  } else if (uMode == 4) {
    mvPosition.xyz = cbCenter + (mvPosition.xyz - cbCenter) * cbE;
  }
  // Collapse not-yet-spawned elements to their center (invisible)
  mvPosition.xyz = mix(cbCenter, mvPosition.xyz, step(aSpawn, uTime));
}
mvPosition = modelViewMatrix * mvPosition;
gl_Position = projectionMatrix * mvPosition;
`;

export function makeAnimations() {
  const uniforms = {
    uTime: { value: 1e9 }, // idle: everything spawned
    uDur: { value: 0.9 },
    uMode: { value: 0 },
    uDrop: { value: 20 },
    uFocus: { value: new THREE.Vector3() },
  };
  let anim = "drop";
  let order = "sequence";
  let playing = false;
  let endTime = 0;

  const api = {
    get anim() { return anim; },
    get playing() { return playing; },
    get order() { return order; },
    setAnim(name) { anim = name; },
    setOrder(name) { order = name; },

    patchMaterial(mat) {
      mat.onBeforeCompile = (shader) => {
        Object.assign(shader.uniforms, uniforms);
        shader.vertexShader = HEADER + shader.vertexShader.replace(
          "#include <project_vertex>", PROJECT_CHUNK);
      };
      mat.customProgramCacheKey = () => "craftbot-anim";
    },

    // kept (Uint8Array, optional): elements that stay in place - only the
    // rest animate in (iteration switch; see matchElements in model-data.js)
    play(model, sceneApi, { kept = null } = {}) {
      let animated = model ? model.count : 0;
      if (kept) for (let e = 0; e < model.count; e++) if (kept[e]) animated--;
      if (anim === "none" || animated === 0) {
        uniforms.uMode.value = 0;
        uniforms.uTime.value = 1e9;
        playing = false;
        return;
      }
      const total = Math.min(6, Math.max(2, animated * 0.004));
      sceneApi.setSpawnTimes(computeSpawnTimes(model, order, total, kept));
      const size = sceneApi.bounds.getSize(new THREE.Vector3());
      uniforms.uDrop.value = Math.max(size.z * 1.2, 4);
      sceneApi.bounds.getCenter(uniforms.uFocus.value);
      uniforms.uMode.value = MODE_ID[anim];
      uniforms.uTime.value = 0;
      endTime = total + uniforms.uDur.value;
      playing = true;
    },

    // Debug/testing: hold the animation at a fixed time
    freeze(t) {
      playing = false;
      uniforms.uTime.value = t;
    },

    tick(dt) {
      if (!playing) return;
      uniforms.uTime.value += dt;
      if (uniforms.uTime.value > endTime + 0.5) {
        uniforms.uTime.value = 1e9; // settle into idle (exact final positions)
        playing = false;
      }
    },
  };
  return api;
}
