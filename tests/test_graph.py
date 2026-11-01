"""Graph construction prefers curated edges and drops unknown slugs."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from build_graph import build_graph, build_neighbors  # noqa: E402


def test_curated_prerequisite_outranks_related() -> None:
    catalog = {
        "pages": [
            {"slug": "c/language/pointer", "title": "Pointer", "category": "language", "links": ["c/language/array", "c/memory/malloc"]},
            {"slug": "c/language/array", "title": "Array", "category": "language", "links": []},
            {"slug": "c/memory/malloc", "title": "malloc", "category": "memory", "links": []},
        ]
    }
    graph = build_graph(
        catalog,
        [{"source": "c/language/pointer", "target": "c/memory/malloc", "kind": "prerequisite"}],
    )
    kinds = {(edge["source"], edge["target"]): edge["kind"] for edge in graph["edges"]}
    assert kinds[("c/language/pointer", "c/memory/malloc")] == "prerequisite"
    assert kinds[("c/language/pointer", "c/language/array")] == "related"
    neighbors = build_neighbors(graph, limit=2)
    assert neighbors["c/language/pointer"][0]["slug"] == "c/memory/malloc"
    assert neighbors["c/language/pointer"][0]["kind"] == "prerequisite"


def test_unknown_slug_is_dropped() -> None:
    catalog = {"pages": [{"slug": "c/language/pointer", "title": "Pointer", "category": "language", "links": ["c/missing"]}]}
    graph = build_graph(catalog, [{"source": "c/nope", "target": "c/language/pointer", "kind": "uses"}])
    assert graph["edges"] == []
