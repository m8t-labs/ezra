# Contributing to Ezra

Ezra is an Azure expert, and this repository is everything Ezra knows. Improving it is a
pull request — no build step, no toolchain, mostly Markdown.

## What a contribution is

Ezra's knowledge is three kinds of file, and a good contribution is usually one of them.

| | What it is | Where it lives |
|---|---|---|
| **Skill** | A repeatable play: when to run it, the steps in order, and what never to do. | `skills/<slug>/SKILL.md` |
| **Knowledge** | A durable fact or hard-won gotcha that changes how Ezra answers. | `memory/` |
| **Reference** | Background Ezra consults mid-task — a mapping table, a form field guide, a contract. | `references/` |

The agent's own definition — its character, its rules, its routing table — is
[`agent/persona.md`](agent/persona.md). Changes there are welcome and read closely: it is
what the deployed agent becomes.

Everything else (`inbox/`, `artifacts/`, `quarantine/`) is Ezra's working space at runtime.
Don't hand-edit it.

## Writing a skill

Copy the shape of an existing one — [`skills/cost-check/SKILL.md`](skills/cost-check/SKILL.md)
is a good model. Every skill needs:

- **Frontmatter:** `type`, `title`, `created`, `updated`, `tags`, `origin`.
- **Three sections:** `## When to run this`, `## The discipline`, `## Never`.
- **Two registrations:** a line in [`skills/_index.md`](skills/_index.md), and a row in the
  persona's routing table. A skill in neither is a skill Ezra will never reach.

A skill tagged `class-b` — one that touches someone's real subscription — must also link
[`references/advisor-handoff.md`](references/advisor-handoff.md), so there is always a path
to a human.

## Before you open a pull request

Run the same checks CI runs:

```bash
pip install -r ci/requirements.txt
python -m pytest ci/tests    # the checks' own tests — CI runs these first
python ci/check.py           # then the repository itself
```

Together they take a couple of seconds, and `check.py` prints the file and line of anything
it finds. Six families:

| Family | What it protects |
|---|---|
| `layout` | The repository shape the platform consumes — required files, runtime directories, no symlinks. |
| `persona` | The agent definition: its name, a declared version, the decision-policy block, and its Voice. |
| `corpus` | Skill frontmatter, the three required sections, and both registrations. |
| `primitives` | Two reference documents the platform parses as wire contracts — dropping a field breaks them silently. |
| `links` | Every internal reference resolves. Backticked paths, Markdown links and bare paths all count. |
| `hygiene` | Nothing internal, secret or personal reaches a public branch. |

Two rules deserve their reasoning stated, because a checker that surprises you is a checker
you learn to ignore:

- **Voice is pinned to a golden file.** If you change Ezra's character on purpose, update
  [`ci/golden/voice.md`](ci/golden/voice.md) in the same pull request. The point is that the
  change shows up in the diff, not that it can't happen.
- **Hygiene runs over the whole repository, not just skills.** Use `example.com` addresses
  and placeholder identifiers in anything you write. Real email addresses, real GUIDs and
  real tokens are refused — this repository is public, and some of it is written by a
  machine reading real conversations. The same rule refuses a small set of named companies
  and internal tool names; if it fires, describe the situation without naming them.

We do not lint prose style. Write like a person.

## How review works

Open a pull request against `main`. Checks run automatically; a maintainer reads it and
merges. Direct pushes to `main` are blocked for everyone, including us.

There is no changelog file — releases are described in
[GitHub Releases](https://github.com/m8t-labs/ezra/releases).

## Where Ezra's own learning goes

The Ezra hosted at [m8t.run](https://m8t.run) is designed to learn from the questions people
ask it and to commit what it learns to a separate branch of this repository — never
straight to `main`. Maintainers then curate that branch and open a pull request to promote
what belongs in the seed everyone else forks. That loop is not switched on yet;
[AGENTS.md](AGENTS.md) describes where it stands.

When it is, those promotion pull requests will run exactly the checks described above. That
is deliberate:
the hygiene rules are what stand between a real conversation and a public branch, so the
machine's contributions are held to the same bar as yours.

## If you forked this repo

Forking is how you get your own Ezra, and GitHub copies **everything** — including a few
files that belong to the canonical project rather than to yours. Worth a minute:

| File | What to do |
|---|---|
| `.github/CODEOWNERS` | Replace our handles with yours, or delete it. |
| `.github/ISSUE_TEMPLATE/config.yml`, `SUPPORT.md` | These point at the canonical project. Repoint them at your own channels if your fork takes issues. |
| `.github/dependabot.yml` | Ours. Keep it if you want the same updates, delete it if you don't. |
| `ci/` | **Keep it.** It works in your fork — see below. |

**The checks are built to survive being forked.** Rename the agent, rewrite its Voice, throw
out our skills and write your own: all of that stays green. Only two rules are switched off
outside the canonical repository — the persona's *name* (the platform pins this repo to a
specific one) and the Voice golden (that is our agent's character, not yours). Everything
that checks whether your brain actually *works* — layout, skill structure, index
registration, resolvable links, no leaked secrets — keeps running on your content. That is
the part worth having.

**Your fork is yours, and the door back is open.** What you teach your Ezra stays in your
repository under your rules. If you write a skill or work out a gotcha you are proud of,
you can offer it upstream as an ordinary pull request here — the same review as any other
contribution. There is no tooling for this yet and nothing automatic about it; it is simply
allowed, and welcome.

## Who watches this repository

[@orkeren21](https://github.com/orkeren21) and [@ilanbm](https://github.com/ilanbm) own
issues, discussions and review here. If something has been sitting unanswered, say so on
the thread — that is a bug in how we're running the repository, and we'd rather know.

## Conduct and security

By participating you agree to the [Code of Conduct](CODE_OF_CONDUCT.md). To report a
vulnerability, follow [SECURITY.md](SECURITY.md) — please don't open a public issue for one.
