"""Named third parties and internal tool names, stored as digests rather than as text.

## What this does and does not protect

This list exists so that content promoted into a public repository does not name a company
or an internal tool it should not. Writing that list in plain text would put the names
themselves in the public repository — a guard that carries its own contraband, and a
curated list of associations is worse than the mentions it prevents.

Hashing makes the list **illegible**: it cannot be read, grepped, or found by a search
engine, and a contributor browsing this file learns nothing. It is **not** cryptographic
secrecy. The salt ships here, so anyone who already suspects a specific name can confirm
it in one line of Python.

That sets a hard ceiling on what belongs here: **names we would rather not associate with
publicly, and nothing above that.** Anything genuinely sensitive — a credential, a person,
an unannounced partner — does not belong in a public checker at all, hashed or otherwise.

## Adding an entry

The plaintext master list lives in the platform repository, which is private. This file
carries digests only. To add one:

    python ci/rules/entities.py --digest "the name"

and paste the line it prints into `DIGESTS`. Keep the file sorted; the ordering carries no
information.
"""
from __future__ import annotations

import hashlib
import re
import sys

SALT = "m8t-agent-repo-entity-v1"
"""Ships in the open, deliberately. See the module docstring — this defeats casual reading
and search indexing, not a determined guess."""

MAX_NGRAM = 4
"""The longest entry is four words. Raising this costs scan time on every document."""

# Digests of the entries, sorted. Deliberately unlabelled: a comment naming what each one
# is would undo the point of hashing them.
DIGESTS = frozenset({
    "0bde909e1e88416cb7dd0d4a6bec80d02b8e4ae7e2936dd63f624d1127e27655",
    "1a5c9d87da9fd6b04f77927f2277bdbe293069acc9eb11b6a14639bf8b3d0442",
    "22b9ff9fb0b437bdfbe4537e66b76d6235d2acb35c0d35fb40e4c421592c2d38",
    "7258411925597ee0737dac2070fefcec8faeeafbe30dfff8dee117c876c1876c",
    "7f10231d1ff072b97c55ea7d349d4b51d2c8e2385c85c8dd4704b2d37e9caac9",
    "827816d938d5aac42e028de6f8114c892c5f55fb820c3c4234678a008e25a793",
    "8d6af8f3b6f8003362437bfcc0715ba9f97c39b28651fe7533399cf942329650",
    "c3fe46272fbbe3a41d97fbe5e8abf863b10a62159956492275c64c6ad525308c",
    "ed407776fd3b8efe073321955ce17e743bfd61ea4a156f7f793784fcda61223b",
})

_TOKEN_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")


def digest(phrase: str) -> str:
    """The stored form of one entry. Normalisation must match `_tokens` exactly, or an
    entry will be stored in a shape the scanner can never produce."""
    normalised = " ".join(_TOKEN_RE.findall(phrase.lower()))
    return hashlib.sha256(f"{SALT}:{normalised}".encode()).hexdigest()


def _tokens(text: str) -> list[tuple[str, int]]:
    return [(m.group(0), m.start()) for m in _TOKEN_RE.finditer(text.lower())]


def find_named_entity(text: str, digests: frozenset[str] = DIGESTS) -> int | None:
    """Byte offset of the first entry present in `text`, or None.

    Returns a position, never the matched text: the finding tells a contributor which line
    to look at, and CI does not need to confirm what they already wrote.
    """
    tokens = _tokens(text)
    for size in range(1, MAX_NGRAM + 1):
        for i in range(len(tokens) - size + 1):
            phrase = " ".join(t for t, _ in tokens[i:i + size])
            if hashlib.sha256(f"{SALT}:{phrase}".encode()).hexdigest() in digests:
                return tokens[i][1]
    return None


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--digest":
        print(f'    "{digest(sys.argv[2])}",')
    else:
        print(__doc__)
        print('usage: python ci/rules/entities.py --digest "the name"', file=sys.stderr)
        raise SystemExit(2)
