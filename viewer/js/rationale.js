// Design-rationale panel: renders a run's markdown document (Fable runs ship
// one, see tools/export_all_models.py) in a collapsible, scrollable box.
// Numbered headings carry data-section so callouts (callouts.js) can scroll
// to a passage; callout quotes are wrapped in <mark> (callout-data.js).
// Pure DOM - no three.js imports.

import { renderMarkdown } from "./markdown.js";
import { markQuotes } from "./callout-data.js";
import { isMobile } from "./gui.js";

const FLASH_MS = 1600;

export function makeDocPanel(host, title = "DESIGN RATIONALE") {
  const root = document.createElement("div");
  root.id = "doc";
  root.hidden = true;
  root.innerHTML = `<h2>${title}</h2><div class="md"></div>`;
  if (isMobile()) root.classList.add("closed");
  const md = root.querySelector(".md");
  host.appendChild(root);

  const cache = new Map(); // path -> markdown source
  let current = null;
  const toggleListeners = [];
  const sectionListeners = [];
  let hoveredSection = null;

  const isOpen = () => !root.hidden && !root.classList.contains("closed");
  const emitToggle = () => { for (const fn of toggleListeners) fn(isOpen()); };

  root.querySelector("h2").addEventListener("click", () => {
    root.classList.toggle("closed");
    emitToggle();
  });

  // Heading hover -> section listeners (null when leaving headings)
  md.addEventListener("pointerover", (ev) => {
    const h = ev.target.closest("[data-section]");
    const section = h ? h.dataset.section : null;
    if (section === hoveredSection) return;
    hoveredSection = section;
    for (const fn of sectionListeners) fn(section);
  });
  md.addEventListener("pointerleave", () => {
    if (hoveredSection === null) return;
    hoveredSection = null;
    for (const fn of sectionListeners) fn(null);
  });

  return {
    el: root,
    get isOpen() { return isOpen(); },
    onToggle(fn) { toggleListeners.push(fn); },
    onSectionHover(fn) { sectionListeners.push(fn); },

    // path=null hides the panel. callouts = the run's authored callouts
    // (their quotes get marked). Loads lazily and caches per document.
    async show(path, callouts = null) {
      current = path;
      if (!path) { root.hidden = true; emitToggle(); return; }
      let source = cache.get(path);
      if (source === undefined) {
        try {
          const res = await fetch(path);
          if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
          source = await res.text();
        } catch (err) {
          console.warn(`rationale: ${path}: ${err.message}`);
          if (current === path) { root.hidden = true; emitToggle(); }
          return;
        }
        cache.set(path, source);
      }
      if (current !== path) return; // superseded while loading
      md.innerHTML = renderMarkdown(markQuotes(source, callouts?.callouts));
      md.scrollTop = 0;
      root.hidden = false;
      emitToggle();
    },

    // Open the panel and scroll to a section heading (or to the callout's
    // marked quote inside it), flashing the target.
    scrollToSection(section, calloutId = null) {
      if (root.hidden) return;
      if (root.classList.contains("closed")) {
        root.classList.remove("closed");
        emitToggle();
      }
      const heading = md.querySelector(`[data-section="${CSS.escape(section)}"]`);
      const mark = calloutId ? md.querySelector(`mark[data-callout="${CSS.escape(calloutId)}"]`) : null;
      const target = mark ?? heading;
      if (!target) return;
      target.scrollIntoView({ block: "center", behavior: "smooth" });
      for (const el of [heading, mark]) {
        if (!el) continue;
        el.classList.add("flash");
        setTimeout(() => el.classList.remove("flash"), FLASH_MS);
      }
    },
  };
}
