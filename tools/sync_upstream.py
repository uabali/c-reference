#!/usr/bin/env python3
"""Detect content diffs against a newer cppreference html-book dump.

By default this contacts the GitHub releases API, downloads the latest
html-book archive if it differs from the dump recorded in content/SOURCE.json,
converts it in a temporary directory, and writes reports/upstream-diff.md.

Pass --apply to replace content/mdx, content/catalog.json, and the search
documents. Curated enrichment is never overwritten.
"""

from __future__ import annotations

import argparse
import json
import shutil
import tarfile
import tempfile
import urllib.request
from pathlib import Path

from convert import convert_tree

API = "https://api.github.com/repos/PeterFeicht/cppreference-doc/releases/latest"
USER_AGENT = "c-umutabali-upstream-sync"


def diff_pages(old_pages: list[dict], new_pages: list[dict]) -> dict:
    old = {page["slug"]: page.get("hash", "") for page in old_pages}
    new = {page["slug"]: page.get("hash", "") for page in new_pages}
    added = sorted(set(new) - set(old))
    removed = sorted(set(old) - set(new))
    changed = sorted(slug for slug in set(old) & set(new) if old[slug] != new[slug])
    return {"added": added, "removed": removed, "changed": changed}


def fetch_latest_release() -> dict:
    request = urllib.request.Request(
        API,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": USER_AGENT,
        },
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def html_book_asset(release: dict) -> dict:
    assets = release.get("assets") or []
    books = [
        asset
        for asset in assets
        if asset.get("name", "").startswith("html-book-") and asset["name"].endswith(".tar.xz")
    ]
    if not books:
        raise SystemExit("latest release has no html-book tar.xz asset")
    return books[0]


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=180) as response, dest.open("wb") as handle:
        shutil.copyfileobj(response, handle)


def extract_c_portion(archive: Path, dest: Path) -> Path:
    """Extract reference/en (C pages live beside C++ pages; converter ignores C++)."""
    dest.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive, "r:xz") as tar:
        members = [
            member
            for member in tar.getmembers()
            if member.name.startswith("reference/en/") or member.name.startswith("reference/common/images/")
        ]
        tar.extractall(dest, members=members, filter="data")
    en_root = dest / "reference" / "en"
    if not (en_root / "c.html").is_file():
        raise SystemExit(f"extracted archive has no C root at {en_root}")
    return en_root


def render_report(current: str, latest: str, asset_name: str, diff: dict | None, note: str) -> str:
    lines = [
        "# Upstream diff",
        "",
        f"- Recorded dump: `{current}`",
        f"- Latest html-book: `{latest}` ({asset_name})",
        "",
        note,
        "",
    ]
    if diff is not None:
        lines.append(f"- Added: {len(diff['added'])}")
        lines.append(f"- Removed: {len(diff['removed'])}")
        lines.append(f"- Changed: {len(diff['changed'])}")
        lines.append("")
        for label in ("added", "removed", "changed"):
            lines.append(f"## {label.title()}")
            lines.append("")
            rows = diff[label]
            if not rows:
                lines.append("_None._")
            else:
                lines.extend(f"- `{slug}`" for slug in rows[:400])
                if len(rows) > 400:
                    lines.append(f"- … {len(rows) - 400} more")
            lines.append("")
    lines.append(
        "Re-run `python3 tools/sync_upstream.py --apply` to replace generated MDX. "
        "Files under `content/curated/` are left untouched."
    )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    repo = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Replace generated content with the new dump")
    parser.add_argument("--archive", type=Path, help="Use a local html-book tar.xz instead of GitHub")
    parser.add_argument("--force", action="store_true", help="Diff even when the release tag matches")
    parser.add_argument("--content", type=Path, default=repo / "content")
    parser.add_argument("--public", type=Path, default=repo / "public")
    parser.add_argument("--report", type=Path, default=repo / "reports" / "upstream-diff.md")
    args = parser.parse_args()

    source_path = args.content / "SOURCE.json"
    current = "unknown"
    if source_path.is_file():
        current = json.loads(source_path.read_text(encoding="utf-8")).get("dump", current)

    if args.archive:
        archive = args.archive
        latest = archive.stem
        asset_name = archive.name
    else:
        release = fetch_latest_release()
        asset = html_book_asset(release)
        latest = release.get("tag_name") or asset["name"]
        asset_name = asset["name"]
        archive = repo / ".cache" / "cppref" / asset_name
        if not archive.is_file():
            print(f"downloading {asset['browser_download_url']}")
            download(asset["browser_download_url"], archive)

    if latest == current and not args.force and not args.archive:
        report = render_report(
            current,
            latest,
            asset_name,
            None,
            "No newer html-book release. Pass --force to reconvert and diff anyway.",
        )
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(report, encoding="utf-8")
        print(report)
        return

    with tempfile.TemporaryDirectory(prefix="cppref-sync-") as temp:
        en_root = extract_c_portion(archive, Path(temp) / "dump")
        out_content = Path(temp) / "content"
        out_public = Path(temp) / "public"
        new_catalog = convert_tree(en_root, out_content, out_public)
        old_pages = []
        catalog_path = args.content / "catalog.json"
        if catalog_path.is_file():
            old_pages = json.loads(catalog_path.read_text(encoding="utf-8")).get("pages", [])
        diff = diff_pages(old_pages, new_catalog["pages"])
        report = render_report(
            current,
            latest,
            asset_name,
            diff,
            "Compared converted page bodies by SHA-256.",
        )
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(report, encoding="utf-8")
        print(report)
        if args.apply:
            mdx_dest = args.content / "mdx"
            if mdx_dest.exists():
                shutil.rmtree(mdx_dest)
            shutil.copytree(out_content / "mdx", mdx_dest)
            shutil.copyfile(out_content / "catalog.json", args.content / "catalog.json")
            shutil.copyfile(out_content / "SOURCE.json", args.content / "SOURCE.json")
            docs = args.public / "search" / "documents.json"
            docs.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(out_public / "search" / "documents.json", docs)
            media_src = out_public / "media" / "cppref"
            if media_src.exists():
                media_dest = args.public / "media" / "cppref"
                if media_dest.exists():
                    shutil.rmtree(media_dest)
                shutil.copytree(media_src, media_dest)
            print("applied upstream content")


if __name__ == "__main__":
    main()
