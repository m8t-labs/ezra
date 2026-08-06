"""The runbook rule, one red case per claim.

Every breaker starts from the REAL `guides/bootstrap.md` and changes exactly one thing.
A hand-built fixture would prove the regex matches a string someone wrote to match it;
starting from the shipped document proves the rule fires on the document it guards.

Three claims, three breakers, per the rule family discipline: a single lumped breaker
would let two of the three go vacuous the day someone deletes an assertion.
"""
from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from ci.rules.runbook import (
    BROWSER_COMMAND,
    FALLBACK_VERDICT,
    ORG_COMMAND,
    RUNBOOK,
    STOP_PHRASE,
    check_runbook,
)

ROOT = Path(__file__).resolve().parents[2]


def codes(findings) -> set[str]:
    return {f.code for f in findings}


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A copy of the real runbook, in a tree shaped like this repository."""
    (tmp_path / "guides").mkdir()
    shutil.copy(ROOT / RUNBOOK, tmp_path / RUNBOOK)
    return tmp_path


def edit(repo: Path, old: str, new: str) -> None:
    p = repo / RUNBOOK
    text = p.read_text(encoding="utf-8")
    assert old in text, f"fixture no longer matches the runbook: {old!r} is gone"
    p.write_text(text.replace(old, new, 1), encoding="utf-8")


# ── green ──────────────────────────────────────────────────────────────────────

def test_the_shipped_runbook_passes(repo):
    assert check_runbook(repo) == []


def test_the_real_repository_passes():
    """Guards the fixture above from drifting away from what actually ships."""
    assert check_runbook(ROOT) == []


# ── claim 1: the org is chosen deliberately ────────────────────────────────────

def test_red_when_the_org_is_not_chosen_by_asking_the_cli(repo):
    edit(repo, ORG_COMMAND, "m8t brain something-else")
    assert "runbook.org.undeliberate" in codes(check_runbook(repo))


def test_red_when_the_raw_listing_is_promoted_out_of_its_fallback_row(repo):
    """The subtle one: the command stays put, the row stops calling it a fallback."""
    p = repo / RUNBOOK
    text = p.read_text(encoding="utf-8")
    row_at = text.find(FALLBACK_VERDICT)
    assert row_at != -1
    start = text.rfind("\n", 0, row_at) + 1
    end = text.find("\n", row_at)
    row = text[start:end]
    p.write_text(text.replace(row, row.replace("Fall back", "Prefer to check manually")),
                 encoding="utf-8")
    assert "runbook.org.raw_listing_promoted" in codes(check_runbook(repo))


# ── claim 2: the founder is stopped before the browser opens ───────────────────

def test_red_when_the_stop_is_removed(repo):
    edit(repo, STOP_PHRASE, "Let them know what is happening")
    assert "runbook.stop.missing" in codes(check_runbook(repo))


def test_red_when_the_stop_moves_after_the_browser_command(repo):
    """A pause after the window opened is a caption, not a pause."""
    p = repo / RUNBOOK
    text = p.read_text(encoding="utf-8")
    without = text.replace(STOP_PHRASE, "", 1)
    browser_at = without.find(BROWSER_COMMAND)
    assert browser_at != -1
    after = without[:browser_at + len(BROWSER_COMMAND)] + f"\n\n{STOP_PHRASE}\n" + without[browser_at + len(BROWSER_COMMAND):]
    p.write_text(after, encoding="utf-8")
    assert "runbook.stop.after_browser" in codes(check_runbook(repo))


def test_red_when_the_browser_opens_before_the_brains_are_explained(repo):
    """Every occurrence, not the first: the step explains the brains twice, and removing
    one leaves the claim true. A breaker that changes less than the whole claim proves
    nothing about the rule."""
    p = repo / RUNBOOK
    text = p.read_text(encoding="utf-8")
    assert text.lower().count("working memory") >= 2
    p.write_text(text.replace("working memory", "the thing"), encoding="utf-8")
    assert "runbook.stop.unexplained" in codes(check_runbook(repo))


# ── claim 3: no skip path that does not work ───────────────────────────────────

@pytest.mark.parametrize("offer", [
    "You can skip this step if you do not want brain-backed workers.",
    "This gives you a basic platform without brain-backed workers.",
    "If you are on a personal GitHub account, you may skip this step.",
])
def test_red_when_a_non_working_skip_is_offered(repo, offer):
    p = repo / RUNBOOK
    p.write_text(p.read_text(encoding="utf-8") + "\n" + offer + "\n", encoding="utf-8")
    assert "runbook.skip.not_a_working_path" in codes(check_runbook(repo))


# ── the guard cannot go quiet ──────────────────────────────────────────────────

def test_red_when_the_runbook_itself_disappears(repo):
    (repo / RUNBOOK).unlink()
    assert "runbook.missing" in codes(check_runbook(repo))


def test_silent_only_when_there_is_no_runbook_folder_at_all(tmp_path):
    """A copy that carries no runbook has nothing to guard. Absence of the FOLDER is a
    shape someone chose; absence of the FILE inside it is the failure above."""
    assert check_runbook(tmp_path) == []


def test_red_when_the_guarded_step_is_renamed_away(repo):
    edit(repo, "### 3b.", "### 3c.")
    assert "runbook.step_missing" in codes(check_runbook(repo))
