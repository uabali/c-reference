import Link from "next/link";
import { getMistakes, referenceHref } from "@/lib/content";

export const metadata = { title: "Common mistakes" };

export default function MistakesPage() {
  const mistakes = getMistakes();
  return (
    <main id="content" className="px-4 py-8 md:px-10">
      <h1 className="font-serif text-4xl">Common mistakes</h1>
      <p className="mt-2 max-w-2xl text-muted">
        Original notes. The corrected programs compile with clang -std=c23. The broken snippets are shown so you can recognize them; do not compile those.
      </p>
      <div className="mt-6 max-w-3xl space-y-6">
        {mistakes.map((item) => (
          <article key={item.title} className="rounded-2xl border border-line bg-elev p-5">
            <h2 className="font-serif text-3xl">{item.title}</h2>
            <p className="mt-2">{item.why}</p>
            <h3 className="mt-3 text-sm font-bold uppercase tracking-wide text-warn">Recognize this</h3>
            <pre className="codeblock overflow-x-auto rounded-xl bg-[#1c1915] p-3 text-sm text-[#f6f1e8]"><code>{item.wrong}</code></pre>
            <h3 className="mt-3 text-sm font-bold uppercase tracking-wide text-good">Prefer this</h3>
            <pre className="codeblock overflow-x-auto rounded-xl bg-[#1c1915] p-3 text-sm text-[#f6f1e8]"><code>{item.right}</code></pre>
            {item.page ? <p className="mt-2"><Link className="text-sm font-semibold text-accent" href={referenceHref(item.page)}>Reference page</Link></p> : null}
          </article>
        ))}
      </div>
    </main>
  );
}
