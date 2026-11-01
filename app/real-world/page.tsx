import Link from "next/link";
import { godboltUrl } from "@/lib/godbolt";
import { getRealWorld } from "@/lib/content";

export const metadata = { title: "Real-world patterns" };

export default function RealWorldPage() {
  const items = getRealWorld();
  return (
    <main id="content" className="px-4 py-8 md:px-10">
      <h1 className="font-serif text-4xl">Patterns from real C</h1>
      <p className="mt-2 max-w-2xl text-muted">
        Small programs in the shape you meet in systems code. They are original, compile with clang -std=c23, and are MIT.
      </p>
      <div className="mt-6 max-w-3xl space-y-8">
        {items.map((item) => (
          <article key={item.slug} id={item.slug} className="rounded-2xl border border-line bg-elev p-5">
            <h2 className="font-serif text-3xl">{item.title}</h2>
            <p className="mt-2">{item.summary}</p>
            {item.body.map((paragraph) => <p key={paragraph} className="mt-2 text-sm">{paragraph}</p>)}
            <p className="mt-3">
              <Link className="text-sm font-semibold text-accent" href={godboltUrl(item.code, item.godboltCompiler, item.options)}>Open in Compiler Explorer</Link>
            </p>
            <pre className="codeblock mt-3 overflow-x-auto rounded-xl bg-[#1c1915] p-3 text-sm text-[#f6f1e8]"><code>{item.code}</code></pre>
          </article>
        ))}
      </div>
    </main>
  );
}
