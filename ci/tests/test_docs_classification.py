"""Product runbooks are public prose, not brain content.

`guides/` holds the BYOC install runbook a founder pastes into a coding agent. It lives in
this repository because the platform's source is private and the runbook must stay
anonymously readable — but it is not brain content: the agent never reads it, the platform
never consumes it, and it refers to files that exist in a different repository.

So it gets its own classification. Three claims, each tested here rather than inherited:

* the reference resolver skips it — its links point into the platform repo by design;
* the doc-shape families never looked at it in the first place (a path exclusion nobody
  tests is a dormant gate);
* the hygiene sweep stays ARMED on it, minus exactly two rules that fire on correct
  content in Azure documentation — role GUIDs and Microsoft's own `aka.ms` links.

Both exemptions are scoped to the folder BY NAME. A prefix or a wildcard would let a
future folder inherit them silently, which is how an exemption outlives its reason.
"""
from __future__ import annotations

from pathlib import Path

from ci.rules.corpus import check_corpus
from ci.rules.hygiene import is_ingested, scan_text
from ci.rules.layout import check_layout
from ci.rules.links import check_links
from ci.rules.primitives import check_primitives
from ci.rules.tree import DOCS_ROOTS, is_docs

A_REAL_GUID = "7f3a1c02-4b8e-4d1a-9f60-2ec5b8a91d34"
A_TOKEN = "ghp_" + "A" * 36


def build(tmp_path: Path, files: dict[str, str]) -> Path:
    for rel, body in files.items():
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body, encoding="utf-8")
    return tmp_path


def codes(findings) -> set[str]:
    return {f.code for f in findings}


# ── the classification itself ──────────────────────────────────────────────────

def test_the_runbook_folder_is_classified_as_docs():
    assert is_docs("guides/install.md")
    assert is_docs("guides/install/prereqs-macos.md")


def test_brain_content_is_not_classified_as_docs():
    assert not is_docs("skills/quota-diagnose/SKILL.md")
    assert not is_docs("memory/MEMORY.md")
    assert not is_docs("README.md")


def test_the_classification_matches_a_whole_path_segment():
    """`guidesomething/` is a different folder and inherits nothing."""
    assert not is_docs("guidesomething/x.md")
    assert not is_docs("skills/guides/SKILL.md")


def test_every_docs_root_has_a_case_here():
    """FAMILIES==BREAKERS, applied to the exemption list: a name added to DOCS_ROOTS with
    no case of its own would inherit two hygiene exemptions under a green suite."""
    assert DOCS_ROOTS == {"guides"}


# ── the agent does not read it ─────────────────────────────────────────────────

def test_the_runbook_is_not_ingested():
    """Pinned, not inherited. The safety rules key off `is_ingested`, so this one boolean
    is what keeps `rm -rf ~/.m8t` in an uninstall guide from reading as an attack."""
    assert not is_ingested("guides/uninstall.md")
    assert is_ingested("memory/MEMORY.md")


def test_a_destructive_command_in_the_runbook_is_not_a_finding():
    body = "Remove the folder:\n\n```bash\nrm -rf ~/.m8t\n```\n"
    assert "hygiene.safety.destructive" not in codes(
        scan_text(body, "guides/uninstall.md", ingested=is_ingested("guides/uninstall.md")))
    assert "hygiene.safety.destructive" in codes(
        scan_text(body, "memory/notes.md", ingested=is_ingested("memory/notes.md")))


# ── links: skipped, and only here ──────────────────────────────────────────────

def test_the_resolver_skips_the_runbook(tmp_path):
    """Its references point at the platform repo, which is not this repository."""
    root = build(tmp_path, {
        "guides/install.md": "Open [`installer/entrypoint.sh`](installer/entrypoint.sh).\n",
    })
    assert check_links(root) == []


def test_the_resolver_still_catches_a_broken_link_in_brain_content(tmp_path):
    """The positive leg. Without it, a resolver that silently stopped running everywhere
    would pass the test above just as well."""
    root = build(tmp_path, {
        "skills/x/SKILL.md": "Open [`installer/entrypoint.sh`](installer/entrypoint.sh).\n",
    })
    assert codes(check_links(root)) == {"links.unresolved"}


def test_content_can_still_link_into_the_runbook(tmp_path):
    """Skipped as a SOURCE of links, still visible as a TARGET — the README points at it."""
    root = build(tmp_path, {
        "README.md": "Install with [`guides/install.md`](guides/install.md).\n",
        "guides/install.md": "# Install\n",
    })
    assert check_links(root) == []


# ── hygiene: armed, minus two ──────────────────────────────────────────────────

def test_secrets_are_still_caught_in_the_runbook():
    found = codes(scan_text(f"export TOKEN={A_TOKEN}\n", "guides/install.md",
                            ingested=False, docs=True))
    assert "hygiene.secret.github_token" in found


def test_a_real_mailbox_is_still_caught_in_the_runbook():
    """A domain outside the RFC-2606 reserved set — `example.org` and friends are
    documentation placeholders the rule deliberately allows."""
    found = codes(scan_text("mail founder@acme-corp.io\n", "guides/install.md",
                            ingested=False, docs=True))
    assert "hygiene.identity.email" in found


def test_role_guids_are_allowed_in_the_runbook():
    """Azure role-definition ids are how a deploy guide names a role precisely."""
    body = f"Assign the Foundry User role (`{A_REAL_GUID}`).\n"
    assert "hygiene.identity.guid" not in codes(
        scan_text(body, "guides/deploy.md", ingested=False, docs=True))


def test_role_guids_are_still_refused_in_brain_content():
    body = f"Assign the Foundry User role (`{A_REAL_GUID}`).\n"
    assert "hygiene.identity.guid" in codes(
        scan_text(body, "memory/notes.md", ingested=True, docs=False))


def test_microsoft_short_links_are_allowed_in_the_runbook():
    body = "Install the CLI: https://aka.ms/installazurecliwindows\n"
    assert "hygiene.scrub.akams" not in codes(
        scan_text(body, "guides/install/prereqs-windows.md", ingested=False, docs=True))


def test_microsoft_short_links_are_still_refused_in_brain_content():
    body = "Install the CLI: https://aka.ms/installazurecliwindows\n"
    assert "hygiene.scrub.akams" in codes(
        scan_text(body, "memory/notes.md", ingested=True, docs=False))


def test_the_exemptions_do_not_reach_an_undeclared_folder():
    """`docs=False` is the default, so a folder nobody classified keeps every rule."""
    body = f"See {A_REAL_GUID} and https://aka.ms/something\n"
    found = codes(scan_text(body, "notes/scratch.md", ingested=False))
    assert {"hygiene.identity.guid", "hygiene.scrub.akams"} <= found


# ── the doc-shape families never looked at it ──────────────────────────────────

def test_the_shape_families_ignore_the_runbook(tmp_path):
    """Asserted, not assumed. `layout`, `corpus` and `primitives` are path-scoped to the
    brain; this proves a runbook file cannot provoke any of them."""
    root = build(tmp_path, {
        "guides/install.md": "# Install\n\nSome prose with no frontmatter at all.\n",
    })
    shape = check_layout(root) + check_corpus(root) + check_primitives(root)
    assert [f for f in shape if f.locus and f.locus.startswith("guides/")] == []
