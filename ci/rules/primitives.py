"""The two reference documents that are wire contracts, not prose.

`advisor-handoff.md` and `notify-advisor-contract.md` describe marker blocks the platform
parses. If a field name is dropped while tidying the prose, the agent emits a block the
platform cannot read — and nothing else in this repository would notice.

Restored from the platform's deleted `test_seed_primitives.py`.
"""
from __future__ import annotations

from pathlib import Path

from .contracts import Finding

HANDOFF = "references/advisor-handoff.md"
NOTIFY = "references/notify-advisor-contract.md"

CONTRACTS = (
    (HANDOFF, "<m8t:advisor_handoff>",
     ("attempted", "blocked", "package", "recipient", "next_action")),
    (NOTIFY, "<m8t:notify_advisor>",
     ("to", "from_label", "subject", "body", "attachments", "mode", "artifacts/notify/", "prepare", "submit")),
)


def check_primitives(root: Path) -> list[Finding]:
    f: list[Finding] = []
    for rel, marker, fields in CONTRACTS:
        path = root / rel
        if not path.is_file():
            f.append(Finding("primitives.missing", f"{rel} is required — it is a wire contract", rel))
            continue
        body = path.read_text(encoding="utf-8")
        if marker not in body:
            f.append(Finding("primitives.marker", f"{rel} no longer documents the {marker} marker", rel))
        for field in fields:
            if field not in body:
                f.append(Finding("primitives.field",
                                 f"{rel} no longer documents '{field}', which the platform parses", rel))
    return f
