import { BrowseIndex } from "@/components/browse-index";
import { getCatalog } from "@/lib/content";

export const metadata = { title: "Alphabetical index" };

export default function BrowsePage() {
  const pages = getCatalog().pages.map((page) => ({
    slug: page.slug,
    title: page.title,
    category: page.category,
  }));
  return (
    <main id="content" className="px-4 py-8 md:px-10">
      <h1 className="font-serif text-4xl">Alphabetical index</h1>
      <p className="mt-2 max-w-2xl text-muted">Every C language and library page in this book. Filter by name or jump to a letter.</p>
      <BrowseIndex pages={pages} />
    </main>
  );
}
