"""The skill corpus gate — ported from the platform's `brain_eval.seed_gate`.

This gate used to run against this content inside the platform repository. When the
content moved out, the gate kept passing on an empty glob: it looked for
`skills/*/SKILL.md`, found nothing, and reported a clean corpus. That is why an absent or
empty corpus is a HARD finding here rather than a quiet pass.

Two rules from the original are handled elsewhere, deliberately:

* **R5** (linked references exist) is subsumed by `links.py`, which resolves every
  reference convention rather than only `references/*.md` inside a skill body.
* **R6/R8** (scrub, safety) are subsumed by `hygiene.py`, which sweeps the whole repository
  rather than only skills and the references they happen to link.
"""
from __future__ import annotations

import re
from pathlib import Path

from .contracts import Finding
from .frontmatter import parse

_FENCE_RE = re.compile(r"^([ \t]*)(`{3,}|~{3,})[^\n]*\n.*?^[ \t]*\2[^\n]*$", re.M | re.S)
_COMMENT_RE = re.compile(r"<!--.*?-->", re.S)


def _registerable(text: str) -> str:
    """Index and routing text with fenced blocks and HTML comments removed.

    A registration inside a code fence or a comment looks right in the diff and does
    nothing — the reader of an index cannot follow it, and neither can the agent."""
    return _COMMENT_RE.sub("", _FENCE_RE.sub("", text))

REQUIRED_FM = ("type", "title", "created", "updated", "tags", "origin")

# heading text (lowercased) -> finding-code suffix
REQUIRED_SECTIONS = {
    "when to run this": "when_to_run",
    "the discipline": "discipline",
    "never": "never",
}

HANDOFF_REF = "references/advisor-handoff.md"


def check_corpus(root: Path, persona_rel: str = "agent/persona.md") -> list[Finding]:
    skills_dir = root / "skills"
    if not skills_dir.is_dir():
        return [Finding("corpus.missing", "no skills/ directory — this repository carries no brain", "skills/")]

    skill_files = sorted(skills_dir.glob("*/SKILL.md"))
    if not skill_files:
        return [Finding("corpus.empty", "skills/ carries no <slug>/SKILL.md", "skills/")]

    def read(rel: str) -> str:
        p = root / rel
        return p.read_text(encoding="utf-8") if p.is_file() else ""

    skills_index = _registerable(read("skills/_index.md"))
    persona = _registerable(read(persona_rel))
    f: list[Finding] = []

    for skill_md in skill_files:
        name = skill_md.parent.name
        rel = f"skills/{name}/SKILL.md"
        fm, body = parse(skill_md.read_text(encoding="utf-8"))
        low_body = body.lower()

        for key in REQUIRED_FM:
            val = fm.get(key)
            if key == "tags":
                if not isinstance(val, list) or not val:
                    f.append(Finding("corpus.frontmatter.tags", "missing or empty 'tags' list", rel))
            elif not val:
                f.append(Finding(f"corpus.frontmatter.{key}", f"missing required frontmatter '{key}'", rel))

        for section, code in REQUIRED_SECTIONS.items():
            # Anchored to a level-2 heading on its own line. A substring test accepted
            # `### When to run this` and `#### Never`, which the loader does not.
            if not re.search(rf"^## {re.escape(section)}\s*$", low_body, re.M):
                f.append(Finding(f"corpus.section.{code}", f"missing required section '## {section}'", rel))

        if rel not in skills_index:
            f.append(Finding("corpus.unregistered.index", f"{rel} is not listed in skills/_index.md", rel))

        if rel not in persona:
            f.append(Finding("corpus.unregistered.routing",
                             f"{rel} is not referenced in {persona_rel} — the agent will never reach it", rel))

        raw_tags = fm.get("tags")
        tags = [str(t).lower() for t in raw_tags] if isinstance(raw_tags, list) else []
        if "class-b" in tags and HANDOFF_REF not in body:
            f.append(Finding("corpus.class_b.no_handoff",
                             f"a class-b skill must link {HANDOFF_REF}", rel))

    ref_index = read("references/_index.md")
    for ref_md in sorted((root / "references").glob("*.md")):
        if ref_md.name == "_index.md":
            continue
        rel = f"references/{ref_md.name}"
        if rel not in ref_index:
            f.append(Finding("corpus.reference.unindexed",
                             f"{rel} is not listed in references/_index.md, so nothing can browse to it", rel))

    return f
