import assert from "node:assert/strict";
import test from "node:test";
import { renderBody, splitFrontmatter } from "../lib/render.ts";
import { cosineTopK } from "../lib/vectors.ts";
import { godboltUrl } from "../lib/godbolt.ts";

test("front matter and fenced code become HTML", () => {
  const source = `---
title: "Pointer"
slug: "c/language/pointer"
---

<p>See <a href="/reference/c/language/array/">array</a>.</p>

\`\`\`c
int *p;
\`\`\`
`;
  const { meta, body } = splitFrontmatter(source);
  assert.equal(meta.title, "Pointer");
  assert.equal(meta.slug, "c/language/pointer");
  const html = renderBody(body);
  assert.match(html, /href="\/reference\/c\/language\/array\/"/);
  assert.match(html, /<code class="language-c">int \*p;<\/code>/);
  assert.equal(html.includes("```"), false);
});

test("cosine top-k ranks the matching vector first", () => {
  const matrix = new Float32Array([1, 0, 0, 0, 1, 0, 0, 0, 1]);
  const hits = cosineTopK(new Float32Array([0, 1, 0]), matrix, 3, 2);
  assert.equal(hits[0]?.index, 1);
  assert.ok((hits[0]?.score ?? 0) > 0.9);
  assert.equal(hits[1]?.index !== 1, true);
});

test("godbolt link is a clientstate URL", () => {
  const url = godboltUrl("int main(void){return 0;}\n", "cclang1810", "-std=c23");
  assert.ok(url.startsWith("https://godbolt.org/clientstate/"));
  assert.equal(url.includes(" "), false);
});
