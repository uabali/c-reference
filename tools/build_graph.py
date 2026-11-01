#!/usr/bin/env python3
"""Build the topic graph from converted links plus curated edges."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def build_graph(catalog: dict, curated_edges: list[dict]) -> dict:
    pages = catalog["pages"]
    known = {page["slug"] for page in pages}
    nodes = [
        {
            "id": page["slug"],
            "title": page["title"],
            "category": page["category"],
        }
        for page in pages
    ]
    edges: list[dict] = []
    seen: set[tuple[str, str, str]] = set()
    curated_pairs: set[tuple[str, str]] = set()

    def add(source: str, target: str, kind: str) -> None:
        if source == target or source not in known or target not in known:
            return
        pair = (source, target)
        if kind == "related" and pair in curated_pairs:
            return
        key = (source, target, kind)
        if key in seen:
            return
        seen.add(key)
        if kind != "related":
            curated_pairs.add(pair)
        edges.append({"source": source, "target": target, "kind": kind})

    for edge in curated_edges:
        add(edge["source"], edge["target"], edge.get("kind", "related"))

    for page in pages:
        for target in page.get("links") or []:
            add(page["slug"], target, "related")

    return {
        "directed": True,
        "kinds": ["prerequisite", "related", "uses"],
        "nodeCount": len(nodes),
        "edgeCount": len(edges),
        "nodes": nodes,
        "edges": edges,
    }


def build_neighbors(graph: dict, limit: int = 8) -> dict:
    titles = {node["id"]: node["title"] for node in graph["nodes"]}
    categories = {node["id"]: node["category"] for node in graph["nodes"]}
    rank = {"prerequisite": 0, "uses": 1, "related": 2}
    buckets: dict[str, list[dict]] = {node["id"]: [] for node in graph["nodes"]}
    for edge in graph["edges"]:
        buckets[edge["source"]].append(
            {
                "slug": edge["target"],
                "title": titles.get(edge["target"], edge["target"]),
                "category": categories.get(edge["target"], ""),
                "kind": edge["kind"],
                "direction": "out",
            }
        )
        buckets[edge["target"]].append(
            {
                "slug": edge["source"],
                "title": titles.get(edge["source"], edge["source"]),
                "category": categories.get(edge["source"], ""),
                "kind": edge["kind"],
                "direction": "in",
            }
        )
    neighbors = {}
    for slug, items in buckets.items():
        items.sort(key=lambda item: (rank.get(item["kind"], 9), item["title"].lower()))
        chosen = []
        seen = set()
        for item in items:
            if item["slug"] in seen:
                continue
            seen.add(item["slug"])
            chosen.append(item)
            if len(chosen) >= limit:
                break
        if chosen:
            neighbors[slug] = chosen
    return neighbors


def main() -> None:
    repo = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=repo / "content" / "catalog.json")
    parser.add_argument(
        "--curated",
        type=Path,
        default=repo / "content" / "curated" / "edges.json",
    )
    parser.add_argument("--out", type=Path, default=repo / "public" / "graph.json")
    parser.add_argument(
        "--neighbors",
        type=Path,
        default=repo / "content" / "neighbors.json",
    )
    args = parser.parse_args()
    catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
    curated = []
    if args.curated.is_file():
        curated = json.loads(args.curated.read_text(encoding="utf-8"))
    graph = build_graph(catalog, curated)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(graph, ensure_ascii=False), encoding="utf-8")
    neighbors = build_neighbors(graph)
    args.neighbors.parent.mkdir(parents=True, exist_ok=True)
    args.neighbors.write_text(json.dumps(neighbors, ensure_ascii=False), encoding="utf-8")
    print(f"graph nodes={graph['nodeCount']} edges={graph['edgeCount']} neighbor-pages={len(neighbors)}")


if __name__ == "__main__":
    main()
