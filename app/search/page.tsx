import { Suspense } from "react";
import { SearchPanel } from "@/components/search-panel";

export const metadata = { title: "Search" };

export default function SearchPage() {
  return (
    <main id="content" className="px-4 py-8 md:px-10">
      <h1 className="font-serif text-4xl">Search</h1>
      <p className="mt-2 max-w-2xl text-muted">
        Full-text search is instant. Meaning search embeds your query in the browser with all-MiniLM and compares it to vectors built at site build time. No API key is required.
      </p>
      <div className="mt-5 max-w-3xl">
        <Suspense fallback={<p className="text-muted">Opening search…</p>}>
          <SearchPanel />
        </Suspense>
      </div>
    </main>
  );
}
