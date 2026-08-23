// Render styles: material sets + optional full-screen post passes.
// Post passes are hand-rolled (render target + fullscreen triangle), no addons.

import * as THREE from "three";
import { LAYER_COLORS } from "./model-data.js";

export const STYLES = ["plaster", "solid", "random", "blueprint", "dither", "pixel"];

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

const DITHER_FRAG = `
uniform sampler2D tDiffuse;
varying vec2 vUv;
void main() {
  vec3 c = texture2D(tDiffuse, vUv).rgb;
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
uniform sampler2D tDiffuse;
varying vec2 vUv;
void main() {
  vec3 c = texture2D(tDiffuse, vUv).rgb;
  c = floor(c * 5.0 + 0.5) / 5.0;
  gl_FragColor = vec4(c, 1.0);
}`;

const QUAD_VERT = `
varying vec2 vUv;
void main() { vUv = uv; gl_Position = vec4(position.xy, 0.0, 1.0); }`;

function makeFullscreenQuad(fragmentShader) {
  const geom = new THREE.BufferGeometry();
  geom.setAttribute("position", new THREE.BufferAttribute(
    new Float32Array([-1, -1, 0, 3, -1, 0, -1, 3, 0]), 3));
  geom.setAttribute("uv", new THREE.BufferAttribute(
    new Float32Array([0, 0, 2, 0, 0, 2]), 2));
  const mat = new THREE.ShaderMaterial({
    uniforms: { tDiffuse: { value: null } },
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

const DEFS = {
  plaster: {
    bg: 0xc8c8cc, colors: "white", edges: false, grid: true,
    fill: () => new THREE.MeshStandardMaterial({ color: 0xe8e4dc, roughness: 0.95, vertexColors: true }),
    line: () => new THREE.LineBasicMaterial({ color: 0x9a968e }),
  },
  solid: {
    bg: 0xdfe6ea, colors: "layer", edges: true, grid: true,
    fill: () => new THREE.MeshLambertMaterial({ vertexColors: true }),
    line: () => new THREE.LineBasicMaterial({ color: 0x1a1a1a }),
  },
  random: {
    bg: 0xffffff, colors: "random", edges: true, grid: false,
    fill: () => new THREE.MeshBasicMaterial({ vertexColors: true }),
    line: () => new THREE.LineBasicMaterial({ color: 0x111111 }),
  },
  blueprint: {
    bg: 0x102a66, colors: "white", edges: true, grid: false,
    fill: () => new THREE.MeshBasicMaterial({
      color: 0x16337a, vertexColors: true,
      polygonOffset: true, polygonOffsetFactor: 1, polygonOffsetUnits: 1,
    }),
    line: () => new THREE.LineBasicMaterial({ color: 0xdce8ff }),
  },
  dither: {
    bg: 0xffffff, colors: "white", edges: false, grid: false, pass: "dither", passScale: 1,
    fill: () => new THREE.MeshStandardMaterial({ color: 0xe8e4dc, roughness: 0.95, vertexColors: true }),
    line: () => new THREE.LineBasicMaterial({ color: 0x555555 }),
  },
  pixel: {
    bg: 0xdfe6ea, colors: "layer", edges: false, grid: false, pass: "pixel", passScale: 0.25,
    fill: () => new THREE.MeshLambertMaterial({ vertexColors: true }),
    line: () => new THREE.LineBasicMaterial({ color: 0x1a1a1a }),
  },
};

export function makeStyles(renderer, scene, grid, { onMaterials } = {}) {
  const passes = {
    dither: makeFullscreenQuad(DITHER_FRAG),
    pixel: makeFullscreenQuad(PIXEL_FRAG),
  };
  let active = "solid";
  let rt = null;
  let rtKey = "";

  function ensureRT(w, h, scale, nearest) {
    const key = `${w}x${h}x${scale}x${nearest}`;
    if (rtKey === key && rt) return rt;
    if (rt) rt.dispose();
    rt = new THREE.WebGLRenderTarget(
      Math.max(1, Math.round(w * scale)), Math.max(1, Math.round(h * scale)), {
        minFilter: nearest ? THREE.NearestFilter : THREE.LinearFilter,
        magFilter: nearest ? THREE.NearestFilter : THREE.LinearFilter,
        depthBuffer: true,
      });
    rtKey = key;
    return rt;
  }

  const api = {
    get active() { return active; },

    apply(name, sceneApi, model) {
      const def = DEFS[name];
      if (!def || !sceneApi) return;
      active = name;
      scene.background = new THREE.Color(def.bg);
      grid.visible = def.grid;
      const fill = def.fill();
      const line = def.line();
      sceneApi.setMaterials(fill, line);
      sceneApi.setEdgesVisible(def.edges);
      const c = new THREE.Color();
      if (def.colors === "layer") {
        sceneApi.setElementColors((e) => c.setHex(LAYER_COLORS[model.layer[e]]));
      } else if (def.colors === "random") {
        const rand = mulberry32(12345);
        const palette = Array.from({ length: 64 }, () =>
          new THREE.Color().setHSL(rand(), 0.65, 0.55));
        sceneApi.setElementColors((e) => palette[e % 64]);
      } else {
        sceneApi.setElementColors(() => c.setRGB(1, 1, 1));
      }
      if (onMaterials) onMaterials(fill, line);
    },

    // Render honoring the active post pass. viewport: {x,y,w,h} in device px
    // (used by the quad view); defaults to the full drawing buffer.
    render(camera, viewport = null) {
      const def = DEFS[active];
      const size = renderer.getDrawingBufferSize(new THREE.Vector2());
      const vp = viewport ?? { x: 0, y: 0, w: size.x, h: size.y };
      if (!def.pass) {
        renderer.setViewport(vp.x / renderer.getPixelRatio(), vp.y / renderer.getPixelRatio(),
          vp.w / renderer.getPixelRatio(), vp.h / renderer.getPixelRatio());
        renderer.setScissor(vp.x / renderer.getPixelRatio(), vp.y / renderer.getPixelRatio(),
          vp.w / renderer.getPixelRatio(), vp.h / renderer.getPixelRatio());
        renderer.setScissorTest(viewport !== null);
        renderer.render(scene, camera);
        renderer.setScissorTest(false);
        return;
      }
      const target = ensureRT(vp.w, vp.h, def.passScale, def.pass === "pixel");
      renderer.setRenderTarget(target);
      renderer.setViewport(0, 0, target.width, target.height);
      renderer.render(scene, camera);
      renderer.setRenderTarget(null);
      const pass = passes[def.pass];
      pass.mat.uniforms.tDiffuse.value = target.texture;
      const pr = renderer.getPixelRatio();
      renderer.setViewport(vp.x / pr, vp.y / pr, vp.w / pr, vp.h / pr);
      renderer.setScissor(vp.x / pr, vp.y / pr, vp.w / pr, vp.h / pr);
      renderer.setScissorTest(viewport !== null);
      renderer.render(pass.quadScene, pass.quadCam);
      renderer.setScissorTest(false);
    },
  };
  return api;
}
