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


def _check_foundry_tools(fm: dict) -> list[Finding]:
    """`targets.foundry.tools` is the agent's declared toolset.

    The platform forwards this block to the model host VERBATIM: whatever is written
    here is what the deployed agent gets. That makes a malformed entry expensive in a
    way most frontmatter mistakes are not — it ships, rather than failing a parse.

    These rules exist because the equivalent assertions used to live in the platform's
    own test suite, alongside a copy of the tool definitions. That copy was removed
    when this file became their only author, and removing a second author should not
    also remove the check.

    Deliberately narrow: it validates SHAPE, never wording and never which tools an
    agent ought to have. A rule that pinned the toolset would be red on every
    legitimate addition, and this repository takes contributions.
    """
    targets = fm.get("targets")
    foundry = targets.get("foundry") if isinstance(targets, dict) else None
    if not isinstance(foundry, dict) or "tools" not in foundry:
        return []

    tools = foundry["tools"]
    if not isinstance(tools, list):
        return [Finding("persona.tools.not_a_list",
                        "targets.foundry.tools must be a list of tool objects", PERSONA_PATH)]

    f: list[Finding] = []
    seen: set[str] = set()
    for i, tool in enumerate(tools):
        where = f"targets.foundry.tools[{i}]"
        # A list of NAMES is the shape a contributor reaches for first. It parses,
        # it forwards, and nothing downstream can match it to a deployed tool.
        if not isinstance(tool, dict):
            f.append(Finding("persona.tools.entry_not_a_mapping",
                             f"{where} is not a tool object — each entry needs at least `- type: <type>`",
                             PERSONA_PATH))
            continue
        kind = tool.get("type")
        if not isinstance(kind, str) or not kind.strip():
            f.append(Finding("persona.tools.type_missing",
                             f"{where} has no string 'type'", PERSONA_PATH))
            continue

        if kind == "function":
            name = tool.get("name")
            if not isinstance(name, str) or not name.strip():
                f.append(Finding("persona.tools.function_name_missing",
                                 f"{where} is a function tool with no 'name'", PERSONA_PATH))
            else:
                if name in seen:
                    f.append(Finding("persona.tools.duplicate",
                                     f"{where} declares '{name}' a second time", PERSONA_PATH))
                seen.add(name)

        description = tool.get("description")
        # What matters is the VALUE, not the source style. A folded (`>`) scalar
        # collapses to one line and is fine; a literal (`|`) one keeps the newlines,
        # so the agent receives different bytes than a single-line description and is
        # then permanently "stale" against a persona that looks correct.
        if isinstance(description, str) and "\n" in description.strip():
            f.append(Finding("persona.tools.description_multiline",
                             f"{where}'s description contains newlines — the platform sends it "
                             "verbatim, so keep it a single line (a literal `|` block embeds them)",
                             PERSONA_PATH))

        f += _check_schema_numbers(tool.get("parameters"), where)
    return f


_NUMERIC_KEYS = ("maxLength", "minLength", "minItems", "maxItems", "minimum", "maximum")


def _check_schema_numbers(node: object, where: str) -> list[Finding]:
    """Quoting a bound turns it into a string the host will not enforce."""
    f: list[Finding] = []
    if isinstance(node, dict):
        for key, value in node.items():
            if key in _NUMERIC_KEYS and not isinstance(value, (int, float)):
                f.append(Finding("persona.tools.schema_not_numeric",
                                 f"{where}: '{key}' must be a number, got {type(value).__name__}",
                                 PERSONA_PATH))
            f += _check_schema_numbers(value, where)
    elif isinstance(node, list):
        for item in node:
            f += _check_schema_numbers(item, where)
    return f


def voice_section(body: str) -> str | None:
    """The `## Voice` section's text, or None when there is no such section."""
    m = re.search(r"^## Voice\s*\n(.*?)(?=^## |\Z)", body, re.M | re.S)
    return m.group(1).strip() if m else None


def check_persona(root: Path, expected_persona: str, voice_golden: str,
                  canonical: bool = True) -> list[Finding]:
    """`canonical` is False in a fork. Two rules below are switched off there — see
    `canonical.py` for why the other rules are not."""
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
    if canonical and name and name != expected_persona:
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

    f += _check_foundry_tools(fm)

    voice = voice_section(body)
    if voice is None:
        f.append(Finding("persona.voice.missing", "no '## Voice' section", PERSONA_PATH))
    elif canonical and voice != voice_golden.strip():
        f.append(Finding(
            "persona.voice.drift",
            "the Voice section differs from ci/golden/voice.md. Voice is the agent's "
            "character — if the change is intended, update the golden in this same pull "
            "request so the diff shows what changed.",
            PERSONA_PATH))

    return f
