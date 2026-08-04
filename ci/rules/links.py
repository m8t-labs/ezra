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

import re
from pathlib import Path

from .contracts import Finding
from .tree import markdown_files

# Runtime brain space. `.gitkeep`-only on the default branch by contract, so nothing under
# these can resolve at pull-request time — and content legitimately cites example paths
# inside them (the persona names `artifacts/azure/YYYY-MM-DD-create-storage-proof.md`).
LIVE_BRAIN_SPACE = frozenset({"artifacts", "inbox", "quarantine"})

_FENCE_RE = re.compile(r"^([ \t]*)(`{3,}|~{3,})[^\n]*\n.*?^[ \t]*\2[^\n]*$", re.M | re.S)
_CODE_SPAN_RE = re.compile(r"(`+)(?!`)(.+?)\1", re.S)
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


def _candidates(text: str) -> list[tuple[str, int]]:
    """(target, offset) for every internal-reference candidate in one document."""
    no_fence = _blank(text, _FENCE_RE)
    out = [(m.group(1), m.start(1)) for m in _BACKTICK_PATH_RE.finditer(no_fence)]
    # Code spans are blanked only AFTER the backtick form is read, since that form IS a
    # code span. What remains is prose, where the other two conventions live.
    prose = _blank(no_fence, _CODE_SPAN_RE)
    out += [(m.group(1), m.start(1)) for m in _INLINE_LINK_RE.finditer(prose)]
    out += [(m.group(1), m.start(1)) for m in _REF_DEF_RE.finditer(prose)]
    out += [(m.group(1), m.start(1)) for m in _BARE_PATH_RE.finditer(prose)]
    return out


def _skip(target: str) -> bool:
    if _SCHEME_RE.match(target) or target.startswith("#"):
        return True
    path = target.split("#", 1)[0].split("?", 1)[0].rstrip("/")
    if "/" not in path:
        # A bare basename is generic doctrine — "each folder carries an `_index.md`" — not
        # a path. Resolving those would be wrong roughly 150 times over.
        return True
    return path.split("/")[0] in LIVE_BRAIN_SPACE


def _resolves(root: Path, locus: str, target: str) -> bool:
    path = target.split("#", 1)[0].split("?", 1)[0].rstrip("/")
    # Repo-root-relative is the dominant form; file-relative (`../y/SKILL.md`) also occurs.
    for base in (root, (root / locus).parent):
        try:
            candidate = (base / path).resolve()
            candidate.relative_to(root.resolve())
        except (ValueError, OSError):
            continue
        if candidate.exists():
            return True
    return False


def check_links(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for rel in markdown_files(root):
        text = (root / rel).read_text(encoding="utf-8", errors="replace")
        seen: set[str] = set()
        for target, offset in _candidates(text):
            if _skip(target) or target in seen or _resolves(root, rel, target):
                continue
            seen.add(target)
            findings.append(Finding(
                "links.unresolved",
                f"`{target}` does not exist in this repository",
                rel,
                text.count("\n", 0, offset) + 1,
            ))
    return findings
