"use client";

import {
  Background,
  Controls,
  ReactFlow,
  type Edge,
  type Node,
  type NodeProps,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { useEffect, useMemo, useState } from "react";
import { Input } from "@/components/ui/input";

type GraphNode = { id: string; title: string; category: string };
type GraphEdge = { source: string; target: string; kind: "prerequisite" | "related" | "uses" };
type GraphFile = { nodes: GraphNode[]; edges: GraphEdge[] };

const kindColor = {
  prerequisite: "#9a3412",
  uses: "#1f4b3a",
  related: "#8a8175",
};

function TopicNode({ data }: NodeProps) {
  const label = String(data.label ?? "");
  const href = String(data.href ?? "#");
  return (
    <a href={href} className="block h-full w-full rounded-lg border border-line bg-elev px-2 py-1 text-xs leading-snug text-ink">
      {label}
    </a>
  );
}

const nodeTypes = { topic: TopicNode };

export function TopicGraph() {
  const [graph, setGraph] = useState<GraphFile | null>(null);
  const [error, setError] = useState("");
  const [mode, setMode] = useState<"map" | "near">("map");
  const [query, setQuery] = useState("pointer");

  useEffect(() => {
    fetch("/graph.json")
      .then((response) => response.json())
      .then((payload: GraphFile) => setGraph(payload))
      .catch(() => setError("Could not load the topic graph."));
  }, []);

  const view = useMemo(() => buildView(graph, mode, query), [graph, mode, query]);

  return (
    <div>
      <div className="mb-3 flex flex-col gap-2 md:flex-row md:items-center">
        <div className="flex gap-2">
          <button type="button" className={`rounded-full px-3 py-1 text-sm ${mode === "map" ? "bg-ink text-bg" : "bg-chip"}`} onClick={() => setMode("map")}>Curated map</button>
          <button type="button" className={`rounded-full px-3 py-1 text-sm ${mode === "near" ? "bg-ink text-bg" : "bg-chip"}`} onClick={() => setMode("near")}>Neighborhood</button>
        </div>
        <Input value={query} onChange={(event) => setQuery(event.target.value)} aria-label="Focus a topic" placeholder="Focus a topic, for example malloc" />
      </div>
      <p className="mb-2 text-xs text-muted">
        Copper edges are prerequisites, green edges are uses, gray edges are cross-links. The map shows curated prerequisite and uses edges. Neighborhood adds the closest cross-links.
      </p>
      {error ? <p className="text-warn" role="alert">{error}</p> : null}
      {!graph && !error ? <p className="text-muted">Loading the graph…</p> : null}
      {view.empty ? <p className="text-muted">No topic matches that focus. Try pointer, malloc, or struct.</p> : null}
      <div className="h-[70vh] overflow-hidden rounded-2xl border border-line bg-bg">
        <ReactFlow nodes={view.nodes} edges={view.edges} nodeTypes={nodeTypes} fitView fitViewOptions={{ padding: 0.12, maxZoom: 1 }} minZoom={0.35} proOptions={{ hideAttribution: true }}>
          <Background />
          <Controls />
        </ReactFlow>
      </div>
    </div>
  );
}

function buildView(graph: GraphFile | null, mode: "map" | "near", query: string) {
  if (!graph) return { nodes: [] as Node[], edges: [] as Edge[], empty: false };
  const focus = graph.nodes.find((node) => node.title.toLowerCase().includes(query.trim().toLowerCase()) || node.id.includes(query.trim().toLowerCase()));
  let edges = graph.edges.filter((edge) => edge.kind === "prerequisite" || edge.kind === "uses");
  if (mode === "near" && focus) {
    const near = graph.edges.filter((edge) => edge.source === focus.id || edge.target === focus.id).slice(0, 18);
    const ids = new Set(near.flatMap((edge) => [edge.source, edge.target]));
    edges = graph.edges.filter((edge) => ids.has(edge.source) && ids.has(edge.target) && (edge.kind !== "related" || edge.source === focus.id || edge.target === focus.id)).slice(0, 40);
  }
  const ids = new Set(edges.flatMap((edge) => [edge.source, edge.target]));
  if (focus) ids.add(focus.id);
  const nodes = graph.nodes.filter((node) => ids.has(node.id));
  if (nodes.length === 0) return { nodes: [] as Node[], edges: [] as Edge[], empty: true };
  const ordered = [...nodes].sort((a, b) => a.category.localeCompare(b.category) || a.title.localeCompare(b.title));
  const flowNodes: Node[] = ordered.map((node, index) => ({
    id: node.id,
    type: "topic",
    position: { x: (index % 4) * 240, y: Math.floor(index / 4) * 78 },
    data: { label: node.title, href: `/reference/${node.id}/` },
    style: { width: 210, height: 58, padding: 0, border: "none", background: "transparent" },
  }));
  const flowEdges: Edge[] = edges.map((edge, index) => ({
    id: `${edge.kind}-${edge.source}-${edge.target}-${index}`,
    source: edge.source,
    target: edge.target,
    style: { stroke: kindColor[edge.kind] },
    label: edge.kind === "related" ? "" : edge.kind,
  }));
  return { nodes: flowNodes, edges: flowEdges, empty: false };
}
