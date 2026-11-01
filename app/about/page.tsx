import { getCatalog } from "@/lib/content";

export const metadata = { title: "About and license" };

export default function AboutPage() {
  const catalog = getCatalog();
  return (
    <main id="content" className="prose px-4 py-8 md:px-10">
      <h1 className="font-serif text-4xl">About this reference</h1>
      <p>
        c.umutabali.com is a C language reference maintained for Umut Abali. It covers the language and the standard library, not C++.
      </p>
      <h2>Source and license</h2>
      <p>
        The reference text is adapted from the C portion of the {catalog.dump} offline HTML book published by Peter Feicht at{" "}
        <a href="https://github.com/PeterFeicht/cppreference-doc/releases/tag/v20250209">PeterFeicht/cppreference-doc</a>,
        which archives <a href="https://en.cppreference.com/w/c">cppreference.com</a>. That text is © the cppreference contributors and licensed under{" "}
        <a href="https://creativecommons.org/licenses/by-sa/3.0/">Creative Commons Attribution-ShareAlike 3.0</a>.
        This site is a derivative work and is published under the same license. Every reference page links to the original article.
      </p>
      <p>
        As of 1 November 2026, v20250209 (9 February 2025) is still the latest html-book release. The April 2026 cppreference redesign broke the upstream update scripts, tracked as issue 51 on that repository, and no newer dump has been published. <code>tools/sync_upstream.py</code> checks for a newer release.
      </p>
      <p>
        Notes labeled “Added on c.umutabali.com” are original and also CC BY-SA 3.0. Example programs in those notes, and the software that builds this site, are MIT. See LICENSE and LICENSE-CONTENT.
      </p>
      <h2>What was added</h2>
      <p>
        Learning paths, five-minute cards, a mistakes chapter, C23 comparison tables, real-world sketches, interactive diagrams, a topic graph, full-text search, and semantic search with a local MiniLM model. The optional assistant sends a question to OpenRouter only if you paste your own key into this browser.
      </p>
    </main>
  );
}
