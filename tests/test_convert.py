"""Tests for the cppreference HTML -> MDX conversion pipeline."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from convert import PageConverter, convert_tree  # noqa: E402
from sync_upstream import diff_pages  # noqa: E402


FIXTURE = Path(__file__).parent / "fixtures" / "sample.html"


def _converter(tmp_path: Path) -> tuple[PageConverter, Path]:
    en = tmp_path / "en"
    (en / "c" / "language").mkdir(parents=True)
    (en / "cpp" / "language").mkdir(parents=True)
    page = en / "c" / "language" / "pointer.html"
    page.write_text(FIXTURE.read_text(encoding="utf-8"), encoding="utf-8")
    (en / "c.html").write_text("<html><body><h1 id='firstHeading'>C</h1><div id='mw-content-text'><p>Root</p></div></body></html>", encoding="utf-8")
    (en / "c" / "language.html").write_text("<html></html>", encoding="utf-8")
    (en / "c" / "language" / "array.html").write_text("<html></html>", encoding="utf-8")
    (en / "c" / "language" / "nullptr.html").write_text("<html></html>", encoding="utf-8")
    media = tmp_path / "media"
    converter = PageConverter(en, media)
    return converter, page


def test_preserves_code_rewrites_links_and_strips_chrome(tmp_path: Path) -> None:
    converter, page = _converter(tmp_path)
    mdx, record = converter.convert_file(page)

    assert record["title"] == "Pointer declaration"
    assert record["slug"] == "c/language/pointer"
    assert record["source"] == "https://en.cppreference.com/w/c/language/pointer"
    assert record["license"] == "CC BY-SA 3.0"
    assert "NAVBAR_SENTINEL" not in mdx
    assert "window.evil" not in mdx
    assert "```c\n" in mdx
    assert "int *p;" in mdx
    assert 'href="/reference/c/language/array/"' in mdx
    assert 'href="/reference/c/language/nullptr/"' in mdx
    assert "https://en.cppreference.com/w/cpp/language/pointer" in mdx
    assert 'id="Syntax"' in mdx
    assert "std-since" in mdx and "std-c23" in mdx
    assert "<table" in mdx
    assert "pointer value" in mdx
    assert "* qualifiers" in mdx
    assert "c/language/array" in record["links"]
    assert "c/language/array" in converter.links
    assert "c/language/nullptr" in converter.links
    assert "cpp/language/pointer" not in converter.links


def test_tree_filters_links_and_writes_catalog(tmp_path: Path) -> None:
    en = tmp_path / "en"
    (en / "c" / "language").mkdir(parents=True)
    (en / "c.html").write_text(
        "<html><body><h1 id='firstHeading'>C reference</h1>"
        "<div id='mw-content-text'><p>See <a href='c/language/pointer.html'>pointers</a>.</p></div>"
        "<div id='footer'><a href='https://en.cppreference.com/w/c'>Online version</a></div></body></html>",
        encoding="utf-8",
    )
    (en / "c" / "language" / "pointer.html").write_text(FIXTURE.read_text(encoding="utf-8"), encoding="utf-8")
    content = tmp_path / "content"
    public = tmp_path / "public"
    catalog = convert_tree(en, content, public)
    slugs = {page["slug"] for page in catalog["pages"]}
    assert slugs == {"c", "c/language/pointer"}
    pointer = next(page for page in catalog["pages"] if page["slug"] == "c/language/pointer")
    assert "c/language/array" not in pointer["links"]
    assert (content / "mdx" / "c" / "language" / "pointer.mdx").is_file()
    docs = json.loads((public / "search" / "documents.json").read_text(encoding="utf-8"))
    assert {doc["slug"] for doc in docs} == slugs
    assert any("Pointer declaration" in doc["title"] for doc in docs)


def test_diff_pages_reports_added_removed_and_changed() -> None:
    old = [
        {"slug": "c/a", "hash": "1", "title": "A"},
        {"slug": "c/b", "hash": "2", "title": "B"},
    ]
    new = [
        {"slug": "c/b", "hash": "9", "title": "B"},
        {"slug": "c/c", "hash": "3", "title": "C"},
    ]
    diff = diff_pages(old, new)
    assert diff["added"] == ["c/c"]
    assert diff["removed"] == ["c/a"]
    assert diff["changed"] == ["c/b"]


def test_real_dump_pointer_page_if_present() -> None:
    html = Path("/tmp/cppref/reference/en/c/language/pointer.html")
    if not html.is_file():
        pytest.skip("cppreference dump is not extracted")
    converter = PageConverter(Path("/tmp/cppref/reference/en"), Path("/tmp/pytest-media"))
    mdx, record = converter.convert_file(html)
    assert record["title"] == "Pointer declaration"
    assert "```c\n" in mdx
    assert "float *p" in mdx
    assert 'href="/reference/c/language/array/"' in mdx
    assert "t-navbar" not in mdx
    assert "googletagmanager" not in mdx
    assert record["source"].startswith("https://en.cppreference.com/w/c/language/pointer")
