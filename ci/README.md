# `ci/` — the checks that run on every pull request

```bash
pip install -r ci/requirements.txt
python -m pytest ci/tests   # the checks' own tests
python ci/check.py          # check this repository
python ci/check.py --list   # what each rule family covers
```

Python only, two dependencies, about a second to run. There is no Node, no `package.json`
and no lockfile here, because a contributor to an agent's knowledge should not have to
install a toolchain to fix a typo in a skill.

## Layout

| | |
|---|---|
| `repo.json` | Which persona this repository provides. |
| `requirements.txt` | The two pinned dependencies. |
| `check.py` | Runs every rule family and reports findings as GitHub annotations. |
| `rules/` | One module per family. Each returns `Finding`s; none of them print or exit. |
| `golden/voice.md` | Ezra's Voice section, byte-exact. Changing the character means changing this file too. |
| `tests/` | A red case per rule, and a green case for what each rule must not fire on. |

Most rules are pure functions over a directory, so most tests build a small fixture
repository in a temp directory. Two do not, deliberately: `test_check.py` copies this
repository to check the runner's wiring against real content, and `test_routing_agrees.py`
reads `SUPPORT.md` and the issue-template chooser, because agreement between those two
files *is* the thing it tests.

## Four things worth knowing before you edit a rule

**`ci/` is excluded from the sweep it performs.** A checker's fixtures contain examples of
what it hunts for, so scanning itself would be permanently red.

**Which is why the named-entity list is hashed.** A rule the sweep cannot see must not be
the one place its own contraband is written down. `rules/entities.py` explains what that
does and does not protect — read it before adding an entry.

**A rule that fires on correct content is worse than no rule**, because people learn to
delete it. Three are deliberately absent or narrowed for exactly this reason, each recorded
as a test rather than a comment: epic/feature codes (in an Azure brain, `E2` and `D4` are VM
sizes), RFC 2606 example domains (content that teaches email setup uses them), and the
safety rules, which apply only to content the agent ingests — a security policy explaining
prompt injection has to use the words.

**`guides/` is documentation, not brain content.** It holds the install runbook a founder
pastes into a coding agent, and it is the same rule above applied a fourth time: its links
point at the platform repository on purpose, a deploy step names an Azure role by its
GUID, and an install step cites Microsoft's own `aka.ms` link. So the resolver skips it and
those two hygiene rules stand down — while secrets, mailboxes, named entities and internal
strings stay armed, because a token pasted into a runbook is still a leaked token. The
folder is named in `rules/tree.py`, one entry, at the root only: a prefix would let the
next folder inherit the exemptions without anyone deciding to grant them.

## Reusing this in another agent repository

Copy `ci/`, then change four things:

1. `repo.json` — the persona slug.
2. `golden/voice.md` — regenerate from that repository's `agent/persona.md`.
3. `rules/hygiene.py` — `_OWN_DOMAIN`, if the maintainers' email domain differs.
4. `tests/test_routing_agrees.py` — it names this repository's support mailbox, or drop it
   if that repository has no `SUPPORT.md`.
5. `rules/tree.py` — `DOCS_ROOTS`, which is empty for a repository that carries no product
   runbooks. Leaving `guides` in it there would grant two hygiene exemptions to a folder
   that does not exist, waiting for someone to create one.

Every other rule reads the agent-repo layout, which is the same everywhere. The digests in
`rules/entities.py` carry no repository-specific information and can be copied as they are.
