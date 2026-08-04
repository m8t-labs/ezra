"""SUPPORT.md and the issue-template chooser are one routing table rendered twice.

Someone will eventually move a destination in one and not the other, and the failure mode
is silent: two documents that each look right, pointing different people to different
places. This makes the drift a test failure instead.
"""
from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
SUPPORT = ROOT / "SUPPORT.md"
CONFIG = ROOT / ".github" / "ISSUE_TEMPLATE" / "config.yml"

_URL_RE = re.compile(r"https?://[^\s)>\]]+")

SECURITY_MAILBOX = "security@m8t.run"


def _config_destinations() -> set[str]:
    config = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    return {link["url"].rstrip("/") for link in config["contact_links"]}


def _support_destinations() -> set[str]:
    return {u.rstrip("/") for u in _URL_RE.findall(SUPPORT.read_text(encoding="utf-8"))}


def test_the_chooser_offers_destinations_support_also_names():
    """SUPPORT.md may name more (it also points at this repository's own issues), but it
    must never omit somewhere the chooser sends people."""
    missing = _config_destinations() - _support_destinations()
    assert not missing, f"in the issue-template chooser but not in SUPPORT.md: {sorted(missing)}"


def test_both_documents_route_security_to_the_same_mailbox():
    assert SECURITY_MAILBOX in SUPPORT.read_text(encoding="utf-8")
    assert SECURITY_MAILBOX in (ROOT / "SECURITY.md").read_text(encoding="utf-8")


def test_the_chooser_actually_offers_destinations():
    """Guards the test above from passing vacuously: an empty chooser has nothing to omit."""
    assert len(_config_destinations()) >= 3


def test_blank_issues_are_disabled_so_the_chooser_is_reached():
    config = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    assert config["blank_issues_enabled"] is False
