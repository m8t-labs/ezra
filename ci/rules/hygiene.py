"""Repo-wide hygiene: what must never reach a public branch.

This repo is public and it is written to by a machine. The hosted Ezra's librarian
promotes real conversation content into `memory/` and `skills/` on a learning branch, and
a promotion pull request is where a real person's name, mailbox, or subscription id would
arrive. So the sweep is **repo-wide**, not corpus-only: the platform's seed gate only ever
scrubbed `skills/` and the references those skills linked, which left `memory/` — the one
directory a machine writes prose into — unscrubbed.

Two rules are deliberately absent, both for the same reason (a rule that fires on correct
content forever is a rule people learn to delete):

* **Epic/feature codes** (`F07`, `E2-F5`). In an Azure brain, `E2`, `D4` and `F8` are VM
  sizes. See `test_azure_vm_sizes_are_never_flagged_as_epic_codes`.
* **RFC 2606 example domains.** Content that teaches email or ACS setup uses
  `example.com` legitimately.

`ci/` is excluded from the sweep, because a checker's fixtures contain examples of what it
hunts for and scanning itself would be permanently red. That exclusion is also why the
named-entity list is stored as digests in `entities.py` rather than as text: a rule the
sweep cannot see must not be the one place its own contraband is written down.
"""
from __future__ import annotations

import re

from .contracts import Finding
from .entities import find_named_entity

# ── what must not appear ───────────────────────────────────────────────────────

# Matched against LOWERCASED text; keep the patterns lowercase.
#
# Only SHAPES live here. Named third parties and internal tool names are matched by digest
# in `entities.py` — writing them out would publish, in a public repository, exactly the
# list of associations the rule exists to prevent.
SCRUB = [
    # Any microsoft.com mailbox, including subdomains (corp., ntdev., …). The email rule
    # below exempts this whole domain on the grounds that this rule owns it, so the two
    # must cover the same set or addresses fall between them.
    ("mailbox", re.compile(r"[\w.+-]+@(?:[\w-]+\.)*microsoft\.com"), "internal Microsoft mailbox"),
    ("internal_host", re.compile(r"\b[\w.-]*\.msft\.net\b|loop\.cloud\.microsoft|loop\.microsoft\.com"),
     "internal Microsoft host"),
]

# The Microsoft "Loop" wiki is a capitalized proper noun, so it is matched case-sensitively
# against the ORIGINAL text ("per Loop", "(Loop)", "in the Loop"). But English capitalizes
# the first word of a sentence, heading and list item, and `Loop` is also an ordinary verb —
# the live corpus carries `## Loop the SA in`. Position decides: initial `Loop` is the verb.
_LOOP_RE = re.compile(r"\bLoop\b")
_SENTENCE_INITIAL = re.compile(r"(?:^|[.!?:])\s*(?:[#>*+-]+\s*|\d+[.)]\s*)*$")

AKAMS_ALLOWLIST = frozenset({"aka.ms/oai/stuquotarequest", "aka.ms/oai/quotaincrease"})
_AKAMS_RE = re.compile(r"aka\.ms/[a-z0-9._/-]+")

DESTRUCTIVE = [
    r"\brm\s+(-[a-z]+\s+)*-[a-z]*(rf|fr)[a-z]*\b",
    r"\brm\s+(-[a-z]+\s+)*-[a-z]*r[a-z]*\s+(-[a-z]+\s+)*-[a-z]*f[a-z]*\b",
    r"\brm\s+(-[a-z]+\s+)*-[a-z]*f[a-z]*\s+(-[a-z]+\s+)*-[a-z]*r[a-z]*\b",
    r"push\s+--force",
    r"\bpush\s+\S+\s+\+\S+",
    r"\bgit\s+(-\S+(\s+\S+)?\s+)*reset\s+--hard\b",
    r"curl\s+[^\n|]*\|\s*sh",
    r"\bfind\s+[^\n]*-delete\b",
    r"\bdrop\s+table\b",
]
# The platform's pattern was `ignore (all|previous) instructions`, which does not match the
# single most common phrasing of the attack — "ignore all previous instructions" — because
# it allows exactly one word between the verb and the noun. Widened to a short word gap, and
# `disregard` added. False positives in Azure prose are essentially nil; a miss is expensive.
# A TRIPWIRE, not a boundary. These catch the common phrasings and careless copy-paste;
# they do not stop anyone who is trying. Content is defended by the agent's own rules and
# by review, not by this list. SECURITY.md says so out loud, because a reader who mistakes
# it for a boundary will trust content it passed.
INJECTION = [
    r"\b(?:ignore|disregard|forget)\s+(?:\w+\s+){0,6}(?:instructions|prompt|rules)\b",
    r"\b(?:previous|prior|above|earlier|preceding)\s+(?:\w+\s+){0,3}instructions\b",
    r"exfiltrat",
    r"disable .*(safety|guard|check)",
    r"\b(?:developer|god|dan)\s+mode\b",
    r"\byour new (?:system )?prompt\b",
]

SECRETS = [
    # Token prefixes are case-SIGNIFICANT (`GHP_` is not a token); the descriptive
    # key/value forms below are not, so those carry re.I.
    ("github_token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b|\bgithub_pat_[A-Za-z0-9_]{20,}"),
     "a GitHub token"),
    # Every current model-provider key inserts a hyphenated segment before the random part
    # (`sk-proj-…`, `sk-ant-api03-…`), so a pattern requiring alphanumerics straight after
    # `sk-` matches only the retired format.
    ("api_key", re.compile(r"\bsk-(?:[A-Za-z0-9]+-)*[A-Za-z0-9]{20,}\b"
                           r"|\bxox[baprs]-[A-Za-z0-9-]{10,}"
                           r"|\bAKIA[0-9A-Z]{16}\b"), "an API key"),
    ("connection_string", re.compile(r"AccountKey=|SharedAccessSignature=|Password=[^\s<>{]", re.I),
     "a connection string"),
    ("private_key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----", re.I), "a private key"),
]

