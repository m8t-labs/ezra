from __future__ import annotations

import textwrap
from pathlib import Path

from ci.rules.corpus import check_corpus

VALID_SKILL = textwrap.dedent("""\
    ---
    type: skill
    title: "Demo skill"
    created: 2026-06-22T00:00:00Z
    updated: 2026-06-22T00:00:00Z
    tags: [demo]
    origin: operator
    ---

    # Demo skill

    ## When to run this
    When demoing the gate.

    ## The discipline
    1. Do the thing.

    ## Never
    - Never break.
    """)


def build(tmp_path: Path, skills: dict[str, str], *, index=None, persona=None, refs=None) -> Path:
    seed = tmp_path
    (seed / "skills").mkdir(parents=True, exist_ok=True)
    (seed / "references").mkdir(parents=True, exist_ok=True)
    (seed / "agent").mkdir(parents=True, exist_ok=True)
    for name, text in skills.items():
        d = seed / "skills" / name
        d.mkdir(exist_ok=True)
        (d / "SKILL.md").write_text(text, encoding="utf-8")
    if index is None:
        index = "# Skills\n" + "\n".join(f"- `skills/{n}/SKILL.md` — {n}" for n in skills)
    (seed / "skills" / "_index.md").write_text(index, encoding="utf-8")
    for rn, rt in (refs or {}).items():
        (seed / "references" / rn).write_text(rt, encoding="utf-8")
    ref_index = "# References\n" + "\n".join(f"- `references/{n}`" for n in (refs or {}))
    (seed / "references" / "_index.md").write_text(ref_index, encoding="utf-8")
    if persona is None:
        persona = "# Persona\n" + "\n".join(f"| x | `skills/{n}/SKILL.md` |" for n in skills)
    (seed / "agent" / "persona.md").write_text(persona, encoding="utf-8")
    return seed


def codes(root: Path) -> set[str]:
    return {f.code for f in check_corpus(root)}


# ── the failure that made this gate necessary ──────────────────────────────────
# In the platform repository this gate globbed skills/*/SKILL.md. When the content moved
# out, the glob matched nothing and the gate reported a clean corpus — a PASS on a
# directory that no longer existed. Absence must be loud.
def test_a_missing_corpus_is_refused(tmp_path):
    assert codes(tmp_path) == {"corpus.missing"}


def test_an_empty_corpus_is_refused(tmp_path):
    (tmp_path / "skills").mkdir()
    assert codes(tmp_path) == {"corpus.empty"}


def test_a_valid_corpus_passes(tmp_path):
    assert codes(build(tmp_path, {"demo": VALID_SKILL})) == set()


# ── one malformed fixture per rule ─────────────────────────────────────────────
def test_missing_origin_frontmatter_is_refused(tmp_path):
    broken = VALID_SKILL.replace("origin: operator\n", "")
    assert "corpus.frontmatter.origin" in codes(build(tmp_path, {"demo": broken}))


def test_empty_tags_list_is_refused(tmp_path):
    broken = VALID_SKILL.replace("tags: [demo]", "tags: []")
    assert "corpus.frontmatter.tags" in codes(build(tmp_path, {"demo": broken}))


def test_missing_never_section_is_refused(tmp_path):
    broken = VALID_SKILL.replace("## Never\n- Never break.\n", "")
    assert "corpus.section.never" in codes(build(tmp_path, {"demo": broken}))


def test_missing_when_to_run_section_is_refused(tmp_path):
    broken = VALID_SKILL.replace("## When to run this", "## Sometimes")
    assert "corpus.section.when_to_run" in codes(build(tmp_path, {"demo": broken}))


def test_missing_discipline_section_is_refused(tmp_path):
    broken = VALID_SKILL.replace("## The discipline", "## Steps")
    assert "corpus.section.discipline" in codes(build(tmp_path, {"demo": broken}))


# The required sections are level-2 headings. A substring test accepted any depth, so
# `### Never` looked registered and the loader disagreed.
def test_a_required_section_at_the_wrong_heading_level_is_refused(tmp_path):
    broken = VALID_SKILL.replace("## Never", "#### Never")
    assert "corpus.section.never" in codes(build(tmp_path, {"demo": broken}))


def test_a_required_section_mentioned_in_prose_does_not_count(tmp_path):
    broken = VALID_SKILL.replace("## When to run this", "Read the '## When to run this' part")
    assert "corpus.section.when_to_run" in codes(build(tmp_path, {"demo": broken}))


# A registration inside a fenced block or an HTML comment looks right in the diff and is
# unreachable for both a reader and the agent.
def test_a_registration_inside_a_code_fence_does_not_count(tmp_path):
    fenced = "# Skills\n\n```\n- `skills/demo/SKILL.md`\n```\n"
    assert "corpus.unregistered.index" in codes(build(tmp_path, {"demo": VALID_SKILL}, index=fenced))


def test_a_routing_entry_inside_an_html_comment_does_not_count(tmp_path):
    hidden = "# Persona\n<!-- | x | `skills/demo/SKILL.md` | -->\n"
    assert "corpus.unregistered.routing" in codes(build(tmp_path, {"demo": VALID_SKILL}, persona=hidden))


def test_a_skill_absent_from_the_index_is_refused(tmp_path):
    root = build(tmp_path, {"demo": VALID_SKILL}, index="# Skills\n(nothing)")
    assert "corpus.unregistered.index" in codes(root)


def test_a_skill_the_persona_never_routes_to_is_refused(tmp_path):
    root = build(tmp_path, {"demo": VALID_SKILL}, persona="# Persona\nno routing table")
    assert "corpus.unregistered.routing" in codes(root)


def test_a_class_b_skill_without_the_handoff_is_refused(tmp_path):
    b = VALID_SKILL.replace("tags: [demo]", "tags: [demo, class-b]")
    assert "corpus.class_b.no_handoff" in codes(build(tmp_path, {"demo": b}))


def test_a_class_b_skill_linking_the_handoff_passes(tmp_path):
    b = VALID_SKILL.replace("tags: [demo]", "tags: [demo, class-b]").replace(
        "- Never break.", "- Never break. See references/advisor-handoff.md")
    root = build(tmp_path, {"demo": b}, refs={"advisor-handoff.md": "x"})
    assert "corpus.class_b.no_handoff" not in codes(root)


def test_an_unindexed_reference_is_refused(tmp_path):
    root = build(tmp_path, {"demo": VALID_SKILL}, refs={"orphan.md": "x"})
    (root / "references" / "_index.md").write_text("# References\n(nothing)", encoding="utf-8")
    assert "corpus.reference.unindexed" in codes(root)
