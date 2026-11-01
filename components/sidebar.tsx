"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useMemo, useState } from "react";
import { categoryLabel } from "@/lib/categories";
import type { NavPage } from "@/lib/types";
import { cn } from "@/lib/utils";

export function Sidebar({
  pages,
  categories,
  onNavigate,
}: {
  pages: NavPage[];
  categories: { id: string; title: string }[];
  onNavigate?: () => void;
}) {
  const pathname = usePathname();
  const [query, setQuery] = useState("");
  const [open, setOpen] = useState<string | null>(null);
  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return pages;
    return pages.filter((page) => page.title.toLowerCase().includes(q) || page.slug.toLowerCase().includes(q));
  }, [pages, query]);
  const groups = useMemo(() => {
    const map = new Map<string, NavPage[]>();
    for (const page of filtered) {
      const list = map.get(page.category) ?? [];
      list.push(page);
      map.set(page.category, list);
    }
    return categories
      .map((category) => ({ ...category, pages: map.get(category.id) ?? [] }))
      .filter((category) => category.pages.length > 0);
  }, [categories, filtered]);

  return (
    <div className="flex h-full flex-col">
      <label className="px-3 pb-3">
        <span className="sr-only">Filter reference pages</span>
        <input
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Filter 600+ pages"
          className="h-9 w-full rounded-full border border-line bg-bg px-3 text-sm outline-none focus:ring-2 focus:ring-accent"
        />
      </label>
      <nav className="min-h-0 flex-1 space-y-1 overflow-y-auto px-2 pb-6" aria-label="Reference">
        {groups.map((group) => {
          const expanded = query.trim() !== "" || open === group.id;
          return (
            <div key={group.id}>
              <button
                type="button"
                className="flex w-full items-center justify-between gap-2 rounded-lg px-2 py-1.5 text-left text-xs font-bold uppercase tracking-normal text-muted hover:bg-chip"
                aria-expanded={expanded}
                onClick={() => setOpen(expanded && !query ? null : group.id)}
              >
                <span className="min-w-0 truncate">{categoryLabel(group.id) || group.title}</span>
                <span className="shrink-0 tabular-nums">{group.pages.length}</span>
              </button>
              {expanded ? (
                <ul className="mb-2 space-y-0.5">
                  {group.pages.map((page) => {
                    const href = `/reference/${page.slug}/`;
                    const active = pathname === href;
                    return (
                      <li key={page.slug}>
                        <Link
                          href={href}
                          onClick={onNavigate}
                          className={cn(
                            "block truncate rounded-lg px-2 py-1 text-sm hover:bg-chip",
                            active && "bg-accent/15 font-semibold text-accent",
                          )}
                        >
                          {page.title}
                        </Link>
                      </li>
                    );
                  })}
                </ul>
              ) : null}
            </div>
          );
        })}
        {groups.length === 0 ? <p className="px-2 text-sm text-muted">No pages match that filter.</p> : null}
      </nav>
    </div>
  );
}
