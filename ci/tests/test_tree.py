"""Which files the rules see.

This is the quietest way for the gate to stop working: a file the sweep never reads
produces no findings, which is indistinguishable from a file that passed.
"""
from __future__ import annotations

from pathlib import Path

from ci.rules.tree import all_files, every_path, markdown_files, text_files


def build(tmp_path: Path, rels: list[str]) -> Path:
    for rel in rels:
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("x\n", encoding="utf-8")
    return tmp_path


def test_the_checker_is_excluded_at_the_root(tmp_path):
    root = build(tmp_path, ["ci/rules/hygiene.py", "README.md"])
    assert all_files(root) == ["README.md"]


# `ci` is an ordinary word. Excluding it at any depth would silently drop a skill about
# continuous integration from every sweep — and a skill is exactly where a real GUID or
# token pasted from a pipeline would end up.
def test_a_directory_named_ci_deeper_in_the_tree_is_still_scanned(tmp_path):
    root = build(tmp_path, ["skills/ci/SKILL.md", "memory/ci/notes.md"])
    assert set(all_files(root)) == {"skills/ci/SKILL.md", "memory/ci/notes.md"}


def test_tool_droppings_are_excluded_at_any_depth(tmp_path):
    root = build(tmp_path, ["__pycache__/x.md", "skills/__pycache__/y.md", "README.md"])
    assert all_files(root) == ["README.md"]


def test_link_resolution_can_see_the_checker_even_though_it_is_not_scanned(tmp_path):
    """`ci/` is excluded from scanning, but content legitimately links to ci/README.md —
    a resolver that cannot see the file would call a correct link broken."""
    root = build(tmp_path, ["ci/README.md", "README.md"])
    assert "ci/README.md" in every_path(root)
    assert "ci/README.md" not in all_files(root)


def test_configuration_and_data_files_are_swept(tmp_path):
    root = build(tmp_path, [".m8t/brain.yaml", ".github/workflows/pr.yml", "ci/repo.json", "LICENSE"])
    swept = set(text_files(root))
    assert {".m8t/brain.yaml", ".github/workflows/pr.yml", "LICENSE"} <= swept
    assert "ci/repo.json" not in swept


def test_markdown_listing_is_markdown_only(tmp_path):
    root = build(tmp_path, ["a.md", "b.yml", "LICENSE"])
    assert markdown_files(root) == ["a.md"]
