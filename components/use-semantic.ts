"use client";

import { useEffect, useState } from "react";
import { cosineTopK } from "@/lib/vectors";

export type SearchDoc = {
  slug: string;
  title: string;
  category: string;
  headings: string;
  summary: string;
  excerpt: string;
  text: string;
};

type Extractor = (text: string, options: { pooling: "mean"; normalize: true }) => Promise<{ data: Float32Array }>;

let extractorPromise: Promise<Extractor> | null = null;

async function getExtractor() {
  if (!extractorPromise) {
    extractorPromise = import("@xenova/transformers").then(async ({ pipeline, env }) => {
      env.allowRemoteModels = false;
      env.allowLocalModels = true;
      env.localModelPath = "/models";
      env.backends.onnx.wasm.wasmPaths = "/ort/";
      env.backends.onnx.wasm.numThreads = 1;
      const pipe = await pipeline("feature-extraction", "Xenova/all-MiniLM-L6-v2", { quantized: true });
      return pipe as Extractor;
    });
  }
  return extractorPromise;
}

export function useSemanticIndex() {
  const [docs, setDocs] = useState<SearchDoc[] | null>(null);
  const [matrix, setMatrix] = useState<Float32Array | null>(null);
  const [dim, setDim] = useState(384);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancel = false;
    Promise.all([
      fetch("/search/documents.json").then((response) => response.json()),
      fetch("/search/embeddings.bin").then((response) => response.arrayBuffer()),
      fetch("/search/embedding-meta.json").then((response) => response.json()),
    ])
      .then(([documents, buffer, meta]) => {
        if (cancel) return;
        if (!Array.isArray(documents) || documents.length !== meta.count) {
          setError("The search index and embedding file are out of step. Rebuild embeddings.");
          return;
        }
        setDocs(documents as SearchDoc[]);
        setMatrix(new Float32Array(buffer));
        setDim(meta.dim);
      })
      .catch(() => {
        if (!cancel) setError("Could not load the local search index.");
      });
    return () => {
      cancel = true;
    };
  }, []);

  async function search(query: string, k = 8) {
    if (!docs || !matrix) throw new Error("Index is still loading.");
    const extractor = await getExtractor();
    const output = await extractor(query, { pooling: "mean", normalize: true });
    return cosineTopK(output.data, matrix, dim, k).map((hit) => ({
      score: hit.score,
      doc: docs[hit.index],
    }));
  }

  return { docs, error, ready: Boolean(docs && matrix), search };
}
