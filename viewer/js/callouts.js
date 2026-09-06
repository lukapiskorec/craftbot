// Design-rationale callouts: tags over the model that point at passages of
// the DESIGN RATIONALE document. Authored per Fable run in
// experiments/<exp>/Fable/experiment_NN_fable_callouts.json (validated by
// tools/callouts.py), resolved here against whatever iteration is loaded -
// a callout whose elements do not exist in this iteration is not shown.
//
// Tag = DOM box (hover-tag style) with an SVG leader line to the anchor:
// the centroid of the matched elements, or the matched element nearest the
// camera ("nearest" - for scattered sets like every bead). Hovering a tag
// tints its elements; clicking pins the tag (bigger, keeps the hover colour,
// its quote stays lit in the document) and scrolls to the passage. Clicking
// the pinned tag again releases it.

import * as THREE from "three";
import { resolveMatch } from "./callout-data.js";

const TAG_OFFSET = 90; // px from the anchor, away from the model centre
const SVG_NS = "http://www.w3.org/2000/svg";

// deps: views (camera + quad flag), canvas, getSceneApi, getStyles, docPanel
export function makeCallouts(host, { views, canvas, getSceneApi, getStyles, docPanel }) {
  const svg = document.createElementNS(SVG_NS, "svg");
  svg.id = "callout-lines";
  host.appendChild(svg);

  let data = null; // authored callouts of the current run
  let model = null;
  let visible = false;
  let suspended = false; // elements are knolled: their anchors are wrong until they return
  let items = []; // resolved: {c, ids, layers, centroid, el, line, dot, sx, sy, tx, ty, on}
  let tinted = null; // item whose elements are currently highlighted
  let hovered = null; // pointer is over this tag (or its heading in the doc)
  let pinned = null; // item clicked open; survives the pointer leaving
  const _v = new THREE.Vector3();
  const _p = new THREE.Vector3();

  function clear() {
    for (const it of items) { it.el.remove(); it.line.remove(); it.dot.remove(); }
    items = [];
    tinted = hovered = null;
    setPinned(null);
  }

  function tint(item, on) {
    const api = getSceneApi();
    if (!api) return;
    const color = on ? getStyles().hoverColor : null;
    for (const eid of item.ids) api.highlight(eid, color);
  }

  // The hovered tag wins over the pinned one, so only one set is ever tinted
  function refreshTint() {
    const want = hovered ?? pinned;
    if (tinted === want) return;
    if (tinted) { tint(tinted, false); tinted.el.classList.remove("active"); }
    tinted = want;
    if (want) { tint(want, true); want.el.classList.add("active"); }
  }

  function setHovered(item) {
    hovered = item;
    refreshTint();
  }

  function setPinned(item) {
    if (pinned === item) return;
    if (pinned) pinned.el.classList.remove("pinned");
    pinned = item;
    if (pinned) pinned.el.classList.add("pinned");
    docPanel.setPinnedCallout(pinned ? pinned.c.id : null);
    refreshTint();
  }

  function resolve() {
    clear();
    if (!data || !model) return;
    for (const c of data.callouts || []) {
      const ids = resolveMatch(model, c.match || {});
      if (!ids.length) continue;
      const centroid = new THREE.Vector3();
      const layers = new Set();
      for (const eid of ids) {
        centroid.x += model.centers[eid * 3];
        centroid.y += model.centers[eid * 3 + 1];
        centroid.z += model.centers[eid * 3 + 2];
        layers.add(model.layer[eid]);
      }
      centroid.divideScalar(ids.length);
      const el = document.createElement("div");
      el.className = "callout";
      el.dataset.callout = c.id;
      el.textContent = c.label;
      el.hidden = true;
      host.appendChild(el);
      const line = document.createElementNS(SVG_NS, "line");
      const dot = document.createElementNS(SVG_NS, "circle");
      dot.setAttribute("r", "3");
      svg.append(line, dot);
      const item = { c, ids, layers, centroid, el, line, dot, sx: 0, sy: 0, tx: 0, ty: 0, on: false };
      el.addEventListener("pointerenter", () => setHovered(item));
      el.addEventListener("pointerleave", () => setHovered(null));
      el.addEventListener("click", () => {
        const pin = pinned !== item;
        setPinned(pin ? item : null);
        if (pin) docPanel.scrollToSection(c.section, c.id);
      });
      items.push(item);
    }
  }

  function anchorOf(item, camera) {
    if (item.c.anchor !== "nearest") return item.centroid;
    let best = Infinity;
    for (const eid of item.ids) {
      _v.set(model.centers[eid * 3], model.centers[eid * 3 + 1], model.centers[eid * 3 + 2]);
      const d = _v.distanceToSquared(camera.position);
      if (d < best) { best = d; _p.copy(_v); }
    }
    return _p;
  }

  function hideAll() {
    for (const it of items) {
      if (!it.on) continue;
      it.on = false;
      it.el.hidden = true;
      it.line.setAttribute("visibility", "hidden");
      it.dot.setAttribute("visibility", "hidden");
    }
  }

  function layersShown(item) {
    const api = getSceneApi();
    for (const li of item.layers) if (api.buckets[li].layerGroup.visible) return true;
    return false;
  }

  const api = {
    get visible() { return visible; },

    setVisible(on) {
      visible = on;
      if (!on) { hideAll(); setHovered(null); setPinned(null); }
    },

    setSuspended(on) { suspended = on; },

    setData(d) { data = d; resolve(); },

    setModel(m) { model = m; resolve(); },

    // Doc heading hover -> emphasise the callouts of that section
    highlightSection(section) {
      setHovered(section ? items.find((it) => it.c.section === section) ?? null : null);
    },

    tick() {
      if (!visible || suspended || !items.length || views.quad || !getSceneApi()) { hideAll(); return; }
      const camera = views.camera;
      const r = canvas.getBoundingClientRect();
      getSceneApi().bounds.getCenter(_v).project(camera);
      const cx = r.left + (_v.x * 0.5 + 0.5) * r.width;
      const cy = r.top + (-_v.y * 0.5 + 0.5) * r.height;
      const shown = [];
      for (const it of items) {
        const p = anchorOf(it, camera);
        _v.copy(p).project(camera);
        const sx = r.left + (_v.x * 0.5 + 0.5) * r.width;
        const sy = r.top + (-_v.y * 0.5 + 0.5) * r.height;
        const inside = _v.z < 1 && sx >= r.left && sx <= r.right && sy >= r.top && sy <= r.bottom;
        if (!inside || !layersShown(it)) {
          if (it.on) { it.on = false; it.el.hidden = true; it.line.setAttribute("visibility", "hidden"); it.dot.setAttribute("visibility", "hidden"); }
          continue;
        }
        let dx = sx - cx, dy = sy - cy;
        const len = Math.hypot(dx, dy);
        if (len < 1) { dx = 1; dy = -1; } else { dx /= len; dy /= len; }
        it.sx = sx; it.sy = sy;
        it.tx = sx + dx * TAG_OFFSET; it.ty = sy + dy * TAG_OFFSET;
        shown.push(it);
      }
      // Greedy de-overlap: in vertical order, push each tag below every
      // earlier tag it would cover (repeat, since a push can create a new
      // overlap with another earlier tag).
      shown.sort((a, b) => a.ty - b.ty);
      for (let i = 1; i < shown.length; i++) {
        const b = shown[i];
        for (let pass = 0, moved = true; moved && pass < 8; pass++) {
          moved = false;
          for (let j = 0; j < i; j++) {
            const a = shown[j];
            const w = (a.el.offsetWidth + b.el.offsetWidth) / 2 + 4;
            const h = (a.el.offsetHeight + b.el.offsetHeight) / 2 + 4;
            if (Math.abs(a.tx - b.tx) < w && Math.abs(b.ty - a.ty) < h) { b.ty = a.ty + h; moved = true; }
          }
        }
      }
      for (const it of shown) {
        it.on = true;
        it.el.hidden = false;
        it.el.style.left = `${it.tx}px`;
        it.el.style.top = `${it.ty}px`;
        it.line.setAttribute("visibility", "visible");
        it.line.setAttribute("x1", it.sx); it.line.setAttribute("y1", it.sy);
        it.line.setAttribute("x2", it.tx); it.line.setAttribute("y2", it.ty);
        it.dot.setAttribute("visibility", "visible");
        it.dot.setAttribute("cx", it.sx); it.dot.setAttribute("cy", it.sy);
      }
    },
  };
  return api;
}
