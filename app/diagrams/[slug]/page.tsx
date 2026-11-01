import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { Diagram } from "@/components/diagrams";
import { DIAGRAMS } from "@/lib/diagrams";

export function generateStaticParams() {
  return DIAGRAMS.map((item) => ({ slug: item.slug }));
}

export const dynamicParams = false;

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const item = DIAGRAMS.find((entry) => entry.slug === slug);
  return { title: item?.title ?? "Diagram" };
}

export default async function DiagramPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const item = DIAGRAMS.find((entry) => entry.slug === slug);
  if (!item) notFound();
  return (
    <main id="content" className="px-4 py-8 md:px-10">
      <p className="text-sm text-muted"><Link href="/diagrams/">Diagrams</Link></p>
      <h1 className="mt-2 font-serif text-4xl">{item.title}</h1>
      <p className="mt-2 max-w-2xl text-muted">{item.blurb}</p>
      <div className="mt-6 max-w-3xl"><Diagram id={item.slug} /></div>
    </main>
  );
}
