// Labels for the knolled arrangements (knolling.js): one tag per layer band
// on the band's right-hand side - layer name, piece count and length range -
// so the bands read as a list down the sheet in the top view. Hovering a tag
// tints the band's elements. Shares the rationale callouts' tag and leader
// line styling; shown in place of them while the elements sit in a grid.

import * as THREE from "three";
import { LAYERS } from "./model-data.js";

const SVG_NS = "http://www.w3.org/2000/svg";
const LEAD = 28; // px from the band edge to the tag

// deps: views (camera + quad flag), canvas, getSceneApi, getStyles
export function makeBandLabels(host, { views, canvas, getSceneApi, getStyles }) {
  const svg = document.createElementNS(SVG_NS, "svg");
  svg.id = "band-lines";
  host.appendChild(svg);

  let layout = null; // the settled arrangement, or null
  let visible = false;
  let items = []; // {band, el, line, dot, on}
  let tinted = null;
  const _v = new THREE.Vector3();

  function tint(item, on) {
    const api = getSceneApi();
    if (!api) return;
    const color = on ? getStyles().hoverColor : null;
    for (const eid of item.band.ids) api.highlight(eid, color);
  }

  function setTinted(item) {
    if (tinted === item) return;
    if (tinted) { tint(tinted, false); tinted.el.classList.remove("active"); }
    tinted = item;
    if (item) { tint(item, true); item.el.classList.add("active"); }
  }

  function clear() {
    setTinted(null);
    for (const it of items) { it.el.remove(); it.line.remove(); it.dot.remove(); }
    items = [];
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

  const fmt = (m) => m.toFixed(2);

  function build() {
    clear();
    if (!layout?.bands) return;
    for (const band of layout.bands) {
      const el = document.createElement("div");
      el.className = "callout band";
      const range = band.maxLen - band.minLen < 0.005
        ? `${fmt(band.maxLen)} m` : `${fmt(band.minLen)} to ${fmt(band.maxLen)} m`;
      const name = document.createElement("b");
      name.textContent = `${LAYERS[band.layer]} · ${band.count}`;
      el.append(name, document.createElement("br"), range);
      el.hidden = true;
      host.appendChild(el);
      const line = document.createElementNS(SVG_NS, "line");
      const dot = document.createElementNS(SVG_NS, "circle");
      dot.setAttribute("r", "3");
      svg.append(line, dot);
      const item = { band, el, line, dot, on: false };
      el.addEventListener("pointerenter", () => setTinted(item));
      el.addEventListener("pointerleave", () => setTinted(null));
      items.push(item);
    }
  }

  return {
    // layout: the arrangement the elements have settled in, null when they
    // are in the model or in flight
    setLayout(l) {
      if (l === layout) return;
      layout = l;
      build();
    },

    setVisible(on) {
      visible = on;
      if (!on) { hideAll(); setTinted(null); }
    },

    tick() {
      const api = getSceneApi();
      if (!visible || !layout || views.quad || !api) { hideAll(); return; }
      const camera = views.camera;
      const r = canvas.getBoundingClientRect();
      const edge = layout.bounds.max[0]; // tags line up on the sheet's right edge
      for (const it of items) {
        const b = it.band;
        const y = (b.min[1] + b.max[1]) / 2;
        _v.set(b.max[0], y, b.min[2]).project(camera); // dot: the band's own edge
        const sx = r.left + (_v.x * 0.5 + 0.5) * r.width;
        const sy = r.top + (-_v.y * 0.5 + 0.5) * r.height;
        _v.set(edge, y, b.min[2]).project(camera); // lead runs on to the sheet edge
        const ex = r.left + (_v.x * 0.5 + 0.5) * r.width + LEAD;
        const ey = r.top + (-_v.y * 0.5 + 0.5) * r.height;
        const inside = _v.z < 1 && sx >= r.left && sx <= r.right && sy >= r.top && sy <= r.bottom;
        if (!inside || !api.buckets[b.layer].layerGroup.visible) {
          if (it.on) { it.on = false; it.el.hidden = true; it.line.setAttribute("visibility", "hidden"); it.dot.setAttribute("visibility", "hidden"); }
          continue;
        }
        it.on = true;
        it.el.hidden = false;
        // .callout is centred on (left, top): put its left edge at the lead's end
        it.el.style.left = `${ex + it.el.offsetWidth / 2}px`;
        it.el.style.top = `${ey}px`;
        it.line.setAttribute("visibility", "visible");
        it.line.setAttribute("x1", sx); it.line.setAttribute("y1", sy);
        it.line.setAttribute("x2", ex); it.line.setAttribute("y2", ey);
        it.dot.setAttribute("visibility", "visible");
        it.dot.setAttribute("cx", sx); it.dot.setAttribute("cy", sy);
      }
    },
  };
}
