export const CATEGORY_LABELS: Record<string, string> = {
  overview: "Overview",
  language: "Language",
  keyword: "Keywords",
  preprocessor: "Preprocessor",
  header: "Headers",
  types: "Type support",
  program: "Program utilities",
  variadic: "Variadic functions",
  error: "Error handling",
  memory: "Dynamic memory",
  string: "Strings",
  algorithm: "Algorithms",
  numeric: "Numerics",
  chrono: "Date and time",
  io: "Input/output",
  locale: "Localization",
  thread: "Concurrency",
  atomic: "Atomics",
  experimental: "Technical specifications",
  compiler_support: "Compiler support",
  symbol_index: "Symbol index",
  links: "External links",
  index: "Index",
};

export function categoryLabel(id: string) {
  return CATEGORY_LABELS[id] ?? id;
}
