import { TopicGraph } from "@/components/topic-graph";

export const metadata = { title: "Topic graph" };

export default function GraphPage() {
  return (
    <main id="content" className="px-4 py-8 md:px-8">
      <h1 className="font-serif text-4xl">Topic graph</h1>
      <p className="mt-2 max-w-3xl text-muted">
        Edges come from two places: cross-links inside the converted reference, marked related, and a curated set of prerequisite and uses links for the learning paths. Click a node to open its page. Each reference page also shows a small slice of this graph.
      </p>
      <div className="mt-4">
        <TopicGraph />
      </div>
    </main>
  );
}
