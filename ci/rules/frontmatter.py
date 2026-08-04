"""YAML frontmatter split.

Ported from the platform's `brain_eval.collector._parse` so the two agree on what
counts as frontmatter. A document with no frontmatter is not an error here — the rule
that cares reports the missing keys itself.
"""
from __future__ import annotations

import re

import yaml

_FM = re.compile(r"^---\n(.*?)\n---\n?(.*)$", re.S)

PARSE_ERROR = "__parse_error__"


def parse(text: str) -> tuple[dict, str]:
    """Return (frontmatter, body). Malformed YAML yields `{PARSE_ERROR: True}` rather
    than raising, so one bad file produces one finding instead of a crashed run."""
    m = _FM.match(text)
    if not m:
        return {}, text
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        fm = {PARSE_ERROR: True}
    return (fm if isinstance(fm, dict) else {PARSE_ERROR: True}), m.group(2)
