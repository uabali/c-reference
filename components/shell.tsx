"use client";

import Link from "next/link";
import { Menu, X } from "lucide-react";
import { useState } from "react";
import { Sidebar } from "@/components/sidebar";
import { ThemeToggle } from "@/components/theme-toggle";
import { Button } from "@/components/ui/button";
import type { NavPage } from "@/lib/types";

const links = [
  ["Paths", "/paths/"],
  ["Search", "/search/"],
  ["Graph", "/graph/"],
  ["Diagrams", "/diagrams/"],
  ["C23", "/c23/"],
  ["Mistakes", "/mistakes/"],
];

export function Shell({
  pages,
  categories,
  children,
}: {
  pages: NavPage[];
  categories: { id: string; title: string }[];
  children: React.ReactNode;
}) {
  const [open, setOpen] = useState(false);
  return (
    <>
      <a href="#content" className="skip-link">Skip to content</a>
      <header className="sticky top-0 z-40 border-b border-line/80 bg-bg/85 backdrop-blur">
        <div className="flex h-16 items-center gap-3 px-3 md:px-5">
          <Button variant="ghost" size="icon" className="md:hidden" aria-label="Open navigation" onClick={() => setOpen(true)}>
            <Menu size={18} />
          </Button>
          <Link href="/" className="flex items-center gap-2 font-serif text-xl tracking-tight">
            <span className="grid h-8 w-8 place-items-center rounded-lg bg-ink text-sm text-bg">C</span>
            C Reference
          </Link>
          <nav className="ml-4 hidden items-center gap-4 text-sm text-muted lg:flex" aria-label="Site">
            {links.map(([label, href]) => (
              <Link key={href} href={href} className="hover:text-ink">{label}</Link>
            ))}
          </nav>
          <div className="ml-auto flex items-center gap-1">
            <Link href="/search/" className="hidden text-sm text-muted hover:text-ink sm:inline">Search</Link>
            <ThemeToggle />
          </div>
        </div>
      </header>
      <div className="mx-auto grid w-full max-w-[1400px] md:grid-cols-[280px_minmax(0,1fr)]">
        <aside className="sticky top-16 hidden h-[calc(100vh-4rem)] border-r border-line md:block">
          <div className="h-full pt-4">
            <Sidebar pages={pages} categories={categories} />
          </div>
        </aside>
        <div className="min-w-0">{children}</div>
      </div>
      {open ? (
        <div className="fixed inset-0 z-50 md:hidden">
          <button className="absolute inset-0 bg-black/40" aria-label="Close navigation" onClick={() => setOpen(false)} />
          <div className="absolute inset-y-0 left-0 flex w-[min(100%,320px)] flex-col bg-elev shadow-2xl">
            <div className="flex items-center justify-between px-3 py-3">
              <span className="font-serif text-lg">Browse</span>
              <Button variant="ghost" size="icon" aria-label="Close" onClick={() => setOpen(false)}><X size={18} /></Button>
            </div>
            <Sidebar pages={pages} categories={categories} onNavigate={() => setOpen(false)} />
          </div>
        </div>
      ) : null}
    </>
  );
}
