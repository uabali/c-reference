"use client";

import Link from "next/link";
import MiniSearch from "minisearch";
import { useSearchParams } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { categoryLabel } from "@/lib/categories";
import { useSemanticIndex, type SearchDoc } from "@/components/use-semantic";

export function SearchPanel() {
  const params = useSearchParams();
  const initial = params.get("q") ?? "";
  const [query, setQuery] = useState(initial);
  const [semantic, setSemantic] = useState<{ title: string; slug: string; summary: string; score: number; category: string }[]>([]);
  const [semanticError, setSemanticError] = useState("");
  const [semanticState, setSemanticState] = useState<"idle" | "loading" | "done">("idle");
  const { docs, error, ready, search } = useSemanticIndex();

  useEffect(() => setQuery(initial), [initial]);

  const engine = useMemo(() => {
    if (!docs) return null;
    const mini = new MiniSearch<SearchDoc & { id: number }>({
      fields: ["title", "headings", "text"],
      storeFields: ["title", "slug", "category", "summary"],
      searchOptions: { boost: { title: 4, headings: 2 }, prefix: true, fuzzy: 0.2 },
    });
    mini.addAll(docs.map((doc, id) => ({ ...doc, id })));
    return mini;
  }, [docs]);

  const textHits = query.trim() && engine ? engine.search(query.trim()).slice(0, 12) : [];

  async function runSemantic() {
    if (!query.trim()) return;
    setSemanticState("loading");
    setSemanticError("");
    try {
      const hits = await search(query.trim(), 8);
      setSemantic(hits.filter((hit) => hit.doc).map((hit) => ({
        title: hit.doc!.title,
        slug: hit.doc!.slug,
        summary: hit.doc!.summary,
        category: hit.doc!.category,
        score: hit.score,
      })));
      setSemanticState("done");
    } catch (err) {
      setSemanticState("idle");
      setSemanticError(err instanceof Error ? err.message : "Semantic search failed.");
    }
  }

  return (
    <div>
      <form className="flex flex-col gap-2 sm:flex-row" onSubmit={(event) => { event.preventDefault(); void runSemantic(); }}>
        <Input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search titles and page text" aria-label="Search query" />
        <Button type="submit">Search by meaning</Button>
      </form>
      {!ready && !error ? <p className="mt-3 text-sm text-muted">Loading the local index…</p> : null}
      {error ? <p className="mt-3 text-sm text-warn" role="alert">{error}</p> : null}
      {query.trim() && ready && textHits.length === 0 ? <p className="mt-4 text-muted">No full-text matches. Try the meaning search, or a shorter word such as malloc.</p> : null}
      <section className="mt-6">
        <h2 className="font-serif text-2xl">Full text</h2>
        <ul className="mt-3 space-y-3">
          {textHits.map((hit) => (
            <li key={hit.id} className="rounded-2xl border border-line bg-elev p-4">
              <Link href={`/reference/${hit.slug}/`} className="font-serif text-2xl hover:text-accent">{hit.title}</Link>
              <p className="text-xs uppercase tracking-wide text-muted">{categoryLabel(String(hit.category))}</p>
              <p className="mt-1 text-sm text-muted">{hit.summary}</p>
            </li>
          ))}
        </ul>
      </section>
      <section className="mt-8">
        <h2 className="font-serif text-2xl">Meaning</h2>
        <p className="mt-1 text-sm text-muted">
          Runs entirely in your browser with the local all-MiniLM model. The first query downloads the model files from this site, not from a paid API.
        </p>
        {semanticState === "loading" ? <p className="mt-3 text-sm">Embedding the query… the first time also loads the model.</p> : null}
        {semanticError ? <p className="mt-3 text-sm text-warn" role="alert">{semanticError}</p> : null}
        {semanticState === "done" && semantic.length === 0 ? <p className="mt-3 text-muted">No semantic neighbors.</p> : null}
        <ul className="mt-3 space-y-3">
          {semantic.map((hit) => (
            <li key={hit.slug} className="rounded-2xl border border-line bg-elev p-4">
              <div className="flex items-center gap-2">
                <Link href={`/reference/${hit.slug}/`} className="font-serif text-2xl hover:text-accent">{hit.title}</Link>
                <Badge>{hit.score.toFixed(2)}</Badge>
              </div>
              <p className="mt-1 text-sm text-muted">{hit.summary}</p>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
