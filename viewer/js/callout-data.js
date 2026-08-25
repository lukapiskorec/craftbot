// Pure logic for design-rationale callouts (no DOM, no three.js): element
// matching and quote marking. Mirrors tools/callouts.py, which validates the
// authored files. Unit-tested with `node --test viewer/test/*.test.mjs`.

// "Truss_*_W?|Purlin_*" -> anchored RegExp. `*` any run, `?` one char,
// `|` separates alternatives.
export function globToRegExp(glob) {
  const alts = String(glob).split("|").map((g) => g.trim()).filter(Boolean)
    .map((g) => g.replace(/[.+^${}()[\]\\]/g, "\\$&").replace(/\*/g, ".*").replace(/\?/g, "."));
  return new RegExp(`^(?:${alts.join("|")})$`);
}

// Element ids of `model` selected by a callout match spec
// {names: glob, collection?: glob} -> Uint32Array
export function resolveMatch(model, match) {
  const nameRe = globToRegExp(match.names || "*");
  const collRe = match.collection ? globToRegExp(match.collection) : null;
  const ids = [];
  for (let e = 0; e < model.count; e++) {
    if (!nameRe.test(model.names[e])) continue;
    if (collRe && !collRe.test(model.collections[model.collection[e]])) continue;
    ids.push(e);
  }
  return Uint32Array.from(ids);
}

// Section token of a heading line's text: "5.1 Truss..." -> "5.1", "5b. X" -> "5b"
export function sectionOf(headingText) {
  const m = /^(\d+[a-z]?(?:\.\d+)*)\.?\s/.exec(headingText);
  return m ? m[1] : null;
}

// [start, end] character range of a section's body: after its heading up to
// the next heading of the same or a higher level. null if not found.
export function sectionRange(md, section) {
  const re = /^(#{1,6})\s+(.*?)\s*#*\s*$/gm;
  let m, start = -1, level = 0;
  while ((m = re.exec(md))) {
    if (start < 0) {
      if (sectionOf(m[2]) === section) { start = m.index + m[0].length; level = m[1].length; }
    } else if (m[1].length <= level) {
      return [start, m.index];
    }
  }
  return start < 0 ? null : [start, md.length];
}

// Whitespace-insensitive search for `quote` inside its section.
// Returns [start, end] or null.
export function findQuote(md, section, quote) {
  const range = sectionRange(md, section);
  if (!range) return null;
  const pattern = quote.trim().split(/\s+/)
    .map((w) => w.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")).join("\\s+");
  const m = new RegExp(pattern).exec(md.slice(range[0], range[1]));
  return m ? [range[0] + m.index, range[0] + m.index + m[0].length] : null;
}

// Wrap every callout quote in the markdown source with control-character
// markers that markdown.js turns into <mark data-callout="id">.
export function markQuotes(md, callouts) {
  const spans = [];
  for (const c of callouts || []) {
    if (!c.quote) continue;
    const hit = findQuote(md, c.section, c.quote);
    if (hit) spans.push({ id: c.id, start: hit[0], end: hit[1] });
  }
  spans.sort((a, b) => b.start - a.start); // splice from the back
  let out = md;
  for (const s of spans) {
    out = `${out.slice(0, s.start)}${s.id}${out.slice(s.start, s.end)}${out.slice(s.end)}`;
  }
  return out;
}
