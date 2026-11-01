import Link from "next/link";
import type { Neighbor } from "@/lib/types";

const kindLabel = {
  prerequisite: "prerequisite",
  related: "related",
  uses: "uses",
};

export function MiniGraph({ title, neighbors }: { title: string; neighbors: Neighbor[] }) {
  if (neighbors.length === 0) return null;
  const left = neighbors.filter((item) => item.direction === "in").slice(0, 4);
  const right = neighbors.filter((item) => item.direction === "out").slice(0, 4);
  return (
    <section className="rounded-2xl border border-line bg-elev p-4" aria-label="Related topics">
      <div className="mb-3 flex items-baseline justify-between gap-3">
        <h2 className="font-serif text-2xl">Related topics</h2>
        <Link href="/graph/" className="text-sm text-accent">Open the graph</Link>
      </div>
      <div className="grid gap-3 md:grid-cols-[1fr_auto_1fr] md:items-center">
        <ul className="space-y-2">
          {left.map((item) => (
            <NodeLink key={`${item.kind}-${item.slug}`} item={item} />
          ))}
        </ul>
        <div className="rounded-2xl bg-ink px-4 py-3 text-center text-sm font-semibold text-bg md:min-w-40">
          {title}
        </div>
        <ul className="space-y-2">
          {right.map((item) => (
            <NodeLink key={`${item.kind}-${item.slug}`} item={item} />
          ))}
        </ul>
      </div>
    </section>
  );
}

function NodeLink({ item }: { item: Neighbor }) {
  return (
    <li>
      <Link href={`/reference/${item.slug}/`} className="block rounded-xl border border-line px-3 py-2 hover:bg-chip">
        <span className="block text-sm font-semibold">{item.title}</span>
        <span className="text-xs uppercase tracking-wide text-muted">
          {item.direction === "in" ? "incoming" : "outgoing"} · {kindLabel[item.kind]}
        </span>
      </Link>
    </li>
  );
}
