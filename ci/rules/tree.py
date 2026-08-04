"""Which files the checker looks at.

In a git checkout the answer is "what git tracks" — that is what a pull request can
actually change. Outside one (the rule tests build fixture trees in a temp directory) it
falls back to a walk, and the two must agree on exclusions.

`.github/` and `.m8t/` ARE content: issue templates are the repo's public front door and
`brain.yaml` is read by the engine. Only `ci/` is excluded, because a checker's own
fixtures necessarily contain the strings it hunts for — the hygiene rules would match
their own source and the gate would be permanently red.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

EXCLUDED_DIRS = frozenset({"ci", ".git", ".pytest_cache", "__pycache__", ".venv"})

MARKDOWN = (".md",)
TEXT = (".md", ".yml", ".yaml", ".json", ".txt")
EXTENSIONLESS = frozenset({"LICENSE", "NOTICE", "CODEOWNERS"})


def _tracked(root: Path) -> list[str] | None:
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "ls-files", "-z"],
            capture_output=True, text=True, check=True,
        ).stdout
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return None
    return [p for p in out.split("\0") if p]


def _walked(root: Path) -> list[str]:
    return sorted(str(p.relative_to(root).as_posix()) for p in root.rglob("*") if p.is_file())


def all_files(root: Path) -> list[str]:
    """Every candidate path, repo-relative, POSIX separators, `ci/` excluded."""
    paths = _tracked(root)
    if paths is None:
        paths = _walked(root)
    return sorted(p for p in paths if not EXCLUDED_DIRS.intersection(p.split("/")[:-1] or [""])
                  and p.split("/")[0] not in EXCLUDED_DIRS)


def _is_text(rel: str) -> bool:
    return rel.split("/")[-1] in EXTENSIONLESS or rel.endswith(TEXT)


def text_files(root: Path) -> list[str]:
    """Files the hygiene sweep reads."""
    return [p for p in all_files(root) if _is_text(p)]


def markdown_files(root: Path) -> list[str]:
    """Files the reference resolver reads."""
    return [p for p in all_files(root) if p.endswith(MARKDOWN)]
