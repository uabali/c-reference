# C Reference

A static C language and standard-library reference for [c.umutabali.com](https://c.umutabali.com), maintained for Umut Abali.

The reference text is the C portion of the cppreference offline book **html-book v20250209** (9 February 2025), the latest release of [PeterFeicht/cppreference-doc](https://github.com/PeterFeicht/cppreference-doc/releases/tag/v20250209) as of 1 November 2026. A newer dump has not been published: the April 2026 cppreference redesign broke the upstream scripts ([issue 51](https://github.com/PeterFeicht/cppreference-doc/issues/51)).

## What is in the site

- 627 reference pages converted from HTML to MDX, with code blocks, tables, version marks, and internal links rewritten to this site.
- Attribution and a link to the original cppreference page on every reference page. The content license is [CC BY-SA 3.0](LICENSE-CONTENT).
- Original notes on 51 important topics: why it matters, when to use it, pitfalls, modern practice, C23, and runnable examples with Compiler Explorer links. Those sections are labeled **Added on c.umutabali.com**.
- Learning paths, five-minute cards, a common-mistakes chapter, a C23 comparison, and four small real-world programs.
- Interactive diagrams for the stack and heap, pointer arithmetic, arrays and strings, struct padding, and function pointers.
- A topic graph (prerequisite, related, uses) plus a related-topics block on each page.
- Full-text search (MiniSearch) and semantic search. Embeddings are computed at build time with `Xenova/all-MiniLM-L6-v2`. The query is embedded in the browser. No API key.
- A beta assistant at `/assistant/` that uses the local index and, only if you paste one, your own OpenRouter key (stored in `localStorage`). The default model is `nvidia/nemotron-3-ultra-550b-a55b:free`.

Example programs are MIT and were compiled and run with Clang 18 (`-std=c23`) or GCC 13 (`-std=c2x`). Software in this repository is MIT (`LICENSE`).

## Run it locally

```bash
npm install
npm run dev
```

The dev server listens on port **43123**. A production static export is:

```bash
npm run build
npx serve out -l 43123
```

`npm test` runs the conversion, graph, curated-content, render, and search tests. `npm run examples` compiles and runs every curated program. `npm run test:e2e` is a Playwright smoke test against the static `out/` directory.

## Refresh the cppreference text

The converted pages are already in `content/mdx`. To rebuild them from a local extract of `reference/en`:

```bash
python3 -m pip install -r tools/requirements.txt
python3 tools/convert.py --html-root /path/to/reference/en
python3 tools/build_graph.py
node tools/build-embeddings.mjs
```

To see whether GitHub has a newer html-book, and optionally replace the generated pages (curated notes are never overwritten):

```bash
python3 tools/sync_upstream.py
python3 tools/sync_upstream.py --apply   # only when a newer dump should replace content/mdx
```

The report is written to `reports/upstream-diff.md`.

## Deploy on Vercel and attach c.umutabali.com

1. Push this repository and import it as a Vercel project. Framework preset: **Next.js**. The build command is `npm run build`. `next.config.ts` sets `output: "export"`, so Vercel publishes the static `out/` directory. No environment variables are required.
2. In the project, open **Settings → Domains** and add `c.umutabali.com`.
3. At the DNS host for `umutabali.com`, add the record Vercel shows. For this subdomain that is a **CNAME** named `c` pointing at `cname.vercel-dns.com`. (If Vercel asks for an `A` record instead, use the address it displays.)
4. Wait until Vercel reports the domain as valid and the certificate is issued. The site is then served at `https://c.umutabali.com`.

The first semantic search in a browser loads `/models/Xenova/all-MiniLM-L6-v2/` and `/ort/*.wasm` from the same deployment. Those files are produced by `npm run build` (`tools/copy-ort.mjs` copies the WebAssembly runtime out of `onnxruntime-web`).

## Limitations

- The book stops at the February 2025 cppreference snapshot. C23 pages that cppreference had not finished (some clause numbers are still "TBD") are reproduced as archived.
- `#embed` and `constexpr` functions are documented, but the compilers used to check examples (Clang 18 and GCC 13) cannot compile them. `constexpr` objects are checked with GCC. The `#embed` page shows the directive as syntax and compiles the equivalent array.
- Semantic search embeds a page excerpt, not every paragraph. The assistant is beta and only runs with a key you provide.
- The topic-graph map draws the curated prerequisite and uses edges. The full cross-link set is used for neighborhoods and for the related-topics block, not drawn as one hairball.
