import Link from "next/link";
import { DIAGRAMS } from "@/lib/diagrams";

export const metadata = { title: "Diagrams" };

export default function DiagramsPage() {
  return (
    <main id="content" className="px-4 py-8 md:px-10">
      <h1 className="font-serif text-4xl">Visual explanations</h1>
      <p className="mt-2 max-w-2xl text-muted">
        Interactive pictures for the ideas that are hard to see in a paragraph. The same diagrams appear on the matching reference pages.
      </p>
      <div className="mt-6 grid gap-3 md:grid-cols-2">
        {DIAGRAMS.map((item) => (
          <Link key={item.slug} href={`/diagrams/${item.slug}/`} className="rounded-2xl border border-line bg-elev p-5">
            <h2 className="font-serif text-3xl">{item.title}</h2>
            <p className="mt-2 text-sm text-muted">{item.blurb}</p>
          </Link>
        ))}
      </div>
    </main>
  );
}
