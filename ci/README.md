# `ci/` — the checks that run on every pull request

```bash
pip install PyYAML pytest
python ci/check.py          # check this repository
python ci/check.py --list   # what each rule family covers
python -m pytest ci/tests   # the checks' own tests
```

Python only, two dependencies, about a second to run. There is no Node, no `package.json`
and no lockfile here, because a contributor to an agent's knowledge should not have to
install a toolchain to fix a typo in a skill.

## Layout

| | |
|---|---|
| `repo.json` | The only repository-specific value: which persona this repo provides. |
| `check.py` | Runs every rule family and reports findings as GitHub annotations. |
| `rules/` | One module per family. Each returns `Finding`s; none of them print or exit. |
| `golden/voice.md` | Ezra's Voice section, byte-exact. Changing the character means changing this file too. |
| `tests/` | A red case per rule and a green case for what each rule must not fire on. |

The rules are pure functions over a directory, which is why the tests build small fixture
repositories in a temp directory rather than mutating this one.

## Two things worth knowing before you edit a rule

**`ci/` is excluded from the sweep it performs.** A checker's fixtures necessarily contain
the strings it hunts for — the internal-string list would match its own source — so
scanning itself would be permanently red. Rules that must see a file therefore cannot live
in `ci/`.

**A rule that fires on correct content is worse than no rule**, because people learn to
delete it. Two rules are deliberately absent for exactly this reason, and both are recorded
as tests rather than comments: epic/feature codes (in an Azure brain, `E2` and `D4` are VM
sizes) and RFC 2606 example domains (content that teaches email setup uses them).

## Reusing this in another agent repository

Copy `ci/`, change `repo.json`, and regenerate `golden/voice.md` from that repo's persona.
Every other rule reads the agent-repo layout, which is the same everywhere.
