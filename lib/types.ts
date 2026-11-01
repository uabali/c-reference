export type Difficulty = "Beginner" | "Intermediate" | "Advanced";

export type Example = {
  title: string;
  code: string;
  compiler: "clang" | "gcc";
  options: string;
  godboltCompiler: string;
  note?: string;
};

export type Enrichment = {
  slug: string;
  difficulty: Difficulty;
  why: string;
  when: string;
  pitfalls: string[];
  practice: string[];
  c23?: string;
  diagram?: string;
  examples: Example[];
  syntaxNote?: { title: string; code: string; note: string };
};

export type NavPage = {
  slug: string;
  title: string;
  category: string;
  summary: string;
};

export type Neighbor = {
  slug: string;
  title: string;
  category: string;
  kind: "prerequisite" | "related" | "uses";
  direction: "in" | "out";
};

export type PathStep = { slug: string; title: string; blurb: string };

export type LearningPath = {
  slug: string;
  title: string;
  minutes: number;
  summary: string;
  steps: PathStep[];
};

export type ConceptCard = {
  slug: string;
  title: string;
  minutes: number;
  difficulty: Difficulty;
  lead: string;
  points: string[];
  page?: string;
};

export type Mistake = {
  title: string;
  why: string;
  wrong: string;
  right: string;
  page?: string;
};

export type RealWorld = {
  slug: string;
  title: string;
  summary: string;
  body: string[];
  code: string;
  compiler: "clang" | "gcc";
  options: string;
  godboltCompiler: string;
};
