// Design-rationale panel: renders a run's markdown document (Fable runs ship
// one, see tools/export_all_models.py) in a collapsible, scrollable box.
// Pure DOM - no three.js imports.

import { renderMarkdown } from "./markdown.js";

export function makeDocPanel(host, title = "DESIGN RATIONALE") {
  const root = document.createElement("div");
  root.id = "doc";
  root.hidden = true;
  root.innerHTML = `<h2>${title}</h2><div class="md"></div>`;
  root.querySelector("h2").addEventListener("click", () => root.classList.toggle("closed"));
  const md = root.querySelector(".md");
  host.appendChild(root);

  const cache = new Map(); // path -> html
  let current = null;

  return {
    el: root,

    // path=null hides the panel. Loads lazily and caches per document.
    async show(path) {
      current = path;
      if (!path) { root.hidden = true; return; }
      let html = cache.get(path);
      if (!html) {
        try {
          const res = await fetch(path);
          if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
          html = renderMarkdown(await res.text());
        } catch (err) {
          console.warn(`rationale: ${path}: ${err.message}`);
          if (current === path) root.hidden = true;
          return;
        }
        cache.set(path, html);
      }
      if (current !== path) return; // superseded while loading
      md.innerHTML = html;
      md.scrollTop = 0;
      root.hidden = false;
    },
  };
}
