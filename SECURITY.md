# Security policy

## Reporting a vulnerability

Please report security issues privately. Do not open a public issue.

- **Preferred:** [Report a vulnerability](https://github.com/m8t-labs/ezra/security/advisories/new)
  through GitHub's private reporting, which keeps the discussion attached to this repository.
- **Or email:** <security@m8t.run>

Tell us what you found, how to reproduce it, and what an attacker could do with it. We aim
to acknowledge within three working days and to keep you updated until it is resolved. If
you'd like credit in the advisory, say so and we will name you.

## What is in scope

This repository is an agent's definition and its knowledge — Markdown, plus the checks in
`ci/`. The things worth reporting here are:

- **Prompt injection in content.** Text crafted to override Ezra's instructions, read out
  what it should not, or talk it into acting outside its rules.
- **Secrets or personal data** committed to any branch, including ones the hosted Ezra
  writes to. If you find a live credential, report it privately rather than opening a pull
  request that deletes it — a deletion in public history is not a rotation.
- **Gaps in the checks.** A way to get either of the above past `python ci/check.py`.

One thing worth knowing before you spend time on that last one: the injection patterns in
`ci/rules/hygiene.py` are a **tripwire, not a boundary**. They catch common phrasings and
careless copy-paste. Anyone deliberately rewording will get past them, and that is expected
— content is defended by the agent's own rules and by human review, not by that list. A
novel rephrasing is not by itself a finding; a way to smuggle a *secret* or a real person's
details past the sweep is.

Ezra runs on the m8t platform, which deploys into its operator's own Azure subscription.
Vulnerabilities in that platform, in a deployed gateway, or in [m8t.run](https://m8t.run)
are also welcome at <security@m8t.run> — same address, and we will route them.

## How the checks run

Nothing in this repository holds credentials. A pull request's checks run on a
GitHub-hosted runner with a read-only token and no repository secrets, so there is nothing
there to steal.

They do **execute the checker as it exists in the pull request** — `ci/` is Python, and
`python ci/check.py` runs that code. A change under `ci/` is therefore reviewed as code,
not as content.
