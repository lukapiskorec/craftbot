// GPU animations. Every material gets a vertex-shader patch that moves
// elements in world space with zero per-frame CPU work:
//
// - Entry animations offset elements by a per-element spawn time (aSpawn
//   attribute; instanced boxes take their centre from instanceMatrix, merged
//   geometry carries an aCenter attribute).
// - Knolling transitions (knolling.js) blend each element between two rigid
//   poses - aFromQ/aFromP and aToQ/aToP, a quaternion about the element's
//   centre plus a new centre - at a per-element time offset (aDelay) along a
//   lifted arc. One uniform, uKnoll, is the global progress the slider scrubs.
//   Normals are rotated with the element so the arranged model shades right.

import * as THREE from "three";
import { computeSpawnTimes } from "./model-data.js";

export const ANIMS = ["drop", "rise", "assemble", "pop", "none"];
export const ORDERS = ["sequence", "layers"];
const MODE_ID = { none: 0, drop: 1, rise: 2, assemble: 3, pop: 4 };

// Fraction of a knolling transition spent staggering the element starts;
// the rest is the flight of a single element.
export const KNOLL_STAGGER = 0.6;

const HEADER = `
uniform float uTime;
uniform float uDur;
uniform int uMode;
uniform float uDrop;
uniform vec3 uFocus;
uniform float uKnollOn;
uniform float uKnoll;
uniform float uStagger;
uniform float uLift;
attribute float aSpawn;
attribute vec4 aFromQ;
attribute vec3 aFromP;
attribute vec4 aToQ;
attribute vec3 aToP;
attribute float aDelay;
#ifndef USE_INSTANCING
attribute vec3 aCenter;
#endif
vec3 cbRotate(vec4 q, vec3 v) {
  return v + 2.0 * cross(q.xyz, cross(q.xyz, v) + q.w * v);
}
float cbKnollT() {
  float u = clamp((uKnoll - aDelay * uStagger) / (1.0 - uStagger), 0.0, 1.0);
  return u * u * (3.0 - 2.0 * u);
}
vec4 cbKnollQ(float t) {
  return normalize(mix(aFromQ, aToQ, t));
}
`;

// Normals: transformedNormal is in view space here; the model matrix is the
// identity, so normalMatrix is the view rotation and its transpose undoes it.
const NORMAL_CHUNK = `
#include <defaultnormal_vertex>
if (uKnollOn > 0.5) {
  vec4 cbNq = cbKnollQ(cbKnollT());
  transformedNormal = normalMatrix * cbRotate(cbNq, transpose(normalMatrix) * transformedNormal);
}
`;

const PROJECT_CHUNK = `
vec4 mvPosition = vec4( transformed, 1.0 );
#ifdef USE_INSTANCING
  mvPosition = instanceMatrix * mvPosition;
  vec3 cbCenter = vec3(instanceMatrix[3]);
#else
  vec3 cbCenter = aCenter;
#endif
if (uKnollOn > 0.5) {
  float cbKt = cbKnollT();
  vec4 cbKq = cbKnollQ(cbKt);
  vec3 cbKc = mix(aFromP, aToP, cbKt) + vec3(0.0, 0.0, uLift * sin(3.14159265 * cbKt));
  mvPosition.xyz = cbKc + cbRotate(cbKq, mvPosition.xyz - cbCenter);
  cbCenter = cbKc;
}
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
    uKnollOn: { value: 0 },
    uKnoll: { value: 0 },
    uStagger: { value: KNOLL_STAGGER },
    uLift: { value: 0 },
  };
  let anim = "drop";
  let order = "sequence";
  let playing = false;
  let endTime = 0;
  let knoll = null; // {duration, settleOff, onEnd, playing}

  function stopEntry() {
    uniforms.uMode.value = 0;
    uniforms.uTime.value = 1e9;
    playing = false;
  }

  const api = {
    get anim() { return anim; },
    get playing() { return playing; },
    get order() { return order; },
    setAnim(name) { anim = name; },
    setOrder(name) { order = name; },

    patchMaterial(mat) {
      mat.onBeforeCompile = (shader) => {
        Object.assign(shader.uniforms, uniforms);
        shader.vertexShader = HEADER + shader.vertexShader
          .replace("#include <defaultnormal_vertex>", NORMAL_CHUNK)
          .replace("#include <project_vertex>", PROJECT_CHUNK);
      };
      mat.customProgramCacheKey = () => "craftbot-anim";
    },

    // kept (Uint8Array, optional): elements that stay in place - only the
    // rest animate in (iteration switch; see matchElements in model-data.js)
    play(model, sceneApi, { kept = null } = {}) {
      let animated = model ? model.count : 0;
      if (kept) for (let e = 0; e < model.count; e++) if (kept[e]) animated--;
      if (anim === "none" || animated === 0) {
        stopEntry();
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

    // ---- knolling ----
    // True while the pose blend is applied (elements are, or are on their
    // way to, an arrangement): hover, selection, caps and callouts read
    // model-space geometry and must stand down.
    get knollOn() { return uniforms.uKnollOn.value > 0.5; },
    get knollT() { return uniforms.uKnoll.value; },
    get knollPlaying() { return !!knoll?.playing; },

    // Start blending from one layout to another (poses per element, see
    // knolling.js). settleOff: the "to" layout is the model itself, so the
    // blend switches off once it lands. Cancels a running entry animation.
    startKnoll(sceneApi, from, to, delays, { lift, duration = 3, settleOff = false, onEnd = null }) {
      stopEntry();
      sceneApi.setPoses(from, to, delays);
      uniforms.uLift.value = lift;
      uniforms.uKnollOn.value = 1;
      uniforms.uKnoll.value = 0;
      knoll = { duration, settleOff, onEnd, playing: true };
    },

    // Slider scrub: hold the transition at progress t (0..1)
    seekKnoll(t) {
      if (!knoll) return;
      knoll.playing = false;
      uniforms.uKnoll.value = t;
      uniforms.uKnollOn.value = knoll.settleOff && t >= 1 ? 0 : 1;
    },

    // Back to the plain model instantly (model switch, entry replay)
    resetKnoll() {
      knoll = null;
      uniforms.uKnollOn.value = 0;
      uniforms.uKnoll.value = 0;
    },

    tick(dt) {
      if (knoll?.playing) {
        const t = Math.min(1, uniforms.uKnoll.value + dt / knoll.duration);
        uniforms.uKnoll.value = t;
        if (t >= 1) {
          knoll.playing = false;
          if (knoll.settleOff) uniforms.uKnollOn.value = 0;
          if (knoll.onEnd) knoll.onEnd();
        }
      }
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
