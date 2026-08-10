"""The chat-invite rule, one red case per way the file can quietly stop working.

Every breaker starts from the REAL `.m8t/chat-invite.json` and changes exactly one thing.
A hand-built fixture would prove the rule matches a string written to match it; starting
from the shipped file proves it fires on the file it guards — and the first test proves the
shipped file passes, so the rule cannot be green by never looking.

The failure this whole family exists for is silent: the CLI reads this file fail-soft, so
every one of these mistakes switches chat off for every founder while nothing goes red.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from ci.rules.chat_invite import CONFIG, check_chat_invite

ROOT = Path(__file__).resolve().parents[2]


def codes(findings) -> set[str]:
    return {f.code for f in findings}


def shipped() -> dict:
    return json.loads((ROOT / CONFIG).read_text(encoding="utf-8"))


def written(tmp_path: Path, payload, *, raw: str | None = None) -> Path:
    (tmp_path / ".m8t").mkdir(parents=True, exist_ok=True)
    (tmp_path / CONFIG).write_text(
        raw if raw is not None else json.dumps(payload, indent=2), encoding="utf-8",
    )
    return tmp_path


def test_the_shipped_config_passes():
    assert check_chat_invite(ROOT) == []


def test_a_missing_file_is_a_finding(tmp_path):
    # Deleting it is how chat silently stops being offered; the CLI cannot tell an
    # absent file from a switched-off one, so this gate has to.
    assert "chat-invite.missing" in codes(check_chat_invite(tmp_path))


def test_malformed_json_is_a_finding(tmp_path):
    root = written(tmp_path, None, raw='{ "schemaVersion": 1, }')
    assert "chat-invite.malformed" in codes(check_chat_invite(root))


@pytest.mark.parametrize("value", ["1", 2, True, None])
def test_a_schema_version_the_cli_would_not_recognise(tmp_path, value):
    root = written(tmp_path, {**shipped(), "schemaVersion": value})
    assert "chat-invite.schema" in codes(check_chat_invite(root))


def test_enabled_must_be_a_boolean(tmp_path):
    root = written(tmp_path, {**shipped(), "enabled": "true"})
    assert "chat-invite.enabled" in codes(check_chat_invite(root))


def test_a_misspelt_url_key_reads_as_no_url(tmp_path):
    payload = {k: v for k, v in shipped().items() if k != "inviteUrl"}
    root = written(tmp_path, {**payload, "enabled": True, "inviteURL": "https://m8t.run/i/x"})
    assert "chat-invite.url-type" in codes(check_chat_invite(root))


def test_enabled_with_no_address(tmp_path):
    root = written(tmp_path, {**shipped(), "enabled": True, "inviteUrl": "  "})
    assert "chat-invite.url-empty" in codes(check_chat_invite(root))


def test_an_address_that_is_off_while_empty_is_fine(tmp_path):
    # The resting state this file ships in: switched off, no address. Not a finding.
    root = written(tmp_path, {**shipped(), "enabled": False, "inviteUrl": ""})
    assert check_chat_invite(root) == []


def test_a_json_root_that_is_not_an_object(tmp_path):
    root = written(tmp_path, None, raw='["schemaVersion", 1]')
    assert "chat-invite.malformed" in codes(check_chat_invite(root))


@pytest.mark.parametrize(
    ("url", "code"),
    [
        ("http://m8t.run/i/x", "chat-invite.url-scheme"),
        ("https://evil.example/i/x", "chat-invite.url-host"),
        ("https://notm8t.run/i/x", "chat-invite.url-host"),
        ("https://m8t.run/i/x?a=1&b=2", "chat-invite.url-unsafe"),
        ("https://m8t.run/i/%USERNAME%", "chat-invite.url-unsafe"),
        # A port the CLI's URL parser throws on. `urlsplit` defers that error until
        # `.port` is read, so the rule has to reach for it or wave the address through.
        ("https://m8t.run:notaport/i/x", "chat-invite.url-port"),
        ("https://m8t.run:99999/i/x", "chat-invite.url-port"),
    ],
)
def test_an_address_the_cli_would_refuse(tmp_path, url, code):
    root = written(tmp_path, {**shipped(), "enabled": True, "inviteUrl": url})
    assert code in codes(check_chat_invite(root))


# The CLI applies its refusal set to the NORMALIZED url (`new URL(...).href`), so every
# character the URL parser percent-encodes becomes a rejection — `%` is in the set. None of
# these look like shell metacharacters, and all of them are ordinary hand-editing mistakes:
# an unfilled template, an editor autocorrecting a hyphen, a pasted non-ASCII path. Before
# this was fixed, all of them passed CI and were then silently refused on every install.
@pytest.mark.parametrize(
    "url",
    [
        "https://m8t.run/i/{INVITE}",
        "https://m8t.run/i/café",
        "https://m8t.run/i/abc–def",
        "https://m8t.run/中文",
        "https://m8t.run/i/x?q=café",
        "https://m8t.run/i/a b",
    ],
)
def test_an_address_the_url_parser_would_re_encode(tmp_path, url):
    root = written(tmp_path, {**shipped(), "enabled": True, "inviteUrl": url})
    assert "chat-invite.url-unsafe" in codes(check_chat_invite(root))


@pytest.mark.parametrize("url", ["https://m8t.run/i/abc123", "https://chat.m8t.run/i/abc123"])
def test_an_address_the_cli_would_open(tmp_path, url):
    root = written(tmp_path, {**shipped(), "enabled": True, "inviteUrl": url})
    assert check_chat_invite(root) == []
