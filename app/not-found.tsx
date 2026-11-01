import Link from "next/link";

export default function NotFound() {
  return (
    <main id="content" className="px-4 py-16 md:px-10">
      <h1 className="font-serif text-4xl">That page is not in this book.</h1>
      <p className="mt-3 max-w-xl text-muted">The reference only includes the C language and standard library from the v20250209 cppreference dump.</p>
      <p className="mt-4"><Link className="font-semibold text-accent" href="/search/">Search instead</Link></p>
    </main>
  );
}
