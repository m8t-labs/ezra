"""Internal references must resolve on disk.

The three conventions below were enumerated from the live corpus rather than assumed. The
counts at the time this was written:

| convention                        | count | previously checked by |
|-----------------------------------|-------|-----------------------|
| `` `memory/MEMORY.md` `` backtick |  150  | nothing               |
| `[text](target)` inline link      |   20  | nothing               |
| bare `memory/founder.md` in prose |   20  | only `references/*.md` inside a skill body |

The backticked path is how brain content overwhelmingly refers to itself, and it was the
one form no gate had ever looked at. Checking only markdown links would have covered 20
references out of 170.

This also subsumes the ported corpus gate's R5 (linked references exist), which resolved
`references/*.md` inside skill bodies only. One defect, one code — two rules reporting the
same broken path with different names is noise for whoever has to fix it.
"""
from __future__ import annotations

import posixpath
import re
from pathlib import Path

from .contracts import Finding
from .tree import every_path, markdown_files

# Runtime brain space. `.gitkeep`-only on the default branch by contract, so nothing under
# these can resolve at pull-request time — and content legitimately cites example paths
# inside them (the persona names `artifacts/azure/YYYY-MM-DD-create-storage-proof.md`).
LIVE_BRAIN_SPACE = frozenset({"artifacts", "inbox", "quarantine"})

_FENCE_RE = re.compile(r"^([ \t]*)(`{3,}|~{3,})[^\n]*\n.*?^[ \t]*\2[^\n]*$", re.M | re.S)
# Deliberately NOT re.S. A code span does not span a blank line, and with DOTALL a single
# stray backtick pairs with the next one anywhere later in the document — blanking every
# link in between, which reads as "no findings".
_CODE_SPAN_RE = re.compile(r"(`+)(?!`)([^\n]+?)\1")
_INLINE_LINK_RE = re.compile(r"\]\(\s*([^)\s]+?)\s*\)")
_REF_DEF_RE = re.compile(r"^\s{0,3}\[[^\]]+\]:\s*(\S+)", re.M)
_BACKTICK_PATH_RE = re.compile(r"`([A-Za-z0-9_.\-/]+\.[A-Za-z0-9]{1,5})`")
_BARE_PATH_RE = re.compile(
    r"(?<![`(\w/\-.])((?:agent|skills|references|memory|targets)/[A-Za-z0-9._/\-]+\.[A-Za-z0-9]{1,5})"
)
_SCHEME_RE = re.compile(r"^[a-z][a-z0-9+.\-]*:|^//")


def _blank(text: str, rx: re.Pattern, group: int = 0) -> str:
    """Replace matches with same-length whitespace so byte offsets — and therefore line
    numbers — survive."""
    def repl(m: re.Match) -> str:
        return "".join(c if c == "\n" else " " for c in m.group(group))
    return rx.sub(repl, text)


EXPLICIT = "explicit"
"""`[text](target)` and `[label]: target` — the author wrote a link, so a bare basename is
unambiguously a path."""
INCIDENTAL = "incidental"
"""A backticked or bare path in prose. Here a bare basename is usually generic doctrine —
"each folder carries an `_index.md`" — and resolving it would be wrong ~150 times over."""


def _candidates(text: str) -> list[tuple[str, int, str]]:
    """(target, offset, convention) for every internal-reference candidate."""
    no_fence = _blank(text, _FENCE_RE)
    out = [(m.group(1), m.start(1), INCIDENTAL) for m in _BACKTICK_PATH_RE.finditer(no_fence)]
    # Code spans are blanked only AFTER the backtick form is read, since that form IS a
    # code span. What remains is prose, where the other conventions live.
    prose = _blank(no_fence, _CODE_SPAN_RE)
    out += [(m.group(1), m.start(1), EXPLICIT) for m in _INLINE_LINK_RE.finditer(prose)]
    out += [(m.group(1), m.start(1), EXPLICIT) for m in _REF_DEF_RE.finditer(prose)]
    out += [(m.group(1), m.start(1), INCIDENTAL) for m in _BARE_PATH_RE.finditer(prose)]
    return out


def _normalise(target: str) -> str:
    return target.split("#", 1)[0].split("?", 1)[0].rstrip("/")


def _skip(target: str, convention: str) -> bool:
    if _SCHEME_RE.match(target) or target.startswith("#"):
        return True
    path = _normalise(target)
    if not path:
        return True
    if "/" not in path and convention == INCIDENTAL:
        return True
    return path.split("/")[0] in LIVE_BRAIN_SPACE


def _known(root: Path) -> set[str]:
    """Every path in the repository, plus the directories implied by them.

    Membership is compared as text rather than with `Path.exists()`, which makes the check
    case-SENSITIVE on every platform. Resolving through the filesystem meant a wrong-case
    link passed on macOS and failed on the Linux runner — the check a contributor ran
    locally was not the check CI ran. It also removes any `..`-escape or symlink surface,
    since nothing is ever resolved against the real filesystem."""
    paths = set(every_path(root))
    for p in list(paths):
        parts = p.split("/")
        for i in range(1, len(parts)):
            paths.add("/".join(parts[:i]))
    return paths


def _resolves(known: set[str], locus: str, target: str) -> bool:
    path = _normalise(target)
    here = locus.rsplit("/", 1)[0] if "/" in locus else ""
    # Repo-root-relative is the dominant form; file-relative (`../y/SKILL.md`) also occurs.
    for base in (path, f"{here}/{path}" if here else path):
        resolved = posixpath.normpath(base)
        if resolved.startswith("../") or resolved == "..":
            continue
        if resolved in known:
            return True
    return False


def check_links(root: Path) -> list[Finding]:
    known = _known(root)
    findings: list[Finding] = []
    for rel in markdown_files(root):
        text = (root / rel).read_text(encoding="utf-8", errors="replace")
        seen: set[str] = set()
        for target, offset, convention in _candidates(text):
            if _skip(target, convention) or target in seen or _resolves(known, rel, target):
                continue
            seen.add(target)
            findings.append(Finding(
                "links.unresolved",
                f"`{target}` does not exist in this repository",
                rel,
                text.count("\n", 0, offset) + 1,
            ))
    return findings
