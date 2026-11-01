"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { categoryLabel } from "@/lib/categories";
import { Input } from "@/components/ui/input";

export function BrowseIndex({ pages }: { pages: { slug: string; title: string; category: string }[] }) {
  const [query, setQuery] = useState("");
  const [letter, setLetter] = useState("All");
  const letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ#".split("");
  const filtered = useMemo(() => {
    return pages.filter((page) => {
      const initial = /^[A-Za-z]/.test(page.title) ? page.title[0]!.toUpperCase() : "#";
      const matchesLetter = letter === "All" || initial === letter;
      const q = query.trim().toLowerCase();
      const matchesQuery = !q || page.title.toLowerCase().includes(q) || page.slug.toLowerCase().includes(q);
      return matchesLetter && matchesQuery;
    });
  }, [letter, pages, query]);
  return (
    <div className="mt-5">
      <Input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Filter by title or slug" aria-label="Filter index" />
      <div className="mt-3 flex flex-wrap gap-1">
        <button type="button" className={`rounded-full px-2 py-1 text-xs ${letter === "All" ? "bg-ink text-bg" : "bg-chip"}`} onClick={() => setLetter("All")}>All</button>
        {letters.map((item) => (
          <button key={item} type="button" className={`rounded-full px-2 py-1 text-xs ${letter === item ? "bg-ink text-bg" : "bg-chip"}`} onClick={() => setLetter(item)}>{item}</button>
        ))}
      </div>
      <p className="mt-3 text-sm text-muted">{filtered.length} pages</p>
      {filtered.length === 0 ? <p className="mt-4 text-muted">Nothing matches. Clear the filter or pick another letter.</p> : null}
      <ul className="mt-3 divide-y divide-line">
        {filtered.slice(0, 400).map((page) => (
          <li key={page.slug} className="flex flex-wrap items-baseline justify-between gap-2 py-2">
            <Link href={`/reference/${page.slug}/`} className="font-medium hover:text-accent">{page.title}</Link>
            <span className="text-xs text-muted">{categoryLabel(page.category)}</span>
          </li>
        ))}
      </ul>
      {filtered.length > 400 ? <p className="mt-3 text-sm text-muted">Showing the first 400 matches. Narrow the filter to see the rest.</p> : null}
    </div>
  );
}
