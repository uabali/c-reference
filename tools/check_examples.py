#!/usr/bin/env python3
"""Compile and run every curated example with the compiler it names."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


def load(path: Path):
    if not path.is_file():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def check(code: str, compiler: str, options: str, label: str) -> str | None:
    with tempfile.TemporaryDirectory() as temp:
        source = Path(temp) / "example.c"
        binary = Path(temp) / "example"
        source.write_text(code, encoding="utf-8")
        cmd = [compiler, *options.split(), str(source), "-o", str(binary)]
        compiled = subprocess.run(cmd, capture_output=True, text=True)
        if compiled.returncode != 0:
            return f"{label}: compile failed\n{compiled.stderr}"
        if compiled.stderr.strip():
            print(f"{label}: warnings\n{compiled.stderr}", file=sys.stderr)
        ran = subprocess.run([str(binary)], capture_output=True, text=True)
        if ran.returncode != 0:
            return f"{label}: exited {ran.returncode}\nstdout:{ran.stdout}\nstderr:{ran.stderr}"
    return None


def main() -> None:
    repo = Path(__file__).resolve().parents[1]
    curated = repo / "content" / "curated"
    jobs: list[tuple[str, str, str, str]] = []
    for item in load(curated / "enrichment.json"):
        for index, example in enumerate(item["examples"]):
            jobs.append((example["code"], example["compiler"], example["options"], f"{item['slug']}#{index} {example['title']}"))
    for item in load(curated / "real-world.json"):
        jobs.append((item["code"], item["compiler"], item["options"], f"real-world {item['slug']}"))
    for item in load(curated / "mistakes.json"):
        if "int main" in item.get("right", ""):
            jobs.append((item["right"], "clang", "-std=c23 -Wall -Wextra", f"mistake {item['title']}"))
    failures = []
    for code, compiler, options, label in jobs:
        error = check(code, compiler, options, label)
        if error:
            failures.append(error)
        else:
            print(f"ok {label}")
    if not jobs:
        raise SystemExit("no examples found")
    if failures:
        print("\n".join(failures))
        raise SystemExit(f"{len(failures)} example(s) failed out of {len(jobs)}")
    print(f"all {len(jobs)} examples compiled and ran")


if __name__ == "__main__":
    main()
