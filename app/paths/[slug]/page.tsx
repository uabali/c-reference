import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { getPath, getPaths, referenceHref } from "@/lib/content";

export function generateStaticParams() {
  return getPaths().map((item) => ({ slug: item.slug }));
}

export const dynamicParams = false;

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  return { title: getPath(slug)?.title ?? "Learning path" };
}

export default async function PathPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const item = getPath(slug);
  if (!item) notFound();
  return (
    <main id="content" className="px-4 py-8 md:px-10">
      <p className="text-sm text-muted"><Link href="/paths/">Learning paths</Link></p>
      <h1 className="mt-2 font-serif text-4xl">{item.title}</h1>
      <p className="mt-2 max-w-2xl text-muted">{item.summary}</p>
      <ol className="mt-6 max-w-3xl space-y-4">
        {item.steps.map((step, index) => (
          <li key={step.slug} className="rounded-2xl border border-line bg-elev p-4">
            <p className="text-xs font-bold uppercase tracking-wide text-accent">Step {index + 1}</p>
            <h2 className="font-serif text-2xl"><Link href={referenceHref(step.slug)}>{step.title}</Link></h2>
            <p className="mt-1 text-sm">{step.blurb}</p>
          </li>
        ))}
      </ol>
    </main>
  );
}
