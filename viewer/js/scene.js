// Scene construction: turns parsed ModelData into per-layer render buckets.
// Each layer is split into two parts - opaque and glass (windows) - so the
// glass part can carry its own semi-transparent material.
// Boxes: one InstancedMesh per part (single BoxGeometry, per-instance color).
// Custom meshes: one merged BufferGeometry per part (per-vertex color).
// Edges: merged LineSegments per part. The scene is Z-up (Blender convention).

import * as THREE from "three";
import { LineSegments2 } from "three/addons/lines/LineSegments2.js";
import { LineSegmentsGeometry } from "three/addons/lines/LineSegmentsGeometry.js";
import { LineMaterial } from "three/addons/lines/LineMaterial.js";
import { LAYERS, LAYER_COLORS } from "./model-data.js";

const CUBE_CORNERS = [
  [1, 1, -1], [1, -1, -1], [-1, -1, -1], [-1, 1, -1],
  [1, 1, 1], [1, -1, 1], [-1, -1, 1], [-1, 1, 1],
];
const CUBE_EDGES = [
  [0, 1], [1, 2], [2, 3], [3, 0],
  [4, 5], [5, 6], [6, 7], [7, 4],
  [0, 4], [1, 5], [2, 6], [3, 7],
];

export function buildModelGroup(model) {
  const group = new THREE.Group();
  const materials = {
    fill: new THREE.MeshLambertMaterial({ vertexColors: true }),
    glass: new THREE.MeshLambertMaterial({
      vertexColors: true, transparent: true, opacity: 0.5, depthWrite: false,
    }),
    line: new THREE.LineBasicMaterial({ color: 0x1a1a1a }),
  };

  const baseColors = new Float32Array(model.count * 3); // last applied colors
  const locate = new Array(model.count); // elementId -> {part, index|range}
  const buckets = LAYERS.map(() => ({ layerGroup: null, parts: [] }));

  const _m = new THREE.Matrix4();
  const _v = new THREE.Vector3();

  for (let li = 0; li < LAYERS.length; li++) {
    const bucket = buckets[li];
    const layerGroup = new THREE.Group();
    layerGroup.name = `layer:${LAYERS[li]}`;
    bucket.layerGroup = layerGroup;
    group.add(layerGroup);

    // glassFlag 0 = opaque part, 1 = glass part
    for (const glassFlag of [0, 1]) {
      const part = {
        glass: glassFlag === 1,
        boxMesh: null, meshMesh: null, boxEdges: null, meshEdges: null,
        boxElementIds: null, faceElement: null,
        vertexRanges: null, edgeRanges: null,
      };
      const partMaterial = glassFlag ? materials.glass : materials.fill;

      // ---- boxes ----
      const boxIdx = [];
      for (let b = 0; b < model.boxes.elementIds.length; b++) {
        const eid = model.boxes.elementIds[b];
        if (model.layer[eid] === li && model.isGlass[eid] === glassFlag) boxIdx.push(b);
      }
      if (boxIdx.length) {
        const n = boxIdx.length;
        const geom = new THREE.BoxGeometry(2, 2, 2);
        // vertexColors is on for the shared fill material (merged meshes need it);
        // boxes get a constant white attribute so instanceColor alone tints them.
        const white = new Float32Array(geom.getAttribute("position").count * 3).fill(1);
        geom.setAttribute("color", new THREE.BufferAttribute(white, 3));
        const spawn = new THREE.InstancedBufferAttribute(new Float32Array(n), 1);
        geom.setAttribute("aSpawn", spawn);
        const mesh = new THREE.InstancedMesh(geom, partMaterial, n);
        const elementIds = new Uint32Array(n);
        for (let i = 0; i < n; i++) {
          const b = boxIdx[i];
          const eid = model.boxes.elementIds[b];
          elementIds[i] = eid;
          _m.fromArray(model.boxes.matrices, b * 16);
          mesh.setMatrixAt(i, _m);
          mesh.setColorAt(i, new THREE.Color(1, 1, 1));
          locate[eid] = { part, index: i };
        }
        mesh.frustumCulled = false;
        part.boxMesh = mesh;
        part.boxElementIds = elementIds;
        layerGroup.add(mesh);

        // Baked world-space edge lines (24 verts per box)
        const pos = new Float32Array(n * 24 * 3);
        const espawn = new Float32Array(n * 24);
        const ecenter = new Float32Array(n * 24 * 3);
        let p = 0;
        for (let i = 0; i < n; i++) {
          const b = boxIdx[i];
          const eid = elementIds[i];
          _m.fromArray(model.boxes.matrices, b * 16);
          for (const [a, c] of CUBE_EDGES) {
            for (const corner of [CUBE_CORNERS[a], CUBE_CORNERS[c]]) {
              _v.set(corner[0], corner[1], corner[2]).applyMatrix4(_m);
              pos[p * 3] = _v.x; pos[p * 3 + 1] = _v.y; pos[p * 3 + 2] = _v.z;
              espawn[p] = 0;
              ecenter[p * 3] = model.centers[eid * 3];
              ecenter[p * 3 + 1] = model.centers[eid * 3 + 1];
              ecenter[p * 3 + 2] = model.centers[eid * 3 + 2];
              p++;
            }
          }
        }
        const egeom = new THREE.BufferGeometry();
        egeom.setAttribute("position", new THREE.BufferAttribute(pos, 3));
        egeom.setAttribute("aSpawn", new THREE.BufferAttribute(espawn, 1));
        egeom.setAttribute("aCenter", new THREE.BufferAttribute(ecenter, 3));
        const lines = new THREE.LineSegments(egeom, materials.line);
        lines.frustumCulled = false;
        lines.raycast = () => {};
        part.boxEdges = lines;
        layerGroup.add(lines);
      }

      // ---- custom meshes, merged ----
      const layerMeshes = model.meshes.filter((mm) =>
        model.layer[mm.elementId] === li && model.isGlass[mm.elementId] === glassFlag);
      if (layerMeshes.length) {
        let nv = 0, ni = 0;
        for (const mm of layerMeshes) { nv += mm.verts.length / 3; ni += mm.index.length; }
        const pos = new Float32Array(nv * 3);
        const col = new Float32Array(nv * 3).fill(1);
        const spawn = new Float32Array(nv);
        const center = new Float32Array(nv * 3);
        const index = new Uint32Array(ni);
        const faceElement = new Uint32Array(ni / 3);
        const vertexRanges = new Map(); // elementId -> [startVert, endVert)
        const edgeRanges = new Map(); // elementId -> [startVert, endVert) in edge buffer
        let vo = 0, io = 0;
        const edgePos = [], edgeSpawn = [], edgeCenter = [];
        for (const mm of layerMeshes) {
          const eid = mm.elementId;
          const vn = mm.verts.length / 3;
          pos.set(mm.verts, vo * 3);
          for (let i = 0; i < vn; i++) {
            center[(vo + i) * 3] = model.centers[eid * 3];
            center[(vo + i) * 3 + 1] = model.centers[eid * 3 + 1];
            center[(vo + i) * 3 + 2] = model.centers[eid * 3 + 2];
          }
          for (let i = 0; i < mm.index.length; i++) index[io + i] = mm.index[i] + vo;
          for (let f = 0; f < mm.index.length / 3; f++) faceElement[io / 3 + f] = eid;
          vertexRanges.set(eid, [vo, vo + vn]);
          locate[eid] = { part, range: [vo, vo + vn] };

          // Edges of this element (hard edges only)
          const eg = new THREE.BufferGeometry();
          eg.setAttribute("position", new THREE.BufferAttribute(Float32Array.from(mm.verts), 3));
          eg.setIndex(new THREE.BufferAttribute(mm.index, 1));
          const edges = new THREE.EdgesGeometry(eg, 10);
          const ep = edges.getAttribute("position").array;
          edgeRanges.set(eid, [edgeSpawn.length, edgeSpawn.length + ep.length / 3]);
          for (let i = 0; i < ep.length; i += 3) {
            edgePos.push(ep[i], ep[i + 1], ep[i + 2]);
            edgeSpawn.push(0);
            edgeCenter.push(model.centers[eid * 3], model.centers[eid * 3 + 1],
              model.centers[eid * 3 + 2]);
          }
          eg.dispose(); edges.dispose();
          vo += vn; io += mm.index.length;
        }
        const geom = new THREE.BufferGeometry();
        geom.setAttribute("position", new THREE.BufferAttribute(pos, 3));
        geom.setAttribute("color", new THREE.BufferAttribute(col, 3));
        geom.setAttribute("aSpawn", new THREE.BufferAttribute(spawn, 1));
        geom.setAttribute("aCenter", new THREE.BufferAttribute(center, 3));
        geom.setIndex(new THREE.BufferAttribute(index, 1));
        geom.computeVertexNormals();
        const mesh = new THREE.Mesh(geom, partMaterial);
        mesh.frustumCulled = false;
        part.meshMesh = mesh;
        part.faceElement = faceElement;
        part.vertexRanges = vertexRanges;
        part.edgeRanges = edgeRanges;
        layerGroup.add(mesh);

        const egeom = new THREE.BufferGeometry();
        egeom.setAttribute("position", new THREE.BufferAttribute(Float32Array.from(edgePos), 3));
        egeom.setAttribute("aSpawn", new THREE.BufferAttribute(Float32Array.from(edgeSpawn), 1));
        egeom.setAttribute("aCenter", new THREE.BufferAttribute(Float32Array.from(edgeCenter), 3));
        const lines = new THREE.LineSegments(egeom, materials.line);
        lines.frustumCulled = false;
        lines.raycast = () => {};
        part.meshEdges = lines;
        layerGroup.add(lines);
      }

      if (part.boxMesh || part.meshMesh) bucket.parts.push(part);
    }
  }

  const allParts = buckets.flatMap((b) => b.parts);
  const bounds = new THREE.Box3().setFromObject(group);

  // ---- selection outline: thick screen-space lines over the picked element ----
  const outlineMaterial = new LineMaterial({
    color: 0xffffff, linewidth: 3, depthTest: false, transparent: true,
  });
  outlineMaterial.resolution.set(window.innerWidth, window.innerHeight);
  const outline = new LineSegments2(new LineSegmentsGeometry(), outlineMaterial);
  outline.frustumCulled = false;
  outline.renderOrder = 999;
  outline.visible = false;
  outline.raycast = () => {};
  group.add(outline);

  // World-space edge segments of one element, sliced out of the baked buffers.
  function edgePositions(eid) {
    const loc = locate[eid];
    if (!loc) return null;
    const part = loc.part;
    if (loc.index !== undefined) {
      const a = part.boxEdges.geometry.getAttribute("position").array;
      return a.slice(loc.index * 24 * 3, (loc.index + 1) * 24 * 3);
    }
    const range = part.edgeRanges.get(eid);
    if (!range) return null;
    const a = part.meshEdges.geometry.getAttribute("position").array;
    return a.slice(range[0] * 3, range[1] * 3);
  }

  function setElementColor(eid, color) {
    const loc = locate[eid];
    if (!loc) return;
    if (loc.index !== undefined) {
      loc.part.boxMesh.setColorAt(loc.index, color);
      loc.part.boxMesh.instanceColor.needsUpdate = true;
    } else {
      const colAttr = loc.part.meshMesh.geometry.getAttribute("color");
      for (let i = loc.range[0]; i < loc.range[1]; i++) {
        colAttr.setXYZ(i, color.r, color.g, color.b);
      }
      colAttr.needsUpdate = true;
    }
  }

  const api = {
    group, buckets, parts: allParts, materials, bounds, locate, outline,

    setLayerVisible(li, on) { buckets[li].layerGroup.visible = on; },

    // colorFn(elementId) -> THREE.Color; stores base colors for highlight restore
    setElementColors(colorFn) {
      const c = new THREE.Color();
      for (let e = 0; e < model.count; e++) {
        c.copy(colorFn(e));
        baseColors[e * 3] = c.r; baseColors[e * 3 + 1] = c.g; baseColors[e * 3 + 2] = c.b;
        setElementColor(e, c);
      }
    },

    // Colour the active style assigned to an element (before any hover tint)
    baseColor(eid) {
      return new THREE.Color(baseColors[eid * 3], baseColors[eid * 3 + 1], baseColors[eid * 3 + 2]);
    },

    highlight(eid, color) { // color=null restores base
      const c = new THREE.Color();
      if (color === null) {
        c.setRGB(baseColors[eid * 3], baseColors[eid * 3 + 1], baseColors[eid * 3 + 2]);
      } else {
        c.copy(color);
      }
      setElementColor(eid, c);
    },

    // eid=null clears. Draws a thick outline around the selected element.
    setSelected(eid, color) {
      if (eid === null) { outline.visible = false; return; }
      const pts = edgePositions(eid);
      if (!pts) { outline.visible = false; return; }
      outline.geometry.dispose();
      outline.geometry = new LineSegmentsGeometry();
      outline.geometry.setPositions(Array.from(pts));
      if (color) outlineMaterial.color.copy(color);
      outline.visible = true;
    },

    setOutlineResolution(w, h) { outlineMaterial.resolution.set(w, h); },

    setMaterials({ fill, glass, line }) {
      materials.fill = fill;
      materials.glass = glass;
      materials.line = line;
      for (const p of allParts) {
        const m = p.glass ? glass : fill;
        if (p.boxMesh) p.boxMesh.material = m;
        if (p.meshMesh) p.meshMesh.material = m;
        if (p.boxEdges) p.boxEdges.material = line;
        if (p.meshEdges) p.meshEdges.material = line;
      }
    },

    forEachMaterial(fn) {
      fn(materials.fill); fn(materials.glass); fn(materials.line); fn(outlineMaterial);
    },

    setEdgesVisible(on) {
      for (const p of allParts) {
        if (p.boxEdges) p.boxEdges.visible = on;
        if (p.meshEdges) p.meshEdges.visible = on;
      }
    },

    setSpawnTimes(times) { // Float32Array per element
      for (const p of allParts) {
        if (p.boxMesh) {
          const a = p.boxMesh.geometry.getAttribute("aSpawn");
          for (let i = 0; i < p.boxElementIds.length; i++) a.setX(i, times[p.boxElementIds[i]]);
          a.needsUpdate = true;
        }
        if (p.boxEdges) {
          const a = p.boxEdges.geometry.getAttribute("aSpawn");
          for (let i = 0; i < p.boxElementIds.length; i++) {
            for (let k = 0; k < 24; k++) a.setX(i * 24 + k, times[p.boxElementIds[i]]);
          }
          a.needsUpdate = true;
        }
        if (p.meshMesh) {
          const a = p.meshMesh.geometry.getAttribute("aSpawn");
          for (const [eid, [v0, v1]] of p.vertexRanges) {
            for (let i = v0; i < v1; i++) a.setX(i, times[eid]);
          }
          a.needsUpdate = true;
        }
        if (p.meshEdges) {
          const a = p.meshEdges.geometry.getAttribute("aSpawn");
          for (const [eid, [v0, v1]] of p.edgeRanges) {
            for (let i = v0; i < v1; i++) a.setX(i, times[eid]);
          }
          a.needsUpdate = true;
        }
      }
    },

    pickables() {
      const out = [];
      for (const b of buckets) {
        if (!b.layerGroup.visible) continue;
        for (const p of b.parts) {
          if (p.boxMesh) out.push(p.boxMesh);
          if (p.meshMesh) out.push(p.meshMesh);
        }
      }
      return out;
    },

    elementOf(intersection) {
      const obj = intersection.object;
      for (const p of allParts) {
        if (obj === p.boxMesh) return p.boxElementIds[intersection.instanceId];
        if (obj === p.meshMesh) return p.faceElement[intersection.faceIndex];
      }
      return null;
    },

    dispose() {
      group.traverse((o) => { if (o.geometry) o.geometry.dispose(); });
      outlineMaterial.dispose();
      group.removeFromParent();
    },
  };

  // Default colors: by layer
  api.setElementColors((e) => new THREE.Color(LAYER_COLORS[model.layer[e]]));
  return api;
}
