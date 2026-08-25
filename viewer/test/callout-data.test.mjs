import test from "node:test";
import assert from "node:assert/strict";
import {
  globToRegExp, resolveMatch, sectionOf, sectionRange, findQuote, markQuotes,
} from "../js/callout-data.js";
import { renderMarkdown } from "../js/markdown.js";

test("globToRegExp: *, ?, alternatives, anchored", () => {
  const re = globToRegExp("Truss_*_W?|Purlin_*");
  assert.ok(re.test("Truss_3_W1"));
  assert.ok(re.test("Purlin_S_2"));
  assert.ok(!re.test("Truss_3_Gusset_1"));
  assert.ok(!re.test("XPurlin_S_2"));
  assert.ok(globToRegExp("P?_*").test("P1_Stud_3") && !globToRegExp("P?_*").test("Ply_P1"));
});

test("resolveMatch: names and optional collection", () => {
  const model = {
    count: 3, names: ["Post_1", "Post_2", "Rail_1"],
    collections: ["", "Structure/Foundation"], collection: Uint16Array.from([1, 0, 0]),
  };
  assert.deepEqual([...resolveMatch(model, { names: "Post_*" })], [0, 1]);
  assert.deepEqual([...resolveMatch(model, { names: "Post_*", collection: "Structure/*" })], [0]);
});

test("sectionOf: numbered headings", () => {
  assert.equal(sectionOf("5.1 Truss members as clipped strips"), "5.1");
  assert.equal(sectionOf("5b. Structural improvements"), "5b");
  assert.equal(sectionOf("2b. Comparison"), "2b");
  assert.equal(sectionOf("Experiment 04 - Fable run"), null);
});

test("sectionRange: body up to the next heading of the same or higher level", () => {
  const md = "## 5. Core\nintro\n### 5.1 A\naaa\n### 5.2 B\nbbb\n## 6. Next\nccc\n";
  assert.equal(md.slice(...sectionRange(md, "5")), "\nintro\n### 5.1 A\naaa\n### 5.2 B\nbbb\n");
  assert.equal(md.slice(...sectionRange(md, "5.1")), "\naaa\n");
  assert.equal(md.slice(...sectionRange(md, "6")), "\nccc\n");
  assert.equal(sectionRange(md, "7"), null);
});

const MD = `# Doc
## 2. Inputs
Rise 5 × 182 with the same 230 run.
### 5.1 Heels
From v04 the heel is 28 mm
outside the wall face.
## 6. Geometry
stair 800, 5 × 182 / 230, landing.
`;

test("findQuote: whitespace-insensitive, scoped to the section", () => {
  const hit = findQuote(MD, "5.1", "the heel is 28 mm outside the wall face");
  assert.ok(hit && MD.slice(hit[0], hit[1]).startsWith("the heel is 28 mm\noutside"));
  assert.equal(findQuote(MD, "2", "5 × 182 / 230"), null); // only in section 6
  assert.ok(findQuote(MD, "6", "5 × 182 / 230"));
  assert.equal(findQuote(MD, "9", "anything"), null);
});

test("markQuotes + renderMarkdown: headings get data-section, quotes become marks", () => {
  const html = renderMarkdown(markQuotes(MD, [
    { id: "heel", section: "5.1", quote: "the heel is 28 mm outside the wall face" },
    { id: "stair", section: "6", quote: "5 × 182 / 230" },
  ]));
  assert.ok(html.includes('<h3 data-section="5.1">5.1 Heels</h3>'));
  assert.ok(html.includes('<h2 data-section="2">2. Inputs</h2>'));
  assert.ok(html.includes('<mark class="ref" data-callout="heel">the heel is 28 mm outside the wall face</mark>'));
  assert.ok(html.includes('<mark class="ref" data-callout="stair">5 × 182 / 230</mark>'));
  assert.ok(!/[]/.test(html));
});
