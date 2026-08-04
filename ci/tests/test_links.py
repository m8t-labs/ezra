"""Internal references must resolve.

The conventions checked here were ENUMERATED from the live corpus, not assumed. At the
time this was written the counts were: backticked path 150, inline markdown link 20, bare
path in prose 20. The backtick form is the dominant one and nothing had ever checked it.
"""
from __future__ import annotations

from pathlib import Path

from ci.rules.links import check_links


def build(tmp_path: Path, files: dict[str, str]) -> Path:
    for rel, text in files.items():
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    return tmp_path


def codes(root: Path) -> set[str]:
    return {f.code for f in check_links(root)}


def targets(root: Path) -> set[str]:
    return {f.message.split("`")[1] for f in check_links(root)}


# ── the three conventions ──────────────────────────────────────────────────────
def test_broken_backtick_path_is_caught(tmp_path):
    root = build(tmp_path, {"a.md": "read `memory/gone.md` first\n"})
    assert codes(root) == {"links.unresolved"}
    assert targets(root) == {"memory/gone.md"}


def test_broken_inline_link_is_caught(tmp_path):
    root = build(tmp_path, {"a.md": "read [it](skills/gone/SKILL.md)\n"})
    assert targets(root) == {"skills/gone/SKILL.md"}


def test_broken_bare_path_in_prose_is_caught(tmp_path):
    root = build(tmp_path, {"a.md": "the answer is in references/gone.md today\n"})
    assert targets(root) == {"references/gone.md"}


def test_a_skills_broken_reference_link_is_caught(tmp_path):
    """The rule the ported corpus gate used to own (its R5), now covered here for every
    convention rather than only for `references/` inside a skill body."""
    root = build(tmp_path, {"skills/x/SKILL.md": "see references/nope.md\n"})
    assert targets(root) == {"references/nope.md"}


# ── what resolves ──────────────────────────────────────────────────────────────
def test_existing_target_is_clean(tmp_path):
    root = build(tmp_path, {"a.md": "read `memory/here.md`\n", "memory/here.md": "x\n"})
    assert check_links(root) == []


def test_directory_target_is_clean(tmp_path):
    root = build(tmp_path, {"a.md": "browse [refs](references/)\n", "references/x.md": "x\n"})
    assert check_links(root) == []


def test_target_relative_to_the_referring_file_is_clean(tmp_path):
    root = build(tmp_path, {"skills/x/SKILL.md": "see [y](../y/SKILL.md)\n", "skills/y/SKILL.md": "y\n"})
    assert check_links(root) == []


# ── what is deliberately not resolved ──────────────────────────────────────────
def test_external_urls_are_skipped(tmp_path):
    root = build(tmp_path, {"a.md": "[m8t](https://github.com/m8t-labs/m8t) and <mailto:a@example.com>\n"})
    assert check_links(root) == []


def test_pure_anchors_are_skipped(tmp_path):
    root = build(tmp_path, {"a.md": "[top](#heading)\n"})
    assert check_links(root) == []


def test_bare_basenames_are_skipped(tmp_path):
    """`MEMORY.md`, `_index.md`, `SKILL.md` appear in AGENTS.md as generic doctrine — the
    folder model, not a path. A rule that resolved them would be wrong 150 times."""
    root = build(tmp_path, {"a.md": "each folder carries an `_index.md`; see `MEMORY.md` and `SKILL.md`\n"})
    assert check_links(root) == []


def test_live_brain_space_targets_are_skipped(tmp_path):
    """`artifacts/`, `inbox/` and `quarantine/` are runtime space — `.gitkeep` only on the
    default branch by contract — so their contents cannot be resolved at PR time. The live
    persona cites `artifacts/azure/YYYY-MM-DD-create-storage-proof.md` as an example path."""
    root = build(tmp_path, {
        "a.md": "proof lands in `artifacts/azure/YYYY-MM-DD-create-storage-proof.md`\n"
                "scratch goes to `inbox/2026-08-04/note.md`\n"
                "suspect content sits in `quarantine/thing.md`\n",
    })
    assert check_links(root) == []


def test_code_fences_are_not_scanned(tmp_path):
    root = build(tmp_path, {"a.md": "```\ncp memory/nowhere.md .\n```\n"})
    assert check_links(root) == []


def test_the_checker_itself_is_not_scanned(tmp_path):
    """`ci/` holds the fixtures for these very rules, so scanning it would be permanently
    red. Uses a markdown file, which the resolver would otherwise read."""
    root = build(tmp_path, {"ci/tests/fixture.md": "see `memory/nope.md`\n"})
    assert check_links(root) == []


def test_github_templates_are_scanned(tmp_path):
    """Issue and PR templates are the repo's public front door — their links must resolve."""
    root = build(tmp_path, {".github/PULL_REQUEST_TEMPLATE.md": "read `docs/gone.md`\n"})
    assert targets(root) == {"docs/gone.md"}


def test_anchor_on_a_real_file_is_clean(tmp_path):
    root = build(tmp_path, {"a.md": "[x](memory/here.md#section)\n", "memory/here.md": "x\n"})
    assert check_links(root) == []
