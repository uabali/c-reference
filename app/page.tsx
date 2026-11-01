import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { getCatalog, getPaths } from "@/lib/content";

const entries = [
  ["Learning paths", "/paths/", "A route through pointers, memory, and the features C23 actually changed."],
  ["Five-minute cards", "/cards/", "One idea, a few sentences, a link into the reference."],
  ["Common mistakes", "/mistakes/", "The bugs that show up in review, with a version that compiles."],
  ["C23 beside older C", "/c23/", "nullptr, attributes, constexpr, typeof, _BitInt, #embed, checked arithmetic."],
  ["Diagrams", "/diagrams/", "Stack and heap, pointer stride, string memory, padding, function pointers."],
  ["Topic graph", "/graph/", "Prerequisite, related, and uses edges you can walk."],
  ["Real programs", "/real-world/", "An arena, a string builder, callbacks, and a tiny config parser."],
  ["Assistant (beta)", "/assistant/", "Bring your own OpenRouter key. Retrieval stays on this site."],
];

export default function HomePage() {
  const catalog = getCatalog();
  const paths = getPaths();
  return (
    <main id="content" className="px-4 py-8 md:px-10 md:py-12">
      <p className="text-sm font-semibold uppercase tracking-[0.16em] text-accent">c.umutabali.com · Umut Abali</p>
      <h1 className="mt-3 max-w-3xl font-serif text-5xl leading-[1.05] tracking-tight md:text-6xl">
        The C language, set so you can learn it.
      </h1>
      <p className="mt-4 max-w-2xl text-lg text-muted">
        Language and library pages from cppreference, under CC BY-SA 3.0, with original notes on why a feature exists, the mistakes around it, and what C23 changed. {catalog.pageCount} reference pages from the {catalog.dump} offline book.
      </p>
      <form action="/search/" className="mt-6 flex max-w-xl gap-2">
        <label className="sr-only" htmlFor="q">Search the reference</label>
        <input id="q" name="q" placeholder="Try strlen, nullptr, restrict…" className="h-12 flex-1 rounded-full border border-line bg-elev px-4 outline-none focus:ring-2 focus:ring-accent" />
        <button className="h-12 rounded-full bg-accent px-5 font-semibold text-white" type="submit">Search</button>
      </form>
      <div className="mt-8 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        {entries.map(([title, href, text]) => (
          <Link key={href} href={href} className="rounded-2xl border border-line bg-elev p-4 shadow-[var(--shadow)] transition hover:-translate-y-0.5">
            <span className="font-serif text-2xl">{title}</span>
            <p className="mt-2 text-sm text-muted">{text}</p>
            <span className="mt-3 inline-flex items-center gap-1 text-sm font-semibold text-accent">Open <ArrowRight size={14} /></span>
          </Link>
        ))}
      </div>
      <section className="mt-10">
        <h2 className="font-serif text-3xl">Start with a path</h2>
        <div className="mt-4 grid gap-3 md:grid-cols-2">
          {paths.slice(0, 4).map((item) => (
            <Link key={item.slug} href={`/paths/${item.slug}/`} className="rounded-2xl border border-line bg-elev p-4">
              <p className="text-xs font-bold uppercase tracking-wide text-muted">{item.minutes} min</p>
              <h3 className="font-serif text-2xl">{item.title}</h3>
              <p className="mt-1 text-sm text-muted">{item.summary}</p>
            </Link>
          ))}
          {paths.length === 0 ? <p className="text-muted">Learning paths are being prepared.</p> : null}
        </div>
      </section>
      <p className="mt-10 max-w-3xl text-sm text-muted">
        Reference text is a derivative of cppreference.com, © the cppreference contributors, CC BY-SA 3.0. Original notes and this site’s arrangement are also CC BY-SA 3.0. Software in this repository is MIT. See the about page for attribution and deployment.
      </p>
    </main>
  );
}
