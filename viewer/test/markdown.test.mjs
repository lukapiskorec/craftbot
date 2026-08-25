import test from "node:test";
import assert from "node:assert/strict";
import { renderMarkdown, inline } from "../js/markdown.js";

test("inline: code keeps its markers, emphasis and links render", () => {
  assert.equal(inline("a `x*y*_z_` b"), "a <code>x*y*_z_</code> b");
  assert.equal(inline("**bold** and *em* and _em_"),
    "<strong>bold</strong> and <em>em</em> and <em>em</em>");
  assert.equal(inline("see [docs](https://x.y/z)"),
    'see <a href="https://x.y/z" target="_blank" rel="noopener">docs</a>');
  assert.equal(inline("1 < 2 & 3"), "1 &lt; 2 &amp; 3");
  assert.equal(inline("layer 3 has 4 posts"), "layer 3 has 4 posts");
});

test("renderMarkdown: headings, paragraphs, rule", () => {
  const html = renderMarkdown("# Title\n\ntext line one\nline two\n\n---\n\n## Sub ##\n");
  assert.equal(html, "<h1>Title</h1>\n<p>text line one line two</p>\n<hr>\n<h2>Sub</h2>");
});

test("renderMarkdown: nested list with continuation lines", () => {
  const html = renderMarkdown("- one\n  more of one\n  - inner\n- two\n\n1. first\n2. second");
  assert.equal(html,
    "<ul><li>one more of one<ul><li>inner</li></ul></li><li>two</li></ul>\n"
    + "<ol><li>first</li><li>second</li></ol>");
});

test("renderMarkdown: pipe table", () => {
  const html = renderMarkdown("| a | b |\n|---|---:|\n| 1 | `x` |\n");
  assert.equal(html,
    "<table><thead><tr><th>a</th><th>b</th></tr></thead>"
    + "<tbody><tr><td>1</td><td><code>x</code></td></tr></tbody></table>");
});

test("renderMarkdown: fenced code is escaped verbatim, blockquote nests", () => {
  const html = renderMarkdown("```\nif a < b: *x*\n```\n> quoted **q**\n> more");
  assert.equal(html,
    "<pre><code>if a &lt; b: *x*</code></pre>\n"
    + "<blockquote><p>quoted <strong>q</strong> more</p></blockquote>");
});
