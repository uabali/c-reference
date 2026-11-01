import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import MiniSearch from "minisearch";

type Doc = { slug: string; title: string; category: string; headings: string; summary: string; text: string };

const docs = JSON.parse(readFileSync(new URL("../public/search/documents.json", import.meta.url), "utf8")) as Doc[];

function engine() {
  const mini = new MiniSearch<Doc & { id: number }>({
    fields: ["title", "headings", "text"],
    storeFields: ["title", "slug", "category", "summary"],
    searchOptions: { boost: { title: 4, headings: 2 }, prefix: true, fuzzy: 0.2 },
  });
  mini.addAll(docs.map((doc, id) => ({ ...doc, id })));
  return mini;
}

test("the index covers the converted book", () => {
  assert.ok(docs.length > 600);
  assert.ok(docs.some((doc) => doc.slug === "c/language/pointer"));
});

test("strlen ranks the strlen page first", () => {
  const hits = engine().search("strlen");
  assert.equal(hits[0]?.slug, "c/string/byte/strlen");
});

test("malloc finds the allocator page", () => {
  const hits = engine().search("malloc");
  assert.equal(hits[0]?.slug, "c/memory/malloc");
});

test("embedding file matches the document count", () => {
  const meta = JSON.parse(readFileSync(new URL("../public/search/embedding-meta.json", import.meta.url), "utf8")) as { count: number; dim: number };
  const bytes = readFileSync(new URL("../public/search/embeddings.bin", import.meta.url));
  assert.equal(meta.count, docs.length);
  assert.equal(bytes.length, meta.count * meta.dim * 4);
});
