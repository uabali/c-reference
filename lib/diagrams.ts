export const DIAGRAMS = [
  { slug: "stack-heap", title: "Stack and heap", blurb: "What dies when a function returns, and what does not." },
  { slug: "pointers", title: "Pointers and arithmetic", blurb: "An address, a stride, and the cell it names." },
  { slug: "arrays", title: "Arrays and strings", blurb: "Why sizeof and strlen disagree, and why literals are not writable." },
  { slug: "padding", title: "Struct padding", blurb: "Reorder fields and watch sizeof change." },
  { slug: "function-pointers", title: "Function pointers", blurb: "A value that names code, used the way qsort uses a comparator." },
  { slug: "translation", title: "Translation phases", blurb: "From source file to running image." },
] as const;

export type DiagramSlug = (typeof DIAGRAMS)[number]["slug"];
