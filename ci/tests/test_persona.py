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


# ── targets.foundry.tools ──────────────────────────────────────────────────────
# The platform forwards this block VERBATIM to the model host, so a malformed entry
# ships rather than failing a parse. Every rule below has its own breaker: a rule
# that cannot be made to fail is not a gate.

WITH_TOOLS = GOOD.replace(
    "default-target: foundry\n",
    """default-target: foundry
targets:
  foundry:
    kind: prompt
    model: gpt-5.4
    tools:
      - type: web_search_preview
      - type: function
        name: present_decision
        description: "Render a card the user answers by picking one of 2-4 options."
        parameters:
          type: object
          properties:
            title: { type: string, maxLength: 120 }
          required: [title]
          additionalProperties: false
""",
)


def test_a_well_formed_tools_block_is_accepted(tmp_path):
    assert codes(tmp_path, WITH_TOOLS) == set()


def test_a_persona_declaring_no_tools_is_accepted(tmp_path):
    """Not every agent declares tools, and this rule never says which it ought to have."""
    assert codes(tmp_path, GOOD) == set()


WITH_INSTALL_OFFER = WITH_TOOLS.replace(
    "      - type: web_search_preview\n",
    "      - type: web_search_preview\n"
    "      - type: function\n"
    "        name: present_install_offer\n"
    "        description: Contextual offer.\n"
    "        parameters: { type: object }\n",
).replace(
    "## Your brain\n",
    "<!-- m8t:install-offer:start -->\n"
    "Only on the public deployment.\n"
    "<!-- m8t:install-offer:end -->\n\n"
    "## Your brain\n",
)


def test_an_install_offer_tool_with_one_policy_block_is_accepted(tmp_path):
    assert codes(tmp_path, WITH_INSTALL_OFFER) == set()


def test_an_install_offer_tool_without_its_policy_block_is_refused(tmp_path):
    stripped = WITH_INSTALL_OFFER.replace(
        "<!-- m8t:install-offer:start -->\n"
        "Only on the public deployment.\n"
        "<!-- m8t:install-offer:end -->\n\n",
        "",
    )
    assert "persona.install_offer_policy.markers" in codes(tmp_path, stripped)


def test_a_duplicated_install_offer_policy_block_is_refused(tmp_path):
    doubled = WITH_INSTALL_OFFER.replace(
        "<!-- m8t:install-offer:end -->",
        "<!-- m8t:install-offer:end -->\n"
        "<!-- m8t:install-offer:start -->\n"
        "duplicate\n"
        "<!-- m8t:install-offer:end -->",
    )
    assert "persona.install_offer_policy.markers" in codes(tmp_path, doubled)


def test_a_list_of_tool_names_is_refused(tmp_path):
    """The shape a contributor reaches for first. It parses, it forwards, and nothing
    downstream can match a bare string to a deployed tool."""
    broken = WITH_TOOLS.replace(
        "    tools:\n      - type: web_search_preview", "    tools:\n      - web_search_preview")
    assert "persona.tools.entry_not_a_mapping" in codes(tmp_path, broken)


def test_tools_that_are_not_a_list_are_refused(tmp_path):
    scalar = GOOD.replace(
        "default-target: foundry\n",
        "default-target: foundry\ntargets:\n  foundry:\n    tools: web_search_preview\n")
    assert "persona.tools.not_a_list" in codes(tmp_path, scalar)


def test_an_entry_without_a_type_is_refused(tmp_path):
    broken = WITH_TOOLS.replace("      - type: web_search_preview\n", "      - server_label: learn\n")
    assert "persona.tools.type_missing" in codes(tmp_path, broken)


def test_a_function_tool_without_a_name_is_refused(tmp_path):
    broken = WITH_TOOLS.replace("        name: present_decision\n", "")
    assert "persona.tools.function_name_missing" in codes(tmp_path, broken)


def test_the_same_function_tool_declared_twice_is_refused(tmp_path):
    broken = WITH_TOOLS.replace(
        "      - type: function\n        name: present_decision\n",
        "      - type: function\n        name: present_decision\n"
        "      - type: function\n        name: present_decision\n",
        1,
    )
    assert "persona.tools.duplicate" in codes(tmp_path, broken)


def test_a_multiline_description_is_refused(tmp_path):
    """A literal block keeps its newlines, so the agent receives different bytes than a
    single-line description — and is then permanently stale against a persona that reads
    correctly."""
    broken = WITH_TOOLS.replace(
        '        description: "Render a card the user answers by picking one of 2-4 options."\n',
        "        description: |\n          Render a card the user answers\n          by picking one of 2-4 options.\n",
    )
    assert "persona.tools.description_multiline" in codes(tmp_path, broken)


def test_a_folded_description_is_accepted(tmp_path):
    """A folded (`>`) scalar collapses to ONE line, so the agent receives exactly what a
    single-line description would give. Refusing it would be red on correct work."""
    folded = WITH_TOOLS.replace(
        '        description: "Render a card the user answers by picking one of 2-4 options."\n',
        "        description: >-\n          Render a card the user answers\n          by picking one of 2-4 options.\n",
    )
    assert codes(tmp_path, folded) == set()


def test_a_quoted_schema_bound_is_refused(tmp_path):
    """Quoting a bound turns it into a string the host will not enforce."""
    broken = WITH_TOOLS.replace("maxLength: 120", 'maxLength: "120"')
    assert "persona.tools.schema_not_numeric" in codes(tmp_path, broken)


def test_a_repeated_non_function_tool_is_refused(tmp_path):
    """Duplicate detection used to cover only function tools, so this passed here
    while the platform's verifier reported drift on the deployed agent — a gate
    greener than the runtime check it is supposed to anticipate."""
    broken = WITH_TOOLS.replace(
        "      - type: web_search_preview\n",
        "      - type: web_search_preview\n      - type: web_search_preview\n", 1)
    assert "persona.tools.duplicate" in codes(tmp_path, broken)


def test_a_repeated_mcp_server_label_is_refused(tmp_path):
    broken = WITH_TOOLS.replace(
        "      - type: web_search_preview\n",
        "      - type: mcp\n        server_label: learn\n"
        "      - type: mcp\n        server_label: learn\n", 1)
    assert "persona.tools.duplicate" in codes(tmp_path, broken)


def test_two_mcp_servers_with_different_labels_are_accepted(tmp_path):
    ok = WITH_TOOLS.replace(
        "      - type: web_search_preview\n",
        "      - type: mcp\n        server_label: learn\n"
        "      - type: mcp\n        server_label: brain\n", 1)
    assert codes(tmp_path, ok) == set()


def test_a_boolean_schema_bound_is_refused(tmp_path):
    """isinstance(True, int) is True in Python, so a YAML boolean slipped past the
    numeric check while a quoted "120" was correctly refused."""
    assert "persona.tools.schema_not_numeric" in codes(tmp_path, WITH_TOOLS.replace("maxLength: 120", "maxLength: true"))
