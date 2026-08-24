// Render styles: material sets, a UI theme, and optional full-screen post
// passes. Post passes are hand-rolled (render target + fullscreen triangle),
// no addons - that keeps them compatible with the quad-view viewport path.
//
// A style has one or more variants ("modes"): clicking the active style button
// advances to its next variant (and re-seeds the palette for RANDOM).

import * as THREE from "three";
import { LAYER_COLORS } from "./model-data.js";

export const STYLES = [
  "plaster", "solid", "random", "mono", "wireframe", "blueprint", "dither", "pixel",
];

// Deterministic per-element colors for the "random" style
function mulberry32(seed) {
  let a = seed >>> 0;
  return () => {
    a += 0x6d2b79f5;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

// ------------------------------------------------------------------
// UI themes - written to CSS custom properties on <html>
// ------------------------------------------------------------------

const LIGHT = {
  ink: "#141414", dim: "#5f5f5c", border: "rgba(0,0,0,0.32)",
  panel: "rgba(255,255,255,0.62)", halo: "rgba(255,255,255,0.9)",
};
const DARK = {
  ink: "#f0f0ee", dim: "#a0a09c", border: "rgba(255,255,255,0.34)",
  panel: "rgba(0,0,0,0.5)", halo: "rgba(0,0,0,0.9)",
};

function theme(base, bg, accent, hover = accent) {
  return { ...base, bg, accent, hover, select: accent };
}

// ------------------------------------------------------------------
// SSAO: depth-only screen-space occlusion, normals reconstructed from
// neighbouring depth taps. Approximates Blender Workbench's cavity shading.
// ------------------------------------------------------------------

function aoKernel(n) {
  const rand = mulberry32(9876);
  const out = [];
  for (let i = 0; i < n; i++) {
    let x, y, z, len;
    do {
      x = rand() * 2 - 1; y = rand() * 2 - 1; z = rand();
      len = Math.hypot(x, y, z);
    } while (len < 0.05 || len > 1);
    // Cluster samples toward the origin for tighter contact darkening
    const k = (0.35 + 0.65 * ((i / n) ** 2)) / len;
    out.push(`vec3(${(x * k).toFixed(4)}, ${(y * k).toFixed(4)}, ${(z * k).toFixed(4)})`);
  }
  return out;
}

// Render targets are always linear-sRGB in three.js, and a hand-written
// ShaderMaterial bypasses the renderer's output encoding - so every pass has
// to encode on its way to the canvas or the whole image comes out dark.
const SRGB_FN = `
vec3 toSRGB(vec3 c) {
  c = clamp(c, 0.0, 1.0);
  return mix(c * 12.92, 1.055 * pow(c, vec3(0.41666)) - 0.055, step(0.0031308, c));
}`;

const AO_SAMPLES = 14;
// GLSL ES 1.00: no const arrays and no derivatives, so the kernel is unrolled
// and the normal comes from neighbouring depth taps rather than dFdx/dFdy.
const AO_FRAG = `
${SRGB_FN}
uniform sampler2D tDiffuse;
uniform sampler2D tDepth;
uniform mat4 uProj;
uniform mat4 uProjInv;
uniform vec2 uTexel;
uniform float uRadius;
uniform float uStrength;
varying vec2 vUv;

vec3 viewPos(vec2 uv, float d) {
  vec4 clip = vec4(uv * 2.0 - 1.0, d * 2.0 - 1.0, 1.0);
  vec4 v = uProjInv * clip;
  return v.xyz / v.w;
}

vec3 viewPosAt(vec2 uv) {
  return viewPos(uv, texture2D(tDepth, uv).x);
}

float occlude(vec3 p, mat3 tbn, vec3 k, float radius) {
  vec3 s = p + tbn * k * radius;
  vec4 sp = uProj * vec4(s, 1.0);
  vec2 suv = (sp.xy / sp.w) * 0.5 + 0.5;
  if (suv.x < 0.0 || suv.x > 1.0 || suv.y < 0.0 || suv.y > 1.0) return 0.0;
  float sd = texture2D(tDepth, suv).x;
  if (sd >= 1.0) return 0.0;
  float sz = viewPos(suv, sd).z;
  // View-space z grows toward the camera: sz above s.z means the surface
  // sampled there sits in front of the sample point, so the point is occluded.
  // The bias has to clear the depth noise of near-tangential samples, or a
  // flat surface self-occludes at roughly 50% and the whole model goes dark.
  float range = smoothstep(0.0, 1.0, radius / max(abs(p.z - sz), 1e-4));
  return step(s.z + 0.02 * radius, sz) * range;
}

void main() {
  vec3 color = texture2D(tDiffuse, vUv).rgb;
  float depth = texture2D(tDepth, vUv).x;
  if (depth >= 1.0) { gl_FragColor = vec4(toSRGB(color), 1.0); return; }

  vec3 p = viewPos(vUv, depth);
  // Pick the nearer neighbour on each axis so silhouettes keep sane normals
  vec3 px1 = viewPosAt(vUv + vec2(uTexel.x, 0.0)) - p;
  vec3 px2 = p - viewPosAt(vUv - vec2(uTexel.x, 0.0));
  vec3 py1 = viewPosAt(vUv + vec2(0.0, uTexel.y)) - p;
  vec3 py2 = p - viewPosAt(vUv - vec2(0.0, uTexel.y));
  vec3 dx = abs(px1.z) < abs(px2.z) ? px1 : px2;
  vec3 dy = abs(py1.z) < abs(py2.z) ? py1 : py2;
  vec3 n = normalize(cross(dx, dy));
  if (n.z < 0.0) n = -n;

  // Per-pixel rotation so the low sample count reads as noise, not banding
  float ang = fract(sin(dot(gl_FragCoord.xy, vec2(12.9898, 78.233))) * 43758.5453) * 6.2831853;
  vec3 rv = vec3(cos(ang), sin(ang), 0.0);
  vec3 t = normalize(rv - n * dot(rv, n));
  mat3 tbn = mat3(t, cross(n, t), n);

  float occ = 0.0;
${aoKernel(AO_SAMPLES).map((k) => `  occ += occlude(p, tbn, ${k}, uRadius);`).join("\n")}
  float shade = clamp(1.0 - (occ / float(${AO_SAMPLES})) * uStrength, 0.0, 1.0);
  gl_FragColor = vec4(toSRGB(color * shade), 1.0);
}`;

const DITHER_FRAG = `
${SRGB_FN}
uniform sampler2D tDiffuse;
varying vec2 vUv;
void main() {
  vec3 c = toSRGB(texture2D(tDiffuse, vUv).rgb);
  float lum = dot(c, vec3(0.299, 0.587, 0.114));
  int x = int(mod(gl_FragCoord.x, 4.0));
  int y = int(mod(gl_FragCoord.y, 4.0));
  int i = y * 4 + x;
  float b[16];
  b[0]=0.0;  b[1]=8.0;  b[2]=2.0;  b[3]=10.0;
  b[4]=12.0; b[5]=4.0;  b[6]=14.0; b[7]=6.0;
  b[8]=3.0;  b[9]=11.0; b[10]=1.0; b[11]=9.0;
  b[12]=15.0;b[13]=7.0; b[14]=13.0;b[15]=5.0;
  float threshold = (b[i] + 0.5) / 16.0;
  float v = lum > threshold ? 1.0 : 0.0;
  gl_FragColor = vec4(vec3(v), 1.0);
}`;

const PIXEL_FRAG = `
${SRGB_FN}
uniform sampler2D tDiffuse;
varying vec2 vUv;
void main() {
  vec3 c = toSRGB(texture2D(tDiffuse, vUv).rgb);
  c = floor(c * 5.0 + 0.5) / 5.0;
  gl_FragColor = vec4(c, 1.0);
}`;

const QUAD_VERT = `
varying vec2 vUv;
void main() { vUv = uv; gl_Position = vec4(position.xy, 0.0, 1.0); }`;

function makeFullscreenQuad(fragmentShader, extraUniforms = {}) {
  const geom = new THREE.BufferGeometry();
  geom.setAttribute("position", new THREE.BufferAttribute(
    new Float32Array([-1, -1, 0, 3, -1, 0, -1, 3, 0]), 3));
  geom.setAttribute("uv", new THREE.BufferAttribute(
    new Float32Array([0, 0, 2, 0, 0, 2]), 2));
  const mat = new THREE.ShaderMaterial({
    uniforms: { tDiffuse: { value: null }, ...extraUniforms },
    vertexShader: QUAD_VERT,
    fragmentShader,
    depthTest: false, depthWrite: false,
  });
  const mesh = new THREE.Mesh(geom, mat);
  const quadScene = new THREE.Scene();
  quadScene.add(mesh);
  const quadCam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
  return { quadScene, quadCam, mat };
}

// ------------------------------------------------------------------
// Style variants
// ------------------------------------------------------------------

// Flat, unlit fill. Every fill material stays white and takes its colour from
// the vertex/instance attribute - that way the hover tint can lighten as well
// as darken, which a tinted material multiplied by vertex colour cannot.
const flat = () => new THREE.MeshBasicMaterial({
  color: 0xffffff, vertexColors: true,
  polygonOffset: true, polygonOffsetFactor: 1, polygonOffsetUnits: 1,
});

const DEFS = {
  plaster: [{
    bg: 0xc9c9c6, colors: 0xe8e4dc, edges: true, ao: true,
    theme: theme(LIGHT, "#c9c9c6", "#b4633a"),
    fill: () => new THREE.MeshStandardMaterial({
      color: 0xffffff, roughness: 0.95, vertexColors: true,
    }),
    line: () => new THREE.LineBasicMaterial({ color: 0x1a1a1a }),
  }],
  solid: [{
    bg: 0xd3d5d3, colors: "layer", edges: true, ao: true,
    theme: theme(LIGHT, "#d3d5d3", "#2f6fb0"),
    fill: () => new THREE.MeshLambertMaterial({ vertexColors: true }),
    line: () => new THREE.LineBasicMaterial({ color: 0x1a1a1a }),
  }],
  random: [{
    bg: 0xffffff, colors: "random", edges: true, ao: true,
    theme: theme(LIGHT, "#ffffff", "#e5195b"),
    fill: () => new THREE.MeshLambertMaterial({ vertexColors: true }),
    line: () => new THREE.LineBasicMaterial({ color: 0x111111 }),
  }],
  mono: [
    {
      bg: 0x000000, colors: 0xffffff, edges: true,
      theme: theme(DARK, "#000000", "#ffffff", "#8a8a8a"),
      fill: flat,
      line: () => new THREE.LineBasicMaterial({ color: 0x000000 }),
    },
    {
      bg: 0xffffff, colors: 0x121212, edges: true,
      theme: theme(LIGHT, "#ffffff", "#000000", "#8a8a8a"),
      fill: flat,
      line: () => new THREE.LineBasicMaterial({ color: 0xffffff }),
    },
  ],
  wireframe: [
    {
      // Fill painted in the background color = hidden-line removal
      bg: 0xffffff, colors: 0xffffff, edges: true,
      theme: theme(LIGHT, "#ffffff", "#000000", "#9a9a9a"),
      fill: flat,
      line: () => new THREE.LineBasicMaterial({ color: 0x000000 }),
    },
    {
      bg: 0x000000, colors: 0x000000, edges: true,
      theme: theme(DARK, "#000000", "#ffffff", "#6a6a6a"),
      fill: flat,
      line: () => new THREE.LineBasicMaterial({ color: 0xffffff }),
    },
  ],
  blueprint: [{
    bg: 0x102a66, colors: 0x16337a, edges: true,
    theme: theme(DARK, "#102a66", "#ffd54a"),
    fill: flat,
    line: () => new THREE.LineBasicMaterial({ color: 0xdce8ff }),
  }],
  dither: [{
    bg: 0xffffff, colors: 0xe8e4dc, edges: false, pass: "dither", passScale: 1,
    theme: theme(LIGHT, "#ffffff", "#000000", "#909090"),
    fill: () => new THREE.MeshStandardMaterial({
      color: 0xffffff, roughness: 0.95, vertexColors: true,
    }),
    line: () => new THREE.LineBasicMaterial({ color: 0x555555 }),
  }],
  pixel: [{
    bg: 0xd3d5d3, colors: "layer", edges: false, pass: "pixel", passScale: 0.25,
    theme: theme(LIGHT, "#d3d5d3", "#2f6fb0"),
    fill: () => new THREE.MeshLambertMaterial({ vertexColors: true }),
    line: () => new THREE.LineBasicMaterial({ color: 0x1a1a1a }),
  }],
};

export function makeStyles(renderer, scene, { onMaterials, onTheme } = {}) {
  const passes = {
    dither: makeFullscreenQuad(DITHER_FRAG),
    pixel: makeFullscreenQuad(PIXEL_FRAG),
    ao: makeFullscreenQuad(AO_FRAG, {
      tDepth: { value: null },
      uProj: { value: new THREE.Matrix4() },
      uProjInv: { value: new THREE.Matrix4() },
      uTexel: { value: new THREE.Vector2() },
      uRadius: { value: 0.3 },
      uStrength: { value: 0.7 },
    }),
  };
  let active = "solid";
  let mode = 0;
  let randomSeed = 12345;
  // Render targets are cached by size: the quad view renders four viewports of
  // two different sizes per frame, and a single slot would dispose/recreate the
  // target four times a frame.
  const targets = new Map();
  const MAX_TARGETS = 6;
  let lastSceneApi = null;
  let lastModel = null;

  function def() { return DEFS[active][mode]; }

  function ensureRT(w, h, scale, nearest, needDepth) {
    const key = `${w}x${h}x${scale}x${nearest}x${needDepth}`;
    const hit = targets.get(key);
    if (hit) {
      targets.delete(key); // re-insert to keep Map order = least-recently-used first
      targets.set(key, hit);
      return hit;
    }
    if (targets.size >= MAX_TARGETS) {
      const oldestKey = targets.keys().next().value;
      const oldest = targets.get(oldestKey);
      if (oldest.depthTexture) oldest.depthTexture.dispose();
      oldest.dispose();
      targets.delete(oldestKey);
    }
    const tw = Math.max(1, Math.round(w * scale));
    const th = Math.max(1, Math.round(h * scale));
    const target = new THREE.WebGLRenderTarget(tw, th, {
      minFilter: nearest ? THREE.NearestFilter : THREE.LinearFilter,
      magFilter: nearest ? THREE.NearestFilter : THREE.LinearFilter,
      depthBuffer: true,
    });
    if (needDepth) {
      target.depthTexture = new THREE.DepthTexture(tw, th, THREE.UnsignedIntType);
    }
    targets.set(key, target);
    return target;
  }

  function applyTheme(t) {
    const root = document.documentElement.style;
    root.setProperty("--bg", t.bg);
    root.setProperty("--ink", t.ink);
    root.setProperty("--dim", t.dim);
    root.setProperty("--accent", t.accent);
    root.setProperty("--border", t.border);
    root.setProperty("--panel", t.panel);
    root.setProperty("--halo", t.halo);
    if (onTheme) onTheme(t);
  }

  const api = {
    get theme() { return def().theme; },
    get hoverColor() { return new THREE.Color(def().theme.hover); },
    get selectColor() { return new THREE.Color(def().theme.select); },

    // Radius of the model's bounding sphere - scales the AO kernel to the model
    setSceneRadius(r) {
      passes.ao.mat.uniforms.uRadius.value = Math.max(r * 0.022, 0.05);
    },

    // advance=true re-clicks the active style: next mode, or re-seed for RANDOM
    apply(name, sceneApi, model, { advance = false } = {}) {
      if (!DEFS[name]) return;
      if (advance && name === active) {
        mode = (mode + 1) % DEFS[name].length;
        if (name === "random") randomSeed = (randomSeed * 1664525 + 1013904223) >>> 0;
      } else if (name !== active) {
        mode = 0;
      }
      active = name;
      if (sceneApi) lastSceneApi = sceneApi;
      if (model) lastModel = model;
      const d = def();
      applyTheme(d.theme);
      if (!lastSceneApi) return;
      scene.background = new THREE.Color(d.bg);
      const fill = d.fill();
      const glass = d.fill();
      glass.transparent = true;
      glass.opacity = 0.5;
      glass.depthWrite = false;
      const line = d.line();
      lastSceneApi.setMaterials({ fill, glass, line });
      lastSceneApi.setEdgesVisible(d.edges);
      lastSceneApi.setSelected(null);
      const c = new THREE.Color();
      if (d.colors === "layer") {
        lastSceneApi.setElementColors((e) => c.setHex(LAYER_COLORS[lastModel.layer[e]]));
      } else if (d.colors === "random") {
        const rand = mulberry32(randomSeed);
        const palette = Array.from({ length: 64 }, () =>
          new THREE.Color().setHSL(rand(), 0.45, 0.62));
        lastSceneApi.setElementColors((e) => palette[e % 64]);
      } else {
        c.setHex(d.colors); // a plain hex: one constant colour for every element
        lastSceneApi.setElementColors(() => c);
      }
      if (onMaterials) onMaterials([fill, glass, line]);
    },

    // Render honoring the active post pass. viewport: {x,y,w,h} in device px
    // (used by the quad view); defaults to the full drawing buffer.
    render(camera, viewport = null) {
      const d = def();
      const size = renderer.getDrawingBufferSize(new THREE.Vector2());
      const vp = viewport ?? { x: 0, y: 0, w: size.x, h: size.y };
      const pr = renderer.getPixelRatio();
      const setVp = () => {
        renderer.setViewport(vp.x / pr, vp.y / pr, vp.w / pr, vp.h / pr);
        renderer.setScissor(vp.x / pr, vp.y / pr, vp.w / pr, vp.h / pr);
        renderer.setScissorTest(viewport !== null);
      };
      if (!d.pass && !d.ao) {
        setVp();
        renderer.render(scene, camera);
        renderer.setScissorTest(false);
        return;
      }
      const target = ensureRT(vp.w, vp.h, d.pass ? d.passScale : 1,
        d.pass === "pixel", !!d.ao);
      renderer.setRenderTarget(target);
      // setViewport multiplies by pixelRatio internally, so divide it back out;
      // passing raw device pixels here scales the image and shifts it off-centre.
      renderer.setViewport(0, 0, target.width / pr, target.height / pr);
      renderer.setScissorTest(false);
      renderer.render(scene, camera);
      renderer.setRenderTarget(null);

      const pass = d.ao ? passes.ao : passes[d.pass];
      pass.mat.uniforms.tDiffuse.value = target.texture;
      if (d.ao) {
        pass.mat.uniforms.tDepth.value = target.depthTexture;
        pass.mat.uniforms.uProj.value.copy(camera.projectionMatrix);
        pass.mat.uniforms.uProjInv.value.copy(camera.projectionMatrixInverse);
        pass.mat.uniforms.uTexel.value.set(1 / target.width, 1 / target.height);
      }
      setVp();
      renderer.render(pass.quadScene, pass.quadCam);
      renderer.setScissorTest(false);
    },
  };
  return api;
}
