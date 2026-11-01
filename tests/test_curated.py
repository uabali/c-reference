"""Curated notes stay attached to real reference pages."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_enrichment_covers_the_important_topics() -> None:
    catalog = json.loads((ROOT / "content" / "catalog.json").read_text(encoding="utf-8"))
    known = {page["slug"] for page in catalog["pages"]}
    rows = json.loads((ROOT / "content" / "curated" / "enrichment.json").read_text(encoding="utf-8"))
    assert len(rows) >= 40
    slugs = [row["slug"] for row in rows]
    assert len(slugs) == len(set(slugs))
    assert set(slugs) <= known
    for row in rows:
        assert row["difficulty"] in {"Beginner", "Intermediate", "Advanced"}
        assert row["why"] and row["when"]
        assert len(row["pitfalls"]) >= 2
        assert len(row["practice"]) >= 2
        assert row["examples"]
        for example in row["examples"]:
            assert "int main" in example["code"]
            assert example["compiler"] in {"clang", "gcc"}
