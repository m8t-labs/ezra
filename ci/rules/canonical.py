"""Am I the canonical repository, or a fork?

Forking this repository is the advertised way to get your own Ezra, and a fork inherits
every file — GitHub has no way to exclude one. Two of these rules only make sense here:

* the persona **name** must match what the platform's pin expects, and
* the **Voice** must match the golden.

In a fork, both are wrong: the README invites you to make Ezra yours, and a guard that goes
red the moment you accept that invitation is a guard you will delete. Everything else —
layout, corpus, wire contracts, links, hygiene — is about brain content and is just as true
in your copy as in ours, so a fork keeps all of it.

**When the answer is unknown, we assume canonical.** Getting it wrong that way produces one
clearly-worded finding; getting it wrong the other way would silently switch off two real
guards on the repository that actually needs them.
"""
from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

_REMOTE_RE = re.compile(r"(?:github\.com[:/])([^/]+/[^/]+?)(?:\.git)?/?$")


def current_repo(root: Path) -> str | None:
    """`owner/name` for this checkout, or None when it cannot be determined."""
    env = os.environ.get("GITHUB_REPOSITORY", "").strip()
    if env:
        return env
    try:
        url = subprocess.run(
            ["git", "-C", str(root), "remote", "get-url", "origin"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return None
    m = _REMOTE_RE.search(url)
    return m.group(1) if m else None


def is_canonical(root: Path, canonical: str | None) -> bool:
    """True unless we can positively identify this checkout as somewhere else."""
    if not canonical:
        return True
    here = current_repo(root)
    return here is None or here.lower() == canonical.lower()
