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

EXCLUDED_ROOTS = frozenset({"ci"})
"""Excluded only at the repository root. `ci` is a real word — a skill about continuous
integration would live at `skills/ci/SKILL.md`, and excluding it at any depth would silently
drop that file from every sweep."""

EXCLUDED_ANYWHERE = frozenset({".git", ".pytest_cache", "__pycache__", ".venv"})
"""Tool droppings, which can appear at any depth and are never content."""

DOCS_ROOTS = frozenset({"guides"})
"""Product runbooks: prose a founder pastes into a coding agent.

The BYOC install runbook lives here because the platform's source is private and the
runbook has to stay anonymously readable. It is not BRAIN content — the platform does not
consume it, and it is outside the content digest — but it is emphatically content an
agent ACTS ON: the README hands it to a coding agent holding the founder's cloud
credentials, and `rules/runbook.py` guards the step in it that opens a browser.

That distinction decides which rules apply, one at a time rather than as a bloc:

* the **reference resolver** skips its INCIDENTAL references only — a backticked
  `installer/entrypoint.sh` is a real file in another repository. Its `[text](target)`
  links stay checked, because those are the founder's navigation between runbooks;
* the **destructive-command** rule stands down: `rm -rf ~/.m8t` is what an uninstall
  guide correctly says, and a prereqs guide correctly pipes Microsoft's installer to a
  shell;
* the **prompt-injection** rule stays ARMED, and is armed here BECAUSE of this folder.
  Nothing legitimate in an install runbook looks like an injection string, and this is
  the repository's softest target: public, contributor-editable, carried by no digest,
  and read by an agent that can act on it;
* everything else — secrets, mailboxes, named entities, GUIDs, internal strings — applies
  unchanged. The two values that legitimately look like leaks are allowlisted one at a
  time in `rules/hygiene.py`, not excused folder-wide.

Named BY NAME, at the root only. A prefix or a wildcard would let a future folder inherit
this treatment silently, which is how an exemption outlives the reason it was granted."""


def is_docs(rel: str) -> bool:
    """True when this file is a product runbook rather than brain content."""
    return rel.split("/")[0] in DOCS_ROOTS

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


def _included(rel: str) -> bool:
    parts = rel.split("/")
    return parts[0] not in EXCLUDED_ROOTS and not EXCLUDED_ANYWHERE.intersection(parts[:-1])


def every_path(root: Path) -> list[str]:
    """Everything in the repository except tool droppings — INCLUDING `ci/`.

    Link resolution needs this: `ci/` is not scanned, but content legitimately links to
    `ci/README.md`, and a link checker that cannot see a file reports it as broken."""
    paths = _tracked(root)
    if paths is None:
        paths = _walked(root)
    return sorted(p for p in paths if not EXCLUDED_ANYWHERE.intersection(p.split("/")))


def all_files(root: Path) -> list[str]:
    """Every candidate path the rules SCAN, repo-relative, POSIX separators."""
    return [p for p in every_path(root) if _included(p)]


def _is_text(rel: str) -> bool:
    return rel.split("/")[-1] in EXTENSIONLESS or rel.endswith(TEXT)


def text_files(root: Path) -> list[str]:
    """Files the hygiene sweep reads."""
    return [p for p in all_files(root) if _is_text(p)]


def markdown_files(root: Path) -> list[str]:
    """Files the reference resolver reads."""
    return [p for p in all_files(root) if p.endswith(MARKDOWN)]
