"""The one shape every rule returns.

Every finding this checker produces is hard: it is a gate, not an advisor. A rule that
wants to say "this is probably fine" should not be a rule.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Finding:
    code: str
    """Dotted rule identifier, e.g. `corpus.frontmatter.tags`. Stable — it is what a
    contributor searches for and what CONTRIBUTING.md names."""

    message: str
    """One line, addressed to whoever opened the pull request."""

    locus: str = ""
    """Repo-relative path the finding is about. Empty for repo-wide findings."""

    line: int = 0
    """1-indexed line, when the rule can name one. 0 means "no specific line"."""