# RFC 2606 reserves these for documentation. See the module docstring.
_EXAMPLE_DOMAIN = re.compile(r"(?:^|\.)(?:example\.(?:com|org|net)|test|invalid|localhost)$|\.example$")
_OWN_DOMAIN = re.compile(r"(?:^|\.)m8t\.run$")
# microsoft.com is owned by the `mailbox` rule above — one cause, one finding.
_MAILBOX_OWNED = re.compile(r"(?:^|\.)microsoft\.com$")
_EMAIL_RE = re.compile(r"\b[\w.+-]+@([\w-]+(?:\.[\w-]+)+)\b")

_GUID_RE = re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b", re.I)

_WORK_ITEM_RE = re.compile(r"\bW-\d{6,}\b")
# Narrowed to a numbered reference. A bare `§` is legitimate in legal or EU-regulatory
# prose a contributor might reasonably add.
_SECTION_REF_RE = re.compile(r"§\s*\d")

# Content the agent actually reads as instructions: the consumed set, plus the operating
# doctrine. The safety rules — destructive commands and prompt-injection markers — exist to
# protect the agent from what it ingests, so they apply HERE and nowhere else.
#
# They must not apply to repository furniture. A SECURITY.md that explains what prompt
# injection is has to use the vocabulary of prompt injection; an injection guard that fires
# on honest security documentation is a category error, and the same
# fires-on-correct-content-forever failure the epic-code rule was dropped for.
#
# Secrets, personal data and internal strings stay repository-wide: a leaked token in
# SECURITY.md is still a leaked token.
INGESTED_ROOTS = ("agent/", "memory/", "skills/", "references/", "targets/")
INGESTED_FILES = ("AGENTS.md",)


def is_ingested(rel: str) -> bool:
    """True when the agent reads this file as instructions."""
    return rel in INGESTED_FILES or rel.startswith(INGESTED_ROOTS)


def _line_of(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


def _is_sentence_initial(text: str, start: int) -> bool:
    """True when the match begins a line, a heading, a list item, or a sentence."""
    line_start = text.rfind("\n", 0, start) + 1
    return bool(_SENTENCE_INITIAL.search(text[line_start:start]))


def _placeholder_guid(value: str) -> bool:
    """A GUID whose hex is a single repeated character is a documentation placeholder."""
    hexits = set(value.replace("-", "").lower())
    return len(hexits) == 1


def scan_text(text: str, locus: str, ingested: bool = True) -> list[Finding]:
    """Return hard findings for one document. At most one finding per rule per document —
    three mailboxes in one file are one problem, not three.

    `ingested` says whether the agent reads this file as instructions; see
    `is_ingested`. It gates the safety rules only."""
    found: list[Finding] = []
    seen: set[str] = set()

    def add(code: str, message: str, pos: int, key: str | None = None) -> None:
        dedupe = key or code
        if dedupe in seen:
            return
        seen.add(dedupe)
        found.append(Finding(code, message, locus, _line_of(text, pos)))

    low = text.lower()

    for name, rx, label in SCRUB:
        m = rx.search(low)
        if m:
            add(f"hygiene.scrub.{name}", f"{label} present: remove it before this is public", m.start())

    # The message names the class and the line, never the match — the contributor knows
    # what they wrote, and CI repeating it back would re-publish the entry.
    offset = find_named_entity(text)
    if offset is not None:
        add("hygiene.scrub.named_entity",
            "a named third party or internal tool name appears on this line: remove it, or "
            "describe the situation without naming them", offset)

    for m in _LOOP_RE.finditer(text):
        if not _is_sentence_initial(text, m.start()):
            add("hygiene.scrub.loop_wiki",
                "reference to the internal Loop wiki: cite a public source instead", m.start())
            break

    for m in _AKAMS_RE.finditer(low):
        slug = m.group(0).rstrip(".")   # the char class greedily takes a trailing sentence period
        if slug not in AKAMS_ALLOWLIST:
            add("hygiene.scrub.akams", f"non-allowlisted aka.ms link: {slug}", m.start(), key=f"akams:{slug}")

    if ingested:
        for pat in DESTRUCTIVE:
            m = re.search(pat, low)
            if m:
                add("hygiene.safety.destructive", f"destructive command pattern /{pat}/", m.start())

        for pat in INJECTION:
            m = re.search(pat, low)
            if m:
                add("hygiene.safety.injection", f"prompt-injection marker /{pat}/", m.start())

    for name, rx, label in SECRETS:
        m = rx.search(text)
        if m:
            add(f"hygiene.secret.{name}", f"what looks like {label}: rotate it, then remove it", m.start())

    for m in _EMAIL_RE.finditer(text):
        domain = m.group(1).lower()
        if _EXAMPLE_DOMAIN.search(domain) or _OWN_DOMAIN.search(domain) or _MAILBOX_OWNED.search(domain):
            continue
        add("hygiene.identity.email",
            "an email address that is not ours: use an example.com placeholder", m.start())

    for m in _GUID_RE.finditer(text):
        if _placeholder_guid(m.group(0)):
            continue
        add("hygiene.identity.guid",
            "a GUID (subscription, tenant or object id) has no place in public brain content",
            m.start())

    m = _WORK_ITEM_RE.search(text)
    if m:
        add("hygiene.internal.work_item", "internal work-item id: name the behaviour instead", m.start())

    m = _SECTION_REF_RE.search(text)
    if m:
        add("hygiene.internal.section_ref",
            "internal design-doc section reference: name the behaviour instead", m.start())

    return found
