from __future__ import annotations

from pathlib import Path

from ci.rules.persona import check_persona

VOICE = "You are a calm engineer. Short sentences."

GOOD = """---
name: ezra
role: Azure Expert
description: Azure architecture and cost triage.
version: 0.4
allowed-targets: [foundry]
default-target: foundry
---

# Azure Expert

## Voice

You are a calm engineer. Short sentences.

## Live UI tools

<!-- m8t:decision-policy:start -->
Answer the question.
<!-- m8t:decision-policy:end -->

## Your brain

Read `memory/MEMORY.md`.
"""


def build(tmp_path: Path, text: str) -> Path:
    (tmp_path / "agent").mkdir(parents=True, exist_ok=True)
    (tmp_path / "agent" / "persona.md").write_text(text, encoding="utf-8")
    return tmp_path


def codes(tmp_path: Path, text: str, persona: str = "ezra", voice: str = VOICE) -> set[str]:
    return {f.code for f in check_persona(build(tmp_path, text), persona, voice)}


def test_the_good_persona_passes(tmp_path):
    assert codes(tmp_path, GOOD) == set()


def test_a_missing_persona_is_refused(tmp_path):
    assert {f.code for f in check_persona(tmp_path, "ezra", VOICE)} == {"persona.missing"}


def test_name_must_match_the_declared_persona(tmp_path):
    assert "persona.name.mismatch" in codes(tmp_path, GOOD.replace("name: ezra", "name: azzy"))


def test_missing_version_is_refused(tmp_path):
    assert "persona.field.version" in codes(tmp_path, GOOD.replace("version: 0.4\n", ""))


def test_malformed_version_is_refused(tmp_path):
    assert "persona.version.malformed" in codes(tmp_path, GOOD.replace("version: 0.4", "version: draft"))


# The version rule is deliberately NOT pinned to a literal: a guard that fails every
# legitimate bump is one people learn to delete. Bumping must stay green.
def test_bumping_the_version_stays_green(tmp_path):
    assert codes(tmp_path, GOOD.replace("version: 0.4", "version: 1.0")) == set()


def test_missing_role_is_refused(tmp_path):
    assert "persona.field.role" in codes(tmp_path, GOOD.replace("role: Azure Expert\n", ""))


def test_default_target_outside_allowed_targets_is_refused(tmp_path):
    assert "persona.target.unknown" in codes(tmp_path, GOOD.replace("default-target: foundry", "default-target: openai"))


def test_deleting_the_decision_policy_block_is_refused(tmp_path):
    stripped = GOOD.replace("<!-- m8t:decision-policy:start -->\nAnswer the question.\n<!-- m8t:decision-policy:end -->\n", "")
    assert "persona.decision_policy.markers" in codes(tmp_path, stripped)


def test_an_unbalanced_decision_policy_block_is_refused(tmp_path):
    assert "persona.decision_policy.markers" in codes(
        tmp_path, GOOD.replace("<!-- m8t:decision-policy:end -->\n", ""))


def test_a_duplicated_decision_policy_block_is_refused(tmp_path):
    doubled = GOOD.replace("<!-- m8t:decision-policy:end -->",
                           "<!-- m8t:decision-policy:end -->\n<!-- m8t:decision-policy:start -->\nx\n<!-- m8t:decision-policy:end -->")
    assert "persona.decision_policy.markers" in codes(tmp_path, doubled)


def test_changing_one_word_of_the_voice_is_refused(tmp_path):
    assert "persona.voice.drift" in codes(tmp_path, GOOD.replace("calm engineer", "loud engineer"))


def test_deleting_the_voice_section_is_refused(tmp_path):
    gone = GOOD.replace("## Voice\n\nYou are a calm engineer. Short sentences.\n\n", "")
    assert "persona.voice.missing" in codes(tmp_path, gone)


def test_voice_trailing_whitespace_does_not_drift(tmp_path):
    """The golden is compared on stripped text, so an editor adding a trailing newline is
    not a character change and must not fail a contributor's pull request."""
    assert codes(tmp_path, GOOD.replace("Short sentences.\n", "Short sentences.\n\n\n")) == set()


def test_unparseable_frontmatter_is_refused(tmp_path):
    assert "persona.frontmatter.invalid" in codes(tmp_path, "---\nname: [unclosed\n---\n\nbody\n")
