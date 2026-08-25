// Retro terminal GUI panel. Pure DOM - no three.js imports.
// makePanel(root) returns a section factory; callers compose controls.

export function makePanel(root, title = "CRAFTBOT VIEWER") {
  root.innerHTML = "";
  const header = document.createElement("header");
  header.innerHTML = `${title} &gt; <span class="cursor">█</span>`;
  root.appendChild(header);

  // className hooks section-specific layout (e.g. the two-column layer grid)
  function section(name, open = true, className = "") {
    const sec = document.createElement("div");
    sec.className = `gui-section ${className}${open ? " open" : ""}`;
    const h2 = document.createElement("h2");
    h2.textContent = name;
    h2.addEventListener("click", () => sec.classList.toggle("open"));
    const body = document.createElement("div");
    body.className = "body";
    sec.append(h2, body);
    root.appendChild(sec);

    function row(labelText) {
      const r = document.createElement("div");
      r.className = "gui-row";
      if (labelText !== null) {
        const label = document.createElement("label");
        label.textContent = labelText;
        r.appendChild(label);
      }
      body.appendChild(r);
      return r;
    }

    return {
      el: sec,
      body,

      addSelect(label, options, onChange) {
        const r = row(label);
        const sel = document.createElement("select");
        r.appendChild(sel);
        const api = {
          el: sel,
          setOptions(opts, value) {
            sel.innerHTML = "";
            for (const o of opts) {
              const opt = document.createElement("option");
              opt.value = o.value;
              opt.textContent = o.label;
              sel.appendChild(opt);
            }
            if (value !== undefined) sel.value = value;
          },
          get value() { return sel.value; },
          set(value) { sel.value = value; },
        };
        api.setOptions(options);
        sel.addEventListener("change", () => onChange(sel.value));
        return api;
      },

      // The whole row is a <label>, so the name toggles the box too.
      addToggle(label, checked, onChange) {
        const r = document.createElement("label");
        r.className = "gui-row gui-toggle";
        body.appendChild(r);
        const box = document.createElement("input");
        box.type = "checkbox";
        box.checked = checked;
        box.addEventListener("change", () => onChange(box.checked));
        const span = document.createElement("span");
        span.textContent = label;
        r.append(box, span);
        return { set(v) { box.checked = v; }, get value() { return box.checked; } };
      },

      // readout(value) -> text shown after the slider (omit for none)
      addSlider(label, min, max, value, onChange, { step = "any", readout = null } = {}) {
        const r = row(label);
        const input = document.createElement("input");
        input.type = "range";
        input.min = min; input.max = max; input.value = value;
        input.step = step;
        r.appendChild(input);
        let out = null;
        if (readout) {
          out = document.createElement("span");
          out.className = "readout";
          r.appendChild(out);
        }
        const show = () => { if (out) out.textContent = readout(parseFloat(input.value)); };
        show();
        input.addEventListener("input", () => { show(); onChange(parseFloat(input.value)); });
        return {
          set(v) { input.value = v; show(); },
          setRange(lo, hi) { input.min = lo; input.max = hi; show(); },
          el: input,
        };
      },

      addButtons(labels, onClick, { radio = false, active = null } = {}) {
        const r = row(null);
        r.style.flexWrap = "wrap";
        const btns = new Map();
        for (const label of labels) {
          const b = document.createElement("button");
          b.textContent = label;
          b.addEventListener("click", () => {
            if (radio) api.setActive(label);
            onClick(label);
          });
          r.appendChild(b);
          btns.set(label, b);
        }
        const api = {
          setActive(label) {
            for (const [l, b] of btns) b.classList.toggle("active", l === label);
          },
        };
        if (active) api.setActive(active);
        return api;
      },

      addInfo() {
        const div = document.createElement("div");
        div.className = "info-line";
        body.appendChild(div);
        return { set(html) { div.innerHTML = html; } };
      },

      addTable(headers) { return makeTable(body, headers); },
    };
  }

  return { section };
}

// Standalone stats table - used both inside a section and in the always-visible
// takeoff block at the top of the screen.
export function makeTable(root, headers) {
  const t = document.createElement("table");
  t.className = "stats";
  const thead = document.createElement("thead");
  thead.innerHTML = `<tr>${headers.map((h) => `<th>${h}</th>`).join("")}</tr>`;
  const tbody = document.createElement("tbody");
  t.append(thead, tbody);
  root.appendChild(t);
  return {
    set(rows) { // rows: [{cells: [..], total?: bool}]
      tbody.innerHTML = rows.map((r) =>
        `<tr${r.total ? ' class="total"' : ""}>${r.cells.map((c) => `<td>${c}</td>`).join("")}</tr>`,
      ).join("");
    },
  };
}

export function fmtBytes(n) {
  return n >= 1048576 ? `${(n / 1048576).toFixed(1)} MB` : `${(n / 1024).toFixed(1)} KB`;
}
