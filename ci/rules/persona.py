"""The agent definition's contract.

`agent/persona.md` is the single most contributable file in this repository and the one
the platform deploys. These rules are what the platform's own test suite used to assert
before the content moved out of it.

On the version rule: it checks that a version is DECLARED and well-formed, not that it
equals a particular number. Pinning a literal here would fail every legitimate bump of the
persona — a guard that is red on correct work is one people learn to delete.
"""
from __future__ import annotations

import re
from pathlib import Path

from .contracts import Finding
from .frontmatter import PARSE_ERROR, parse

PERSONA_PATH = "agent/persona.md"
REQUIRED_FIELDS = ("name", "role", "description", "version")
_VERSION_RE = re.compile(r"^\d+\.\d+$")
_POLICY_START = "<!-- m8t:decision-policy:start -->"
_POLICY_END = "<!-- m8t:decision-policy:end -->"


def voice_section(body: str) -> str | None:
    """The `## Voice` section's text, or None when there is no such section."""
    m = re.search(r"^## Voice\s*\n(.*?)(?=^## |\Z)", body, re.M | re.S)
    return m.group(1).strip() if m else None


def check_persona(root: Path, expected_persona: str, voice_golden: str) -> list[Finding]:
    path = root / PERSONA_PATH
    if not path.is_file():
        return [Finding("persona.missing", f"{PERSONA_PATH} is required — this is an agent repository",
                        PERSONA_PATH)]

    text = path.read_text(encoding="utf-8")
    fm, body = parse(text)
    if fm.get(PARSE_ERROR):
        return [Finding("persona.frontmatter.invalid", "the YAML frontmatter does not parse", PERSONA_PATH)]
    if not fm:
        return [Finding("persona.frontmatter.missing", "no YAML frontmatter found", PERSONA_PATH)]

    f: list[Finding] = []
    for key in REQUIRED_FIELDS:
        if not str(fm.get(key) or "").strip():
            f.append(Finding(f"persona.field.{key}", f"frontmatter is missing '{key}'", PERSONA_PATH))

    name = str(fm.get("name") or "").strip()
    if name and name != expected_persona:
        f.append(Finding(
            "persona.name.mismatch",
            f"declares name '{name}' but ci/repo.json expects '{expected_persona}'. "
            "The platform pins this repository to a persona slug; renaming here breaks that link.",
            PERSONA_PATH))

    version = str(fm.get("version") or "").strip()
    if version and not _VERSION_RE.match(version):
        f.append(Finding("persona.version.malformed",
                         f"version '{version}' is not MAJOR.MINOR", PERSONA_PATH))

    allowed = fm.get("allowed-targets")
    default = str(fm.get("default-target") or "").strip()
    if isinstance(allowed, list) and default and default not in [str(x) for x in allowed]:
        f.append(Finding("persona.target.unknown",
                         f"default-target '{default}' is not in allowed-targets", PERSONA_PATH))

    starts, ends = text.count(_POLICY_START), text.count(_POLICY_END)
    if starts != 1 or ends != 1:
        f.append(Finding(
            "persona.decision_policy.markers",
            "the m8t:decision-policy block must appear exactly once, with both markers. "
            "It governs the present_decision tool the deployed agent holds.",
            PERSONA_PATH))

    voice = voice_section(body)
    if voice is None:
        f.append(Finding("persona.voice.missing", "no '## Voice' section", PERSONA_PATH))
    elif voice != voice_golden.strip():
        f.append(Finding(
            "persona.voice.drift",
            "the Voice section differs from ci/golden/voice.md. Voice is the agent's "
            "character — if the change is intended, update the golden in this same pull "
            "request so the diff shows what changed.",
            PERSONA_PATH))

    return f
