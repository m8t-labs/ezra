#!/usr/bin/env python3
"""Run every gate over this repository.

    python ci/check.py            # from the repository root
    python ci/check.py --list     # what each rule family checks, and nothing else

Exits 0 when the repository is clean, 1 on any finding. Every finding is also emitted as a
GitHub workflow annotation, so a pull request shows the problem on the offending line.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ci.rules.canonical import is_canonical     # noqa: E402
from ci.rules.contracts import Finding          # noqa: E402
from ci.rules.corpus import check_corpus        # noqa: E402
from ci.rules.hygiene import is_ingested, scan_text  # noqa: E402
from ci.rules.layout import check_layout        # noqa: E402
from ci.rules.links import check_links          # noqa: E402
from ci.rules.persona import check_persona      # noqa: E402
from ci.rules.primitives import check_primitives  # noqa: E402
from ci.rules.tree import text_files            # noqa: E402

CI_DIR = Path(__file__).resolve().parent

FAMILIES = {
    "layout": "the agent-repo layout: required files, live brain space, no symlinks in the consumed set",
    "persona": "the agent definition: name, version, decision policy, and the Voice golden",
    "corpus": "the skill corpus: frontmatter, required sections, index and routing registration",
    "primitives": "the two reference documents the platform parses as wire contracts",
    "links": "every internal reference resolves — backticked paths, markdown links, bare paths",
    "hygiene": "nothing internal, secret or personal reaches a public branch",
}


def _repo_config(ci_dir: Path) -> dict:
    return json.loads((ci_dir / "repo.json").read_text(encoding="utf-8"))


def run(root: Path, ci_dir: Path) -> list[Finding]:
    config = _repo_config(ci_dir)
    voice_golden = (ci_dir / "golden" / "voice.md").read_text(encoding="utf-8")

    canonical = is_canonical(root, config.get("canonical"))

    findings: list[Finding] = []
    findings += check_layout(root)
    findings += check_persona(root, config["persona"], voice_golden, canonical)
    findings += check_corpus(root)
    findings += check_primitives(root)
    findings += check_links(root)
    for rel in text_files(root):
        text = (root / rel).read_text(encoding="utf-8", errors="replace")
        findings += scan_text(text, rel, ingested=is_ingested(rel))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", help="repository root (default: cwd)")
    parser.add_argument("--list", action="store_true", help="describe the rule families and exit")
    args = parser.parse_args()

    if args.list:
        for name, what in FAMILIES.items():
            print(f"{name:12} {what}")
        return 0

    root = Path(args.root).resolve()
    findings = run(root, CI_DIR)

    for f in findings:
        where = f"file={f.locus}," + (f"line={f.line}," if f.line else "") if f.locus else ""
        print(f"::error {where}title={f.code}::{f.message}")

    if not findings:
        config = _repo_config(CI_DIR)
        where = "" if is_canonical(root, config.get("canonical")) else \
            " (fork: the persona-name and Voice rules are the canonical repository's, and were skipped)"
        print(f"✓ {len(FAMILIES)} rule families, no findings.{where}")
        return 0

    print(f"\n{len(findings)} finding(s):\n", file=sys.stderr)
    for f in findings:
        locus = f"{f.locus}:{f.line}" if f.line else (f.locus or "(repository)")
        print(f"  {locus}\n    [{f.code}] {f.message}", file=sys.stderr)
    print("\nCONTRIBUTING.md explains each rule family. Run `python ci/check.py` locally to "
          "reproduce.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
