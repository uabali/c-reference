#!/usr/bin/env python3
"""Convert the C portion of a cppreference html-book dump into MDX.

The dump is the offline HTML book from PeterFeicht/cppreference-doc.
Only pages under reference/en/c.html and reference/en/c/ are converted.
Output is markdown-compatible MDX: YAML front matter, HTML prose, and
fenced code blocks. Internal C links are rewritten to /reference/<slug>/.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import shutil
import unicodedata
from pathlib import Path

from bs4 import BeautifulSoup, Comment, NavigableString, Tag

DUMP_VERSION = "v20250209"
DUMP_RETRIEVED = "2025-02-09"
DUMP_ARCHIVE = "html-book-20250209.tar.xz"
DUMP_URL = (
    "https://github.com/PeterFeicht/cppreference-doc/releases/download/"
    "v20250209/html-book-20250209.tar.xz"
)

CATEGORY_LABELS = {
    "overview": "Overview",
    "language": "Language",
    "keyword": "Keywords",
    "preprocessor": "Preprocessor",
    "header": "Headers",
    "types": "Type support",
    "program": "Program utilities",
    "variadic": "Variadic functions",
    "error": "Error handling",
    "memory": "Dynamic memory",
    "string": "Strings",
    "algorithm": "Algorithms",
    "numeric": "Numerics",
    "chrono": "Date and time",
    "io": "Input/output",
    "locale": "Localization",
    "thread": "Concurrency",
    "atomic": "Atomics",
    "experimental": "Technical specifications",
    "compiler_support": "Compiler support",
    "symbol_index": "Symbol index",
    "links": "External links",
    "index": "Index",
}

CATEGORY_ORDER = list(CATEGORY_LABELS)


def clean_chars(value: str) -> str:
    value = value.replace("\xa0", " ")
    return "".join(ch for ch in value if unicodedata.category(ch) != "Cf")


def norm_text(value: str) -> str:
    value = clean_chars(value)
    value = re.sub(r"\s+", " ", value)
    return html.escape(value, quote=False)


def code_text(node: Tag) -> str:
    text = clean_chars(node.get_text())
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if text.endswith("\n"):
        text = text[:-1]
    return text


def fence(code: str, lang: str) -> str:
    tick = "```"
    while tick in code:
        tick += "`"
    lang = lang or "text"
    return f"{tick}{lang}\n{code}\n{tick}"


def code_lang(geshi: Tag) -> str:
    classes: list[str] = []
    classes.extend(geshi.get("class") or [])
    for div in geshi.find_all("div"):
        classes.extend(div.get("class") or [])
    joined = " ".join(classes)
    if "source-cpp" in joined:
        return "cpp"
    if "source-c" in joined:
        return "c"
    return "text"


def mark_html(span: Tag) -> str:
    classes = span.get("class") or []
    text = span.get_text(" ", strip=True)
    if not text:
        return ""
    versioned = any("since" in c or "until" in c or c == "t-mark-rev" for c in classes)
    if not versioned:
        return f'<span class="mark-note">{html.escape(text)}</span>'
    kind = "until" if any("until" in c for c in classes) else "since"
    std = "other"
    for key in ("c23", "c17", "c11", "c99", "c95", "c89", "c95"):
        if any(key in c for c in classes):
            std = key
            break
    if std == "other":
        match = re.search(r"C(?:89|95|99|11|17|23)", text)
        if match:
            std = "c" + match.group(0)[1:]
    return f'<span class="std std-{kind} std-{std}">{html.escape(text)}</span>'


class PageConverter:
    def __init__(self, en_root: Path, media_dir: Path) -> None:
        self.en_root = en_root.resolve()
        self.media_dir = media_dir
        self.current: Path = en_root
        self.links: set[str] = set()

    def convert_file(self, path: Path) -> tuple[str, dict]:
        self.current = path
        self.links = set()
        raw = path.read_text(encoding="utf-8", errors="replace")
        soup = BeautifulSoup(raw, "lxml")
        for bad in soup.find_all(["script", "style"]):
            bad.decompose()

        title_el = soup.select_one("h1.firstHeading")
        title = title_el.get_text(" ", strip=True) if title_el else path.stem
        slug = self.slug_for(path)
        source = self.online_url(soup, slug)
        content = soup.select_one("#mw-content-text")
        if content is None:
            body = "<p></p>"
        else:
            navbar = content.select_one(".t-navbar")
            if navbar:
                navbar.decompose()
            body = self.render_children(content).strip() or "<p></p>"

        crumbs = []
        sub = soup.select_one("#contentSub")
        if sub:
            for anchor in sub.select("a"):
                href = self.rewrite(anchor.get("href") or "")
                crumbs.append({"title": anchor.get_text(" ", strip=True), "href": href})

        headings = []
        for match in re.finditer(r"<h([2-6])([^>]*)>(.*?)</h\1>", body, flags=re.S):
            inner = re.sub(r"<[^>]+>", "", match.group(3))
            inner = html.unescape(re.sub(r"\s+", " ", inner)).strip()
            hid = ""
            id_match = re.search(r'id="([^"]+)"', match.group(2))
            if id_match:
                hid = id_match.group(1)
            if inner:
                headings.append({"id": hid, "text": inner, "level": int(match.group(1))})

        plain = self.plain_text(body)
        category = slug.split("/")[1] if slug.startswith("c/") and "/" in slug[2:] else "overview"
        if slug == "c":
            category = "overview"
        summary = plain[:320].rstrip()
        excerpt = plain[:1400].rstrip()
        body_hash = hashlib.sha256(body.encode("utf-8")).hexdigest()
        meta = {
            "title": title,
            "slug": slug,
            "category": category,
            "source": source,
            "retrieved": DUMP_RETRIEVED,
            "license": "CC BY-SA 3.0",
            "dump": DUMP_VERSION,
        }
        front = ["---"]
        for key, value in meta.items():
            front.append(f"{key}: {json.dumps(value, ensure_ascii=False)}")
        front.append("---")
        mdx = "\n".join(front) + "\n\n" + body + "\n"
        record = {
            **meta,
            "summary": summary,
            "excerpt": excerpt,
            "headings": [h["text"] for h in headings],
            "headingIds": headings,
            "links": sorted(self.links),
            "breadcrumbs": crumbs,
            "hash": body_hash,
            "chars": len(plain),
        }
        return mdx, record

    def slug_for(self, path: Path) -> str:
        rel = path.resolve().relative_to(self.en_root)
        slug = str(rel.with_suffix("")).replace("\\", "/")
        return slug

    def online_url(self, soup: BeautifulSoup, slug: str) -> str:
        for anchor in soup.select("#cpp-navigation a, #footer a"):
            href = anchor.get("href") or ""
            if "cppreference.com/w/" in href and "action=edit" not in href:
                return href.split("?")[0]
        return f"https://en.cppreference.com/w/{slug}"

    def rewrite(self, href: str) -> str:
        href = (href or "").strip()
        if not href or href.startswith("javascript:"):
            return "#"
        if href.startswith("#"):
            return href
        if href.startswith(("mailto:", "http://", "https://")):
            rewritten = self.rewrite_absolute(href)
            self.record_link(rewritten)
            return rewritten
        path_part, _, anchor = href.partition("#")
        if not path_part:
            return "#" + anchor if anchor else "#"
        target = (self.current.parent / path_part).resolve()
        try:
            rel = target.relative_to(self.en_root)
        except ValueError:
            return href
        if target.suffix.lower() not in {".html", ".htm"}:
            copied = self.copy_media(target)
            return copied or href
        slug = str(rel.with_suffix("")).replace("\\", "/")
        if slug == "cpp" or slug.startswith("cpp/"):
            url = f"https://en.cppreference.com/w/{slug}"
        elif slug == "c" or slug.startswith("c/"):
            url = f"/reference/{slug}/"
        else:
            url = f"https://en.cppreference.com/w/{slug}"
        if anchor:
            url += "#" + anchor
        self.record_link(url)
        return url

    def rewrite_absolute(self, href: str) -> str:
        if "cppreference.com/w/" not in href or "action=edit" in href:
            return href
        tail = href.split("/w/", 1)[1]
        path, _, anchor = tail.partition("#")
        path = path.strip("/")
        if path == "c" or path.startswith("c/"):
            url = f"/reference/{path}/"
            if anchor:
                url += "#" + anchor
            return url
        return href

    def record_link(self, url: str) -> None:
        if not url.startswith("/reference/"):
            return
        slug = url[len("/reference/") :].split("#", 1)[0].strip("/")
        if slug:
            self.links.add(slug)

    def copy_media(self, source: Path) -> str | None:
        if not source.is_file():
            return None
        digest = hashlib.sha1(str(source).encode("utf-8")).hexdigest()[:8]
        dest_name = f"{digest}-{source.name}"
        self.media_dir.mkdir(parents=True, exist_ok=True)
        dest = self.media_dir / dest_name
        if not dest.exists():
            shutil.copyfile(source, dest)
        return f"/media/cppref/{dest_name}"

    def render_children(self, parent: Tag) -> str:
        chunks: list[str] = []
        for child in parent.children:
            if isinstance(child, Comment):
                continue
            if isinstance(child, NavigableString):
                text = norm_text(str(child)).strip()
                if text:
                    chunks.append(f"<p>{text}</p>")
                continue
            if not isinstance(child, Tag):
                continue
            piece = self.render_block(child)
            if piece and piece.strip():
                chunks.append(piece.strip())
        return "\n\n".join(chunks)

    def render_block(self, el: Tag) -> str:
        if el.name in ("script", "style"):
            return ""
        classes = set(el.get("class") or [])
        if "t-navbar" in classes or "t-example-live-link" in classes or "editsection" in classes:
            return ""
        if el.name in ("a", "span", "em", "strong", "b", "i", "code", "tt", "sub", "sup", "abbr", "kbd", "small", "img"):
            return self.render_inline_tag(el).strip()
        if el.name == "div" and "mw-geshi" in classes:
            return self.render_geshi(el)
        if el.name in ("h2", "h3", "h4", "h5", "h6"):
            return self.render_heading(el)
        if el.name == "p":
            inner = self.inline(el).strip()
            return f"<p>{inner}</p>" if inner else ""
        if el.name == "table":
            if "t-dcl-begin" in classes:
                return self.render_decls(el)
            if "t-sdsc-begin" in classes:
                return self.render_syntax(el)
            if "t-rev-begin" in classes:
                return self.render_rev(el)
            return self.render_table(el)
        if el.name in ("ul", "ol"):
            return self.render_list(el)
        if el.name == "dl":
            return self.render_dl(el)
        if el.name == "pre":
            return fence(code_text(el), "text")
        if el.name == "blockquote":
            inner = self.render_children(el)
            return f"<blockquote>{inner}</blockquote>" if inner else ""
        if el.name == "hr":
            return "<hr />"
        if el.name == "div":
            if "t-li1" in classes:
                if el.find(["dl", "table", "ul", "ol", "pre"]) or el.select_one("div.mw-geshi"):
                    return f'<div class="li-note">{self.render_children(el)}</div>'
                inner = self.inline(el).strip()
                return f'<p class="li-note">{inner}</p>' if inner else ""
            ref_cls = next((c for c in classes if c.startswith("t-ref-std")), "")
            inner = self.render_children(el)
            if not inner:
                return ""
            if ref_cls:
                std = ref_cls.removeprefix("t-ref-std").strip("-") or "std"
                return f'<section class="std-ref std-ref-{html.escape(std)}">{inner}</section>'
            return inner
        return self.render_children(el)

    def render_heading(self, el: Tag) -> str:
        span = el.find("span", class_="mw-headline")
        hid = ""
        if span and span.get("id"):
            hid = span["id"]
        elif el.get("id"):
            hid = el["id"]
        inner = self.inline(span or el).strip()
        if not hid:
            hid = re.sub(r"\s+", "_", html.unescape(re.sub(r"<[^>]+>", "", inner)))[:80]
        return f'<{el.name} id="{html.escape(hid, quote=True)}">{inner}</{el.name}>'

    def render_geshi(self, el: Tag) -> str:
        pre = el.find("pre")
        if pre is None:
            return fence(code_text(el), code_lang(el))
        return fence(code_text(pre), code_lang(el))

    def render_list(self, el: Tag) -> str:
        items = []
        for li in el.find_all("li", recursive=False):
            inner = self.render_children(li).strip()
            if not inner:
                text = self.inline(li).strip()
                inner = f"<p>{text}</p>" if text else ""
            if inner:
                items.append(f"<li>\n{inner}\n</li>")
        if not items:
            return ""
        body = "\n".join(items)
        return f"<{el.name}>\n{body}\n</{el.name}>"

    def render_dl(self, el: Tag) -> str:
        parts = []
        for child in el.find_all(["dt", "dd"], recursive=False):
            inner = self.render_children(child).strip() or self.inline(child).strip()
            if inner:
                parts.append(f"<{child.name}>{inner}</{child.name}>")
        if not parts:
            return ""
        return "<dl>\n" + "\n".join(parts) + "\n</dl>"

    def iter_rows(self, table: Tag):
        for child in table.children:
            if not isinstance(child, Tag):
                continue
            if child.name == "tr":
                yield child
            elif child.name in ("tbody", "thead", "tfoot"):
                for row in child.find_all("tr", recursive=False):
                    yield row

    def render_table(self, el: Tag) -> str:
        classes = set(el.get("class") or [])
        rows = []
        for tr in self.iter_rows(el):
            cells = []
            for cell in tr.find_all(["th", "td"], recursive=False):
                if cell.find(["p", "div", "table", "pre", "ul", "ol", "dl"]):
                    inner = self.render_children(cell).strip()
                else:
                    inner = self.inline(cell).strip()
                attrs = ""
                if cell.get("colspan"):
                    attrs += f' colspan="{html.escape(str(cell["colspan"]), quote=True)}"'
                if cell.get("rowspan"):
                    attrs += f' rowspan="{html.escape(str(cell["rowspan"]), quote=True)}"'
                cells.append(f"<{cell.name}{attrs}>{inner}</{cell.name}>")
            if cells:
                rows.append("<tr>" + "".join(cells) + "</tr>")
        if not rows:
            return ""
        cls = ["ref-table"]
        if "t-dsc-begin" in classes:
            cls.append("ref-dsc")
        if "t-par-begin" in classes:
            cls.append("ref-params")
        return f'<table class="{" ".join(cls)}">\n' + "\n".join(rows) + "\n</table>"

    def render_decls(self, table: Tag) -> str:
        chunks: list[str] = []
        for tr in self.iter_rows(table):
            classes = set(tr.get("class") or [])
            if "t-dcl-sep" in classes:
                continue
            cells = tr.find_all("td", recursive=False)
            if not cells:
                continue
            if "t-dsc-header" in classes or "t-dcl-header" in classes:
                header = self.inline(cells[0]).strip()
                if header:
                    chunks.append(f'<p class="decl-header">{header}</p>')
                continue
            geshi = cells[0].select_one(".mw-geshi")
            pre = cells[0].find("pre")
            if geshi is not None or pre is not None:
                node = pre or geshi
                assert node is not None
                chunks.append(fence(code_text(node), "c" if geshi is None else code_lang(geshi)))
            else:
                signature = clean_chars(cells[0].get_text())
                signature = re.sub(r"\s+", " ", signature).strip()
                if signature:
                    chunks.append(fence(signature, "c"))
            notes = [self.inline(td).strip() for td in cells[1:]]
            notes = [note for note in notes if note]
            if notes:
                chunks.append(f'<p class="decl-note">{" ".join(notes)}</p>')
        return "\n\n".join(chunks)

    def render_syntax(self, table: Tag) -> str:
        lines = []
        for tr in self.iter_rows(table):
            if "t-sdsc" not in (tr.get("class") or []):
                continue
            cell = tr.find("td")
            if cell is None:
                continue
            text = clean_chars(cell.get_text())
            text = re.sub(r"\s+", " ", text).strip()
            if text:
                lines.append(text)
        if not lines:
            return ""
        return fence("\n".join(lines), "text")

    def render_rev(self, table: Tag) -> str:
        chunks = []
        for tr in self.iter_rows(table):
            cells = tr.find_all("td", recursive=False)
            if not cells:
                continue
            body = self.render_children(cells[0]).strip()
            if not body:
                text = self.inline(cells[0]).strip()
                body = f"<p>{text}</p>" if text else ""
            mark = self.inline(cells[1]).strip() if len(cells) > 1 else ""
            if mark:
                mark = f'<p class="rev-mark">{mark}</p>'
            if body or mark:
                chunks.append(f'<aside class="revision">{mark}{body}</aside>')
        return "\n\n".join(chunks)

    def inline(self, node: Tag) -> str:
        parts: list[str] = []
        for child in node.children:
            if isinstance(child, Comment):
                continue
            if isinstance(child, NavigableString):
                parts.append(norm_text(str(child)))
                continue
            if isinstance(child, Tag):
                parts.append(self.render_inline_tag(child))
        return "".join(parts)

    def render_inline_tag(self, child: Tag) -> str:
        if child.name in ("script", "style"):
            return ""
        classes = set(child.get("class") or [])
        if "t-navbar" in classes or "editsection" in classes:
            return ""
        if child.name == "br":
            return " "
        if child.name == "img":
            return self.render_img(child)
        if child.name == "a":
            if child.get("id") and not child.get_text(strip=True) and not child.find("img"):
                return f'<a id="{html.escape(child["id"], quote=True)}"></a>'
            href = self.rewrite(child.get("href") or "")
            inner = self.inline(child).strip()
            if not inner:
                return ""
            extra = ""
            if href.startswith("http://") or href.startswith("https://"):
                extra = ' rel="noreferrer" target="_blank"'
            return f'<a href="{html.escape(href, quote=True)}"{extra}>{inner}</a>'
        if "t-lines" in classes and child.name == "span":
            bits = []
            for sub in child.find_all("span", recursive=False):
                bit = self.inline(sub).strip()
                if bit:
                    bits.append(bit)
            if bits:
                return "<br />".join(bits)
        if "mw-geshi" in classes or "t-c" in classes or child.name in ("code", "tt", "kbd"):
            text = clean_chars(child.get_text())
            text = re.sub(r"\s+", " ", text).strip()
            return f"<code>{html.escape(text)}</code>" if text else ""
        if any(c.startswith("t-mark") for c in classes):
            return mark_html(child)
        if child.name == "span" and "t-li" in classes:
            text = child.get_text(strip=True)
            return f'<span class="li-num">{html.escape(text)}</span> ' if text else ""
        if child.name in ("b", "strong") or "selflink" in classes:
            inner = self.inline(child)
            return f"<strong>{inner}</strong>" if inner.strip() else ""
        if child.name in ("i", "em") or "t-spar" in classes:
            inner = self.inline(child)
            return f"<em>{inner}</em>" if inner.strip() else ""
        if child.name in ("sub", "sup"):
            return f"<{child.name}>{self.inline(child)}</{child.name}>"
        if child.name == "div" and "mw-geshi" in classes:
            return self.render_geshi(child)
        return self.inline(child)

    def render_img(self, el: Tag) -> str:
        src = el.get("src") or ""
        if not src or src.startswith("data:"):
            return ""
        if src.startswith(("http://", "https://")):
            url = src
        else:
            target = (self.current.parent / src).resolve()
            copied = self.copy_media(target)
            if not copied:
                return ""
            url = copied
        alt = el.get("alt") or ""
        return (
            f'<img src="{html.escape(url, quote=True)}" '
            f'alt="{html.escape(alt, quote=True)}" />'
        )

    @staticmethod
    def plain_text(body: str) -> str:
        without_fences = re.sub(r"```[^\n]*\n", "", body)
        without_fences = without_fences.replace("```", " ")
        text = re.sub(r"<[^>]+>", " ", without_fences)
        text = html.unescape(text)
        return re.sub(r"\s+", " ", text).strip()


def iter_pages(en_root: Path):
    root_page = en_root / "c.html"
    if root_page.is_file():
        yield root_page
    c_dir = en_root / "c"
    if c_dir.is_dir():
        for path in sorted(c_dir.rglob("*.html")):
            yield path


def write_search_documents(pages: list[dict], dest: Path) -> None:
    docs = []
    for page in pages:
        headings = " ".join(page.get("headings") or [])
        summary = page.get("summary") or ""
        excerpt = page.get("excerpt") or summary
        docs.append(
            {
                "slug": page["slug"],
                "title": page["title"],
                "category": page["category"],
                "headings": headings,
                "summary": summary,
                "excerpt": excerpt,
                "text": f"{page['title']}. {headings}. {excerpt}".strip(),
            }
        )
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(docs, ensure_ascii=False), encoding="utf-8")


def convert_tree(en_root: Path, content_dir: Path, public_dir: Path) -> dict:
    en_root = en_root.resolve()
    mdx_root = content_dir / "mdx"
    if mdx_root.exists():
        shutil.rmtree(mdx_root)
    mdx_root.mkdir(parents=True)
    media_dir = public_dir / "media" / "cppref"
    converter = PageConverter(en_root, media_dir)
    pages = []
    for index, path in enumerate(iter_pages(en_root), start=1):
        mdx, record = converter.convert_file(path)
        rel = Path(record["slug"] + ".mdx")
        dest = mdx_root / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(mdx, encoding="utf-8")
        pages.append(record)
        if index % 100 == 0:
            print(f"converted {index} pages")
    known = {page["slug"] for page in pages}
    for page in pages:
        page["links"] = [link for link in page["links"] if link in known and link != page["slug"]]
    pages.sort(key=lambda page: (page["title"].lower(), page["slug"]))
    catalog = {
        "dump": DUMP_VERSION,
        "archive": DUMP_ARCHIVE,
        "archiveUrl": DUMP_URL,
        "retrieved": DUMP_RETRIEVED,
        "license": "CC BY-SA 3.0",
        "original": "https://en.cppreference.com/w/c",
        "pageCount": len(pages),
        "categories": [
            {"id": key, "title": CATEGORY_LABELS[key]}
            for key in CATEGORY_ORDER
            if any(page["category"] == key for page in pages)
        ],
        "pages": pages,
    }
    content_dir.mkdir(parents=True, exist_ok=True)
    write_search_documents(pages, public_dir / "search" / "documents.json")
    for page in pages:
        page.pop("excerpt", None)
    (content_dir / "catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False), encoding="utf-8"
    )
    (content_dir / "SOURCE.json").write_text(
        json.dumps(
            {
                "dump": DUMP_VERSION,
                "archive": DUMP_ARCHIVE,
                "archiveUrl": DUMP_URL,
                "retrieved": DUMP_RETRIEVED,
                "license": "CC BY-SA 3.0",
                "original": "https://en.cppreference.com/w/c",
                "upstreamRepo": "https://github.com/PeterFeicht/cppreference-doc",
                "note": (
                    "Latest html-book release verified on 2026-11-01. "
                    "The April 2026 cppreference redesign broke the upstream "
                    "update scripts (PeterFeicht/cppreference-doc issue 51); "
                    "no newer html-book has been published."
                ),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"wrote {len(pages)} pages")
    return catalog


def main() -> None:
    repo = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--html-root",
        type=Path,
        default=Path("/tmp/cppref/reference/en"),
        help="Path to reference/en inside an extracted html-book",
    )
    parser.add_argument("--content", type=Path, default=repo / "content")
    parser.add_argument("--public", type=Path, default=repo / "public")
    args = parser.parse_args()
    if not (args.html_root / "c.html").is_file():
        raise SystemExit(f"C root page not found at {args.html_root / 'c.html'}")
    convert_tree(args.html_root, args.content, args.public)


if __name__ == "__main__":
    main()
