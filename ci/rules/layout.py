"""Agent-repo layout conformance.

The platform consumes a fixed set of paths from this repository and materializes them back
into the shape every downstream consumer expects. The root must also stay a clean brain
working tree, because a fork inherits its shape and a customer's brain is seeded from it.

Symlinks get their own rule: the platform fetches this repository as a tarball and extracts
it, and a symlink inside the consumed set is the one shape that turns an extraction into a
write outside its target directory.
"""
from __future__ import annotations

from pathlib import Path

from .contracts import Finding

REQUIRED_FILES = (
    (".m8t/brain.yaml", "the brain engine's configuration"),
    ("memory/MEMORY.md", "the memory index the agent reads first"),
    ("skills/_index.md", "the skills index the agent reads first"),
    ("references/_index.md", "the reference catalogue"),
    ("AGENTS.md", "the brain operating doctrine"),
    ("README.md", "the repository's front door"),
    ("LICENSE", "required for a public agent repository"),
)

LIVE_BRAIN_SPACE = ("inbox", "artifacts", "quarantine")
"""Runtime space. Present but empty on the default branch, held by `.gitkeep` — a fork that
inherits a missing directory has a brain the engine cannot write into."""

CONSUMED = ("agent", "memory", "skills", "references", "targets")


def check_layout(root: Path) -> list[Finding]:
    f: list[Finding] = []

    for rel, why in REQUIRED_FILES:
        if not (root / rel).is_file():
            f.append(Finding("layout.missing", f"{rel} is required — {why}", rel))

    for name in LIVE_BRAIN_SPACE:
        d = root / name
        if not d.is_dir():
            f.append(Finding("layout.brain_space.missing",
                             f"{name}/ is required — the engine writes into it", f"{name}/"))
        elif not (d / ".gitkeep").is_file() and not any(d.iterdir()):
            f.append(Finding("layout.brain_space.unheld",
                             f"{name}/ has no .gitkeep, so a clone will not carry it", f"{name}/"))

    for name in CONSUMED:
        d = root / name
        if not d.is_dir():
            continue
        for p in sorted(d.rglob("*")):
            if p.is_symlink():
                f.append(Finding(
                    "layout.symlink",
                    "symlinks are not allowed inside the consumed set — the platform extracts "
                    "this repository from a tarball",
                    str(p.relative_to(root).as_posix())))

    return f
