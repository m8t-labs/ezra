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

- **Prompt injection in content.** Text crafted to override Ezra's instructions, exfiltrate
  what it can read, or talk it into acting outside its rules.
- **Secrets or personal data** committed to any branch, including ones the hosted Ezra
  writes to. If you find a live credential, report it privately rather than opening a pull
  request that deletes it — a deletion in public history is not a rotation.
- **Gaps in the checks.** A way to get any of the above past `python ci/check.py`.

Ezra runs on the m8t platform, which deploys into its operator's own Azure subscription.
Vulnerabilities in that platform, in a deployed gateway, or in [m8t.run](https://m8t.run)
are also welcome at <security@m8t.run> — same address, and we will route them.

## What this repository is not

Nothing here holds credentials, and nothing here executes on our infrastructure when you
open a pull request: the checks read files and run no code from the pull request itself.
