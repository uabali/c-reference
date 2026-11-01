import Link from "next/link";
import { getCards, referenceHref } from "@/lib/content";

export const metadata = { title: "Five-minute cards" };

export default function CardsPage() {
  const cards = getCards();
  return (
    <main id="content" className="px-4 py-8 md:px-10">
      <h1 className="font-serif text-4xl">Five-minute cards</h1>
      <p className="mt-2 max-w-2xl text-muted">
        Original sketches. Read one, then open the reference page if you want the standard’s wording. These notes are CC BY-SA 3.0.
      </p>
      <div className="mt-6 grid gap-4 md:grid-cols-2">
        {cards.map((card) => (
          <article key={card.slug} className="rounded-2xl border border-line bg-elev p-5">
            <p className="text-xs font-bold uppercase tracking-wide text-muted">{card.minutes} min · {card.difficulty}</p>
            <h2 className="font-serif text-3xl">{card.title}</h2>
            <p className="mt-2">{card.lead}</p>
            <ul className="mt-3 list-disc space-y-1 pl-5 text-sm">
              {card.points.map((point) => <li key={point}>{point}</li>)}
            </ul>
            {card.page ? <p className="mt-3"><Link className="text-sm font-semibold text-accent" href={referenceHref(card.page)}>Open the reference page</Link></p> : null}
          </article>
        ))}
      </div>
      {cards.length === 0 ? <p className="mt-6 text-muted">Cards are not generated yet.</p> : null}
    </main>
  );
}
