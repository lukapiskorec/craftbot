// Small Markdown -> HTML renderer for the design rationale documents. Covers
// what those files use: ATX headings, paragraphs, nested -/1. lists, pipe
// tables, fenced code, blockquotes, rules, and inline code/bold/italic/links.
// No DOM - unit-tested with `node --test viewer/test/*.test.mjs`.

function escapeHtml(s) {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

export function inline(text) {
  const codes = [];
  let s = escapeHtml(text).replace(/`([^`]+)`/g, (_, c) => {
    codes.push(c);
    return `\u0000${codes.length - 1}\u0000`;
  });
  s = s.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  s = s.replace(/(^|[^*\w])\*([^*\n]+)\*(?!\w)/g, "$1<em>$2</em>");
  s = s.replace(/(^|[^_\w])_([^_\n]+)_(?!\w)/g, "$1<em>$2</em>");
  s = s.replace(/\[([^\]]+)\]\(([^)\s]+)\)/g,
    '<a href="$2" target="_blank" rel="noopener">$1</a>');
  return s.replace(/\u0000(\d+)\u0000/g, (_, i) => `<code>${codes[i]}</code>`);
}

const LIST_RE = /^(\s*)([-*+]|\d+\.)\s+(.*)$/;

function renderList(items) {
  // items: [{indent, marker, text}], one nesting level per deeper indent
  const ordered = /\d/.test(items[0].marker);
  const tag = ordered ? "ol" : "ul";
  const base = items[0].indent;
  let html = `<${tag}>`;
  let i = 0;
  while (i < items.length) {
    html += `<li>${inline(items[i].text)}`;
    i++;
    const sub = [];
    while (i < items.length && items[i].indent > base) sub.push(items[i++]);
    if (sub.length) html += renderList(sub);
    html += "</li>";
  }
  return `${html}</${tag}>`;
}

function renderTable(rows) {
  const cells = (line) => line.trim().replace(/^\|/, "").replace(/\|$/, "")
    .split("|").map((c) => inline(c.trim()));
  const head = cells(rows[0]).map((c) => `<th>${c}</th>`).join("");
  const body = rows.slice(2).map((r) =>
    `<tr>${cells(r).map((c) => `<td>${c}</td>`).join("")}</tr>`).join("");
  return `<table><thead><tr>${head}</tr></thead><tbody>${body}</tbody></table>`;
}

export function renderMarkdown(md) {
  const lines = md.replace(/\r\n?/g, "\n").split("\n");
  const out = [];
  const para = [];
  const flush = () => {
    if (para.length) out.push(`<p>${inline(para.join(" "))}</p>`);
    para.length = 0;
  };
  let i = 0;
  while (i < lines.length) {
    const line = lines[i];
    if (/^\s*```/.test(line)) {
      flush();
      const buf = [];
      i++;
      while (i < lines.length && !/^\s*```/.test(lines[i])) buf.push(lines[i++]);
      i++;
      out.push(`<pre><code>${escapeHtml(buf.join("\n"))}</code></pre>`);
      continue;
    }
    const h = /^(#{1,6})\s+(.*?)\s*#*\s*$/.exec(line);
    if (h) {
      flush();
      out.push(`<h${h[1].length}>${inline(h[2])}</h${h[1].length}>`);
      i++;
      continue;
    }
    if (/^\s*([-*_])(\s*\1){2,}\s*$/.test(line)) {
      flush();
      out.push("<hr>");
      i++;
      continue;
    }
    if (/^\s*\|/.test(line) && i + 1 < lines.length && /^\s*\|?\s*:?-{2,}/.test(lines[i + 1])) {
      flush();
      const rows = [];
      while (i < lines.length && /^\s*\|/.test(lines[i])) rows.push(lines[i++]);
      out.push(renderTable(rows));
      continue;
    }
    if (LIST_RE.test(line)) {
      flush();
      const items = [];
      while (i < lines.length) {
        const m = LIST_RE.exec(lines[i]);
        if (m) {
          items.push({ indent: m[1].length, marker: m[2], text: m[3] });
        } else if (/^\s+\S/.test(lines[i]) && items.length) {
          items[items.length - 1].text += ` ${lines[i].trim()}`; // continuation
        } else {
          break;
        }
        i++;
      }
      out.push(renderList(items));
      continue;
    }
    if (/^\s*>/.test(line)) {
      flush();
      const buf = [];
      while (i < lines.length && /^\s*>/.test(lines[i])) {
        buf.push(lines[i++].replace(/^\s*>\s?/, ""));
      }
      out.push(`<blockquote>${renderMarkdown(buf.join("\n"))}</blockquote>`);
      continue;
    }
    if (!line.trim()) {
      flush();
      i++;
      continue;
    }
    para.push(line.trim());
    i++;
  }
  flush();
  return out.join("\n");
}
