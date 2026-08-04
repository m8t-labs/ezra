from __future__ import annotations

from pathlib import Path

from ci.rules.layout import check_layout
from ci.rules.primitives import check_primitives

HANDOFF = "<m8t:advisor_handoff>\nattempted blocked package recipient next_action\n"
NOTIFY = ("<m8t:notify_advisor>\nto from_label subject body attachments mode\n"
          "proof in artifacts/notify/ — prepare then submit\n")


def full(tmp_path: Path) -> Path:
    for rel in (".m8t/brain.yaml", "memory/MEMORY.md", "skills/_index.md",
                "references/_index.md", "AGENTS.md", "README.md", "LICENSE"):
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("x\n", encoding="utf-8")
    for name in ("inbox", "artifacts", "quarantine"):
        d = tmp_path / name
        d.mkdir(exist_ok=True)
        (d / ".gitkeep").write_text("", encoding="utf-8")
    (tmp_path / "agent").mkdir(exist_ok=True)
    (tmp_path / "agent" / "persona.md").write_text("x\n", encoding="utf-8")
    return tmp_path


def layout_codes(root: Path) -> set[str]:
    return {f.code for f in check_layout(root)}


# ── layout ─────────────────────────────────────────────────────────────────────
def test_a_complete_layout_passes(tmp_path):
    assert layout_codes(full(tmp_path)) == set()


def test_a_missing_brain_yaml_is_refused(tmp_path):
    root = full(tmp_path)
    (root / ".m8t" / "brain.yaml").unlink()
    assert layout_codes(root) == {"layout.missing"}


def test_a_missing_license_is_refused(tmp_path):
    root = full(tmp_path)
    (root / "LICENSE").unlink()
    assert layout_codes(root) == {"layout.missing"}


def test_a_missing_brain_space_directory_is_refused(tmp_path):
    root = full(tmp_path)
    (root / "inbox" / ".gitkeep").unlink()
    (root / "inbox").rmdir()
    assert "layout.brain_space.missing" in layout_codes(root)


def test_a_brain_space_directory_without_a_gitkeep_is_refused(tmp_path):
    root = full(tmp_path)
    (root / "quarantine" / ".gitkeep").unlink()
    assert "layout.brain_space.unheld" in layout_codes(root)


def test_a_symlink_inside_the_consumed_set_is_refused(tmp_path):
    """The platform extracts this repository from a tarball. A symlink in the consumed set
    is how an extraction writes outside its target directory."""
    root = full(tmp_path)
    (root / "skills" / "evil.md").symlink_to("/etc/passwd")
    assert "layout.symlink" in layout_codes(root)


def test_a_symlink_outside_the_consumed_set_is_not_this_rule(tmp_path):
    root = full(tmp_path)
    (root / "inbox" / "link.md").symlink_to("/etc/passwd")
    assert "layout.symlink" not in layout_codes(root)


# ── primitives ─────────────────────────────────────────────────────────────────
def prims(tmp_path: Path, handoff: str = HANDOFF, notify: str = NOTIFY) -> set[str]:
    refs = tmp_path / "references"
    refs.mkdir(parents=True, exist_ok=True)
    (refs / "advisor-handoff.md").write_text(handoff, encoding="utf-8")
    (refs / "notify-advisor-contract.md").write_text(notify, encoding="utf-8")
    return {f.code for f in check_primitives(tmp_path)}


def test_both_wire_contracts_present_passes(tmp_path):
    assert prims(tmp_path) == set()


def test_a_missing_wire_contract_is_refused(tmp_path):
    assert {f.code for f in check_primitives(tmp_path)} == {"primitives.missing"}


def test_dropping_a_handoff_field_is_refused(tmp_path):
    assert "primitives.field" in prims(tmp_path, handoff=HANDOFF.replace("next_action", ""))


def test_dropping_a_notify_field_is_refused(tmp_path):
    assert "primitives.field" in prims(tmp_path, notify=NOTIFY.replace("from_label", ""))


def test_dropping_the_proof_directory_is_refused(tmp_path):
    assert "primitives.field" in prims(tmp_path, notify=NOTIFY.replace("artifacts/notify/", ""))


def test_removing_the_marker_is_refused(tmp_path):
    assert "primitives.marker" in prims(tmp_path, handoff=HANDOFF.replace("<m8t:advisor_handoff>", ""))
