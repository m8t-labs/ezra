"""The chat-invite config the installer reads.

`.m8t/chat-invite.json` decides whether `m8t bootstrap profile` offers a founder a hosted
Ezra to talk to while their platform installs. The CLI fetches it from this repository's
default branch, anonymously, at install time.

It lives here rather than in the CLI so that switching chat on, or rotating the invite, is
a change to this file and never a CLI release. That is the whole point of the arrangement
— and it is also why this rule exists. The CLI reads the file **fail-soft**: anything it
cannot make sense of resolves to one honest line, opens nothing, and lets the install carry
on. That is right for a founder mid-install and useless as a signal to us: a typo here
(`"1"` instead of `1`, `inviteURL`, a trailing comma) switches chat off for everybody and
nothing anywhere goes red. The first person to find out would be whoever flipped `enabled`
and waited for a link that never came.

So the gate belongs where the file does. A platform-side check would have to reach across a
repository boundary to watch a value this repository owns, and would redden another repo's
main whenever this one moved — the same wart that already exists for the runbook's
generated table, not worth a second instance.

Keep the acceptance rules below in step with `fetchChatInvite` in the platform's
`apps/cli/src/lib/chat-invite.ts`. This gate's job is to fail here, loudly, on what the CLI
would quietly shrug at — so the rule that matters is one-directional: **anything this gate
passes, the CLI must accept.** A false green is chat silently off for every founder.

It is deliberately STRICTER than the CLI in two places, and those are not drift:

* `enabled` must be a real boolean. The CLI treats anything that is not `true` as
  "switched off", which is a legitimate resting state — but `"true"` in quotes is the
  archetypal silent-off typo, so it fails here.
* `inviteUrl` must be a string even while chat is off. The CLI never looks at it in that
  case; requiring it stops a misspelt `inviteURL` from lying dormant until the day someone
  flips `enabled` and waits for a link that never arrives.

⚠️ `CONFIG` below and `CHAT_INVITE_PATH` in `chat-invite.ts` are the same string in two
repositories with nothing tying them together. Moving this file and updating `CONFIG` in
the same commit is a perfectly green pull request here that 404s the installer for every
founder. Treat the path as a wire contract: it changes in both repositories or in neither.
"""
from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlsplit

from .contracts import Finding

CONFIG = ".m8t/chat-invite.json"

ALLOWED_HOSTS = ("m8t.run",)
"""Hosts the CLI is willing to open. Mirrors ALLOWED_INVITE_HOSTS."""

SHELL_UNSAFE = set('&|^<>"`$%\\ \t\r\n{}')
"""Characters the CLI refuses because `cmd /c start` re-parses them on Windows.

`{` and `}` are here for a second-order reason: the CLI applies its refusal to the
URL *after* WHATWG normalization (`new URL(...).href`), and that parser percent-encodes
them — which reintroduces `%`, which is refused. So a URL carrying either is rejected
by the CLI even though neither character is itself a shell metacharacter. Same
mechanism for anything non-printable or non-ASCII, handled in `_cli_would_refuse`.
"""


def _cli_would_refuse(url: str) -> bool:
    """Would `fetchChatInvite`'s SHELL_UNSAFE test reject this address?

    The subtlety worth spelling out, because getting it wrong is a FALSE GREEN — the
    one direction that matters here. The CLI tests its refusal set against
    `new URL(url).href`, i.e. after normalization. Any character the URL parser
    percent-encodes therefore becomes a rejection, because `%` is in the set. That
    covers an unfilled `{PLACEHOLDER}`, a non-ASCII character, an editor's autocorrected
    en-dash, and any control character — none of which look like shell metacharacters,
    and all of which are exactly the "someone hand-edited this file" mistakes this
    family exists to catch.

    So: refuse the literal set, and refuse anything outside printable ASCII.
    """
    return any(ch in SHELL_UNSAFE or not (0x21 <= ord(ch) <= 0x7E) for ch in url)


def _host_allowed(host: str) -> bool:
    host = host.lower()
    return any(host == allowed or host.endswith("." + allowed) for allowed in ALLOWED_HOSTS)


def check_chat_invite(root: Path) -> list[Finding]:
    path = root / CONFIG
    if not path.exists():
        # Absent is not "switched off" — the CLI cannot tell those apart, and neither
        # should we. Deleting the file is how chat silently stops being offered.
        return [Finding("chat-invite.missing", f"{CONFIG} is missing. Chat is configured by this file; deleting it switches chat off silently.", CONFIG)]

    raw = path.read_text(encoding="utf-8")
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as err:
        return [Finding("chat-invite.malformed", f"{CONFIG} is not valid JSON: {err.msg} (line {err.lineno}). The CLI would silently offer no chat.", CONFIG, err.lineno)]

    if not isinstance(parsed, dict):
        return [Finding("chat-invite.malformed", f"{CONFIG} must be a JSON object.", CONFIG)]

    findings: list[Finding] = []

    # The `isinstance(..., bool)` is not redundant: in Python `1 == True`, so a
    # schemaVersion of `true` would otherwise sail through the `!= 1` comparison. That is
    # exactly the kind of near-miss the CLI's `!== 1` rejects.
    if parsed.get("schemaVersion") != 1 or isinstance(parsed.get("schemaVersion"), bool):
        findings.append(Finding("chat-invite.schema", f'{CONFIG}: schemaVersion must be the number 1, not {parsed.get("schemaVersion")!r}. The CLI reads any other value as a config it does not understand.', CONFIG))

    enabled = parsed.get("enabled")
    if not isinstance(enabled, bool):
        findings.append(Finding("chat-invite.enabled", f'{CONFIG}: enabled must be true or false, not {enabled!r}.', CONFIG))

    url = parsed.get("inviteUrl")
    if not isinstance(url, str):
        findings.append(Finding("chat-invite.url-type", f"{CONFIG}: inviteUrl must be a string (use \"\" while chat is off).", CONFIG))
        return findings

    # An address is only required when chat is actually on. Switched off with an empty
    # inviteUrl is the resting state this file ships in.
    if enabled is not True:
        return findings

    url = url.strip()
    if not url:
        findings.append(Finding("chat-invite.url-empty", f"{CONFIG}: enabled is true but inviteUrl is empty, so no founder would be offered chat.", CONFIG))
        return findings

    split = urlsplit(url)
    # `urlsplit` is lazy about the port: it parses the authority happily and defers the
    # ValueError until `.port` is read. `new URL()` throws outright, so a typo'd port is
    # an address the CLI refuses — touch `.port` here or the gate waves it through.
    try:
        split.port
    except ValueError:
        findings.append(Finding("chat-invite.url-port", f"{CONFIG}: inviteUrl has an invalid port — the CLI cannot parse this address at all.", CONFIG))
        return findings

    if split.scheme != "https":
        findings.append(Finding("chat-invite.url-scheme", f"{CONFIG}: inviteUrl must be https — the CLI refuses anything else before opening a browser.", CONFIG))
    elif not _host_allowed(split.hostname or ""):
        findings.append(Finding("chat-invite.url-host", f'{CONFIG}: inviteUrl host {split.hostname!r} is not one the CLI will open. Allowed: {", ".join(ALLOWED_HOSTS)} and their subdomains.', CONFIG))
    if _cli_would_refuse(url):
        findings.append(Finding("chat-invite.url-unsafe", f"{CONFIG}: inviteUrl contains a character the CLI refuses — a shell metacharacter, whitespace, a placeholder brace, or anything outside printable ASCII. Use a plain path-shaped invite.", CONFIG))

    return findings
