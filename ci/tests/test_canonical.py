"""Forks keep the checks that are about brain content, and lose the two that are ours.

Forking is the advertised way to get your own Ezra, and GitHub copies every file — there is
no way to exclude one. So the question is not *whether* a fork inherits these checks, only
whether they help or punish the personalisation the README invites.
"""
from __future__ import annotations

from pathlib import Path

from ci.rules.canonical import current_repo, is_canonical
from ci.rules.persona import check_persona

CANONICAL = "m8t-labs/ezra"
VOICE = "You are a calm engineer. Short sentences."

PERSONA = """---
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
"""


def build(tmp_path: Path, text: str) -> Path:
    (tmp_path / "agent").mkdir(parents=True, exist_ok=True)
    (tmp_path / "agent" / "persona.md").write_text(text, encoding="utf-8")
    return tmp_path


def codes(tmp_path: Path, text: str, canonical: bool) -> set[str]:
    return {f.code for f in check_persona(build(tmp_path, text), "ezra", VOICE, canonical)}


# ── identifying where we are ───────────────────────────────────────────────────
def test_the_actions_environment_names_the_repository(monkeypatch, tmp_path):
    monkeypatch.setenv("GITHUB_REPOSITORY", "someone-else/ezra")
    assert current_repo(tmp_path) == "someone-else/ezra"
    assert is_canonical(tmp_path, CANONICAL) is False


def test_the_canonical_repository_is_recognised(monkeypatch, tmp_path):
    monkeypatch.setenv("GITHUB_REPOSITORY", CANONICAL)
    assert is_canonical(tmp_path, CANONICAL) is True


def test_the_comparison_ignores_case(monkeypatch, tmp_path):
    monkeypatch.setenv("GITHUB_REPOSITORY", "M8T-Labs/Ezra")
    assert is_canonical(tmp_path, CANONICAL) is True


def test_an_unknown_location_is_treated_as_canonical(monkeypatch, tmp_path):
    """Guessing 'fork' wrongly would silently switch off two real guards on the repository
    that needs them. Guessing 'canonical' wrongly produces one clearly-worded finding."""
    monkeypatch.delenv("GITHUB_REPOSITORY", raising=False)
    assert is_canonical(tmp_path, CANONICAL) is True   # tmp_path has no git remote


def test_no_declared_canonical_means_every_rule_applies(tmp_path):
    assert is_canonical(tmp_path, None) is True


# ── what a fork keeps, and what it loses ───────────────────────────────────────
def test_a_fork_may_rename_the_agent(tmp_path):
    renamed = PERSONA.replace("name: ezra", "name: atlas")
    assert codes(tmp_path, renamed, canonical=False) == set()
    assert "persona.name.mismatch" in codes(tmp_path, renamed, canonical=True)


def test_a_fork_may_rewrite_the_voice(tmp_path):
    revoiced = PERSONA.replace("calm engineer", "cheerful assistant")
    assert codes(tmp_path, revoiced, canonical=False) == set()
    assert "persona.voice.drift" in codes(tmp_path, revoiced, canonical=True)


def test_a_fork_doing_both_is_still_green(tmp_path):
    """The exact thing the README invites: 'your fork becomes your Ezra's brain'."""
    mine = PERSONA.replace("name: ezra", "name: atlas").replace("calm engineer", "blunt engineer")
    assert codes(tmp_path, mine, canonical=False) == set()


# Everything that is about the agent WORKING rather than about being ours still applies.
def test_a_fork_still_needs_a_version(tmp_path):
    assert "persona.field.version" in codes(tmp_path, PERSONA.replace("version: 0.4\n", ""), canonical=False)


def test_a_fork_still_needs_the_decision_policy_block(tmp_path):
    stripped = PERSONA.replace("<!-- m8t:decision-policy:end -->\n", "")
    assert "persona.decision_policy.markers" in codes(tmp_path, stripped, canonical=False)


def test_a_fork_still_needs_a_voice_section_at_all(tmp_path):
    gone = PERSONA.replace("## Voice\n\nYou are a calm engineer. Short sentences.\n\n", "")
    assert "persona.voice.missing" in codes(tmp_path, gone, canonical=False)


def test_a_fork_still_needs_a_coherent_target(tmp_path):
    bad = PERSONA.replace("default-target: foundry", "default-target: openai")
    assert "persona.target.unknown" in codes(tmp_path, bad, canonical=False)
