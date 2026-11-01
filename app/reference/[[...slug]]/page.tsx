import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { Attribution } from "@/components/attribution";
import { EnrichmentPanel } from "@/components/enrichment-panel";
import { MiniGraph } from "@/components/mini-graph";
import { categoryLabel, getCatalog, getEnrichment, getNeighbors, getPage, readRenderedPage, referenceHref } from "@/lib/content";

type Params = { slug?: string[] };

export function generateStaticParams() {
  const pages = getCatalog().pages.map((page) => ({ slug: page.slug.split("/") }));
  return [{ slug: [] as string[] }, ...pages];
}

export const dynamicParams = false;

export async function generateMetadata({ params }: { params: Promise<Params> }): Promise<Metadata> {
  const { slug } = await params;
  if (!slug || slug.length === 0) return { title: "Reference index" };
  const page = getPage(slug.join("/"));
  if (!page) return { title: "Reference" };
  return { title: page.title, description: page.summary };
}

export default async function ReferencePage({ params }: { params: Promise<Params> }) {
  const { slug } = await params;
  if (!slug || slug.length === 0) return <Index />;
  const key = slug.join("/");
  const page = getPage(key);
  const rendered = readRenderedPage(key);
  if (!page || !rendered) notFound();
  const enrichment = getEnrichment(key);
  const neighbors = getNeighbors(key);
  return (
    <main id="content" className="px-4 py-6 md:px-10 md:py-8">
      <p className="text-sm text-muted">
        <Link href="/reference/" className="hover:text-ink">Reference</Link>
        {" / "}
        <Link href={`/browse/?category=${page.category}`} className="hover:text-ink">{categoryLabel(page.category)}</Link>
      </p>
      <div className="mt-2 flex flex-wrap items-end justify-between gap-3">
        <h1 className="font-serif text-4xl tracking-tight md:text-5xl">{page.title}</h1>
        {enrichment ? <span className="rounded-full bg-accent/15 px-3 py-1 text-sm font-semibold text-accent">{enrichment.difficulty}</span> : null}
      </div>
      <nav className="mt-3 text-sm text-muted" aria-label="Breadcrumb">
        {page.breadcrumbs.map((crumb, index) => (
          <span key={crumb.href}>
            {index > 0 ? " / " : null}
            <Link href={crumb.href.startsWith("/reference/") ? crumb.href : referenceHref(crumb.href.replace(/^\/reference\//, "").replace(/\/$/, ""))}>{crumb.title}</Link>
          </span>
        ))}
      </nav>
      <div className="mt-4"><Attribution source={page.source} title={page.title} /></div>
      {enrichment ? <div className="mt-6"><EnrichmentPanel item={enrichment} /></div> : null}
      <h2 className="mt-8 font-serif text-2xl">Upstream reference</h2>
      <article className="prose mt-3 max-w-3xl" dangerouslySetInnerHTML={{ __html: rendered.html }} />
      <div className="mt-8 max-w-3xl"><MiniGraph title={page.title} neighbors={neighbors} /></div>
      <div className="mt-6 max-w-3xl"><Attribution source={page.source} title={page.title} /></div>
    </main>
  );
}

function Index() {
  const catalog = getCatalog();
  const groups = catalog.categories.map((category) => ({
    ...category,
    pages: catalog.pages.filter((page) => page.category === category.id).slice(0, 8),
    count: catalog.pages.filter((page) => page.category === category.id).length,
  }));
  return (
    <main id="content" className="px-4 py-8 md:px-10">
      <h1 className="font-serif text-4xl">Reference index</h1>
      <p className="mt-2 max-w-2xl text-muted">
        {catalog.pageCount} pages. The alphabetical list lives on the browse page. Every page below carries the cppreference attribution.
      </p>
      <p className="mt-3"><Link className="font-semibold text-accent" href="/browse/">Open the A–Z index</Link></p>
      <div className="mt-6 grid gap-4 md:grid-cols-2">
        {groups.map((group) => (
          <section key={group.id} className="rounded-2xl border border-line bg-elev p-4">
            <h2 className="font-serif text-2xl">{group.title}</h2>
            <p className="text-xs text-muted">{group.count} pages</p>
            <ul className="mt-2 space-y-1 text-sm">
              {group.pages.map((page) => (
                <li key={page.slug}><Link className="hover:text-accent" href={referenceHref(page.slug)}>{page.title}</Link></li>
              ))}
            </ul>
          </section>
        ))}
      </div>
    </main>
  );
}
