import Link from "next/link";
import { getPaths } from "@/lib/content";

export const metadata = { title: "Learning paths" };

export default function PathsPage() {
  const paths = getPaths();
  return (
    <main id="content" className="px-4 py-8 md:px-10">
      <h1 className="font-serif text-4xl">Learning paths</h1>
      <p className="mt-2 max-w-2xl text-muted">
        Short routes through the reference. Each step links to the upstream page, which carries the added notes where we have them.
      </p>
      <div className="mt-6 grid gap-4 md:grid-cols-2">
        {paths.map((item) => (
          <Link key={item.slug} href={`/paths/${item.slug}/`} className="rounded-2xl border border-line bg-elev p-5">
            <p className="text-xs font-bold uppercase tracking-wide text-muted">{item.minutes} minutes · {item.steps.length} steps</p>
            <h2 className="mt-1 font-serif text-3xl">{item.title}</h2>
            <p className="mt-2 text-sm text-muted">{item.summary}</p>
          </Link>
        ))}
      </div>
      {paths.length === 0 ? <p className="mt-6 text-muted">No paths are published yet.</p> : null}
    </main>
  );
}
