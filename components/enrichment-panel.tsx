import { Diagram } from "@/components/diagrams";
import { Badge } from "@/components/ui/badge";
import { godboltUrl } from "@/lib/godbolt";
import type { Enrichment } from "@/lib/types";

export function EnrichmentPanel({ item }: { item: Enrichment }) {
  return (
    <section className="added-panel space-y-4" aria-label="Added commentary">
      <div className="flex flex-wrap items-center gap-2">
        <p className="added-kicker">Added on c.umutabali.com</p>
        <Badge tone={item.difficulty}>{item.difficulty}</Badge>
      </div>
      <p className="text-sm text-muted">
        Original commentary, kept separate from the upstream cppreference text. Published under CC BY-SA 3.0. The programs are MIT and were compiled on this project with the compiler named on each example.
      </p>
      <div className="grid gap-4 md:grid-cols-2">
        <div>
          <h2 className="font-serif text-2xl">Why it matters</h2>
          <p className="mt-1">{item.why}</p>
        </div>
        <div>
          <h2 className="font-serif text-2xl">When to use it</h2>
          <p className="mt-1">{item.when}</p>
        </div>
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        <div>
          <h2 className="font-serif text-xl">Common pitfalls</h2>
          <ul className="mt-1 list-disc space-y-1 pl-5 text-sm">
            {item.pitfalls.map((pitfall) => <li key={pitfall}>{pitfall}</li>)}
          </ul>
        </div>
        <div>
          <h2 className="font-serif text-xl">Modern practice</h2>
          <ul className="mt-1 list-disc space-y-1 pl-5 text-sm">
            {item.practice.map((note) => <li key={note}>{note}</li>)}
          </ul>
        </div>
      </div>
      {item.c23 ? (
        <div>
          <h2 className="font-serif text-xl">C23</h2>
          <p className="mt-1 text-sm">{item.c23}</p>
        </div>
      ) : null}
      {item.diagram ? <Diagram id={item.diagram} /> : null}
      <div className="space-y-3">
        {item.examples.map((example) => (
          <article key={example.title} className="rounded-xl bg-bg p-3">
            <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
              <h3 className="font-semibold">{example.title}</h3>
              <a className="text-sm font-semibold text-accent" href={godboltUrl(example.code, example.godboltCompiler, example.options)}>
                Open in Compiler Explorer
              </a>
            </div>
            <pre className="codeblock overflow-x-auto rounded-xl bg-[#1c1915] p-3 text-sm text-[#f6f1e8]" data-lang="c">
              <code className="language-c">{example.code}</code>
            </pre>
            <p className="mt-2 text-xs text-muted">
              Checked with {example.compiler} {example.options}. {example.note}
            </p>
          </article>
        ))}
      </div>
      {item.syntaxNote ? (
        <article className="rounded-xl border border-dashed border-line p-3">
          <h3 className="font-semibold">{item.syntaxNote.title}</h3>
          <p className="mt-1 text-sm text-muted">{item.syntaxNote.note}</p>
          <pre className="codeblock mt-2 overflow-x-auto rounded-xl bg-[#1c1915] p-3 text-sm text-[#f6f1e8]" data-lang="c">
            <code>{item.syntaxNote.code}</code>
          </pre>
        </article>
      ) : null}
    </section>
  );
}
