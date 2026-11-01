import fs from "node:fs";
import path from "node:path";
import { categoryLabel } from "@/lib/categories";
import { renderBody, splitFrontmatter } from "@/lib/render";
import type {
  ConceptCard,
  Enrichment,
  LearningPath,
  Mistake,
  NavPage,
  Neighbor,
  RealWorld,
} from "@/lib/types";

export type CatalogPage = NavPage & {
  source: string;
  retrieved: string;
  license: string;
  dump: string;
  headings: string[];
  links: string[];
  breadcrumbs: { title: string; href: string }[];
};

type Catalog = {
  dump: string;
  retrieved: string;
  license: string;
  original: string;
  pageCount: number;
  categories: { id: string; title: string }[];
  pages: CatalogPage[];
};

const root = process.cwd();

function readJson<T>(relative: string, fallback: T): T {
  const full = path.join(root, relative);
  if (!fs.existsSync(full)) return fallback;
  return JSON.parse(fs.readFileSync(full, "utf8")) as T;
}

let catalogCache: Catalog | null = null;

export function getCatalog() {
  if (!catalogCache) {
    catalogCache = readJson<Catalog>("content/catalog.json", {
      dump: "v20250209",
      retrieved: "2025-02-09",
      license: "CC BY-SA 3.0",
      original: "https://en.cppreference.com/w/c",
      pageCount: 0,
      categories: [],
      pages: [],
    });
  }
  return catalogCache;
}

export function getPage(slug: string) {
  return getCatalog().pages.find((page) => page.slug === slug) ?? null;
}

export function readRenderedPage(slug: string) {
  const full = path.join(root, "content/mdx", `${slug}.mdx`);
  if (!fs.existsSync(full)) return null;
  const source = fs.readFileSync(full, "utf8");
  const { meta, body } = splitFrontmatter(source);
  return { meta, html: renderBody(body) };
}

let enrichmentCache: Map<string, Enrichment> | null = null;

export function getEnrichment(slug: string) {
  if (!enrichmentCache) {
    const rows = readJson<Enrichment[]>("content/curated/enrichment.json", []);
    enrichmentCache = new Map(rows.map((row) => [row.slug, row]));
  }
  return enrichmentCache.get(slug) ?? null;
}

export function listEnrichment() {
  if (!enrichmentCache) getEnrichment("__warm__");
  return [...(enrichmentCache?.values() ?? [])];
}

let neighborCache: Record<string, Neighbor[]> | null = null;

export function getNeighbors(slug: string) {
  if (!neighborCache) {
    neighborCache = readJson<Record<string, Neighbor[]>>("content/neighbors.json", {});
  }
  return neighborCache[slug] ?? [];
}

export function getPaths() {
  return readJson<LearningPath[]>("content/curated/paths.json", []);
}

export function getPath(slug: string) {
  return getPaths().find((item) => item.slug === slug) ?? null;
}

export function getCards() {
  return readJson<ConceptCard[]>("content/curated/cards.json", []);
}

export function getMistakes() {
  return readJson<Mistake[]>("content/curated/mistakes.json", []);
}

export function getRealWorld() {
  return readJson<RealWorld[]>("content/curated/real-world.json", []);
}

export function getC23Tables() {
  return readJson<{
    intro: string;
    rows: { feature: string; older: string; c23: string; page?: string }[];
    notes: string[];
  }>("content/curated/c23.json", { intro: "", rows: [], notes: [] });
}

export function referenceHref(slug: string) {
  return `/reference/${slug}/`;
}

export { categoryLabel };
