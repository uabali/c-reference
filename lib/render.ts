export function escapeHtml(value: string) {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

export function escapeAttr(value: string) {
  return escapeHtml(value).replaceAll('"', "&quot;");
}

export function splitFrontmatter(source: string): {
  meta: Record<string, string>;
  body: string;
} {
  if (!source.startsWith("---\n")) return { meta: {}, body: source };
  const end = source.indexOf("\n---\n", 4);
  if (end < 0) return { meta: {}, body: source };
  const meta: Record<string, string> = {};
  for (const line of source.slice(4, end).split("\n")) {
    const match = /^([A-Za-z0-9_]+):\s?(.*)$/.exec(line);
    if (!match) continue;
    try {
      const parsed = JSON.parse(match[2]) as unknown;
      meta[match[1]] = typeof parsed === "string" ? parsed : String(parsed);
    } catch {
      meta[match[1]] = match[2];
    }
  }
  return { meta, body: source.slice(end + 5) };
}

export function renderBody(body: string) {
  const lines = body.split("\n");
  const out: string[] = [];
  let buffer: string[] = [];
  const flush = () => {
    if (buffer.length) {
      out.push(buffer.join("\n"));
      buffer = [];
    }
  };
  let i = 0;
  while (i < lines.length) {
    const open = /^(```+)([A-Za-z0-9_+-]*)\s*$/.exec(lines[i] ?? "");
    if (!open) {
      buffer.push(lines[i] ?? "");
      i += 1;
      continue;
    }
    flush();
    const fence = open[1] ?? "```";
    const lang = open[2] || "text";
    const code: string[] = [];
    i += 1;
    while (i < lines.length && (lines[i] ?? "").trim() !== fence) {
      code.push(lines[i] ?? "");
      i += 1;
    }
    if (i < lines.length) i += 1;
    out.push(
      `<pre class="codeblock" data-lang="${escapeAttr(lang)}"><code class="language-${escapeAttr(lang)}">${escapeHtml(code.join("\n"))}</code></pre>`,
    );
  }
  flush();
  return out.join("\n");
}
