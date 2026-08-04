# Ezra

**An Azure expert that does the work, not the introductions.**

Ask in plain language. Ezra diagnoses before prescribing, says plainly what it doesn't
know, and names the blast radius and the rollback before anything changes.

This repository **is** Ezra: the agent's definition in [`agent/persona.md`](agent/persona.md),
and the knowledge it works from — [memories](memory/MEMORY.md), [skills](skills/_index.md),
and [references](references/) — laid out as a working second brain.

---

## What Ezra does

| | |
|---|---|
| **Grounds before answering** | Reads Microsoft Learn through MCP and quotes the page, rather than recalling an API that changed last quarter. |
| **Reads your subscription** | Cost, quota, role assignments, what is actually deployed and what it is costing you. |
| **Files real requests** | Quota increases, support routing — with the proof written back here. |
| **Makes changes, on your say-so** | States the exact effect in plain English — *"this removes Bob's Contributor role on the subscription; he'd lose write access"* — and waits for your yes. Never a surprise. |
| **Remembers** | Decisions and hard-won gotchas land in this repo, so the next conversation starts where the last one ended. |

Fourteen skills, from `quota-diagnose` to `hipaa-baa` to `cost-check`. Browse
[`skills/_index.md`](skills/_index.md) — they are plain Markdown, and improving one is a
pull request.

## Running Ezra

Ezra runs on [m8t](https://m8t.run), which deploys into **your own Azure
subscription** — your tenant, your data, your bill, no middleman holding your credentials.

```
Fork this repo  →  install m8t  →  your Ezra runs on your fork
```

Your fork becomes your Ezra's brain: it reads from it at the start of a task and writes
back what it learns. What you teach your Ezra stays yours. What you send upstream makes
everyone's better.

## Contributing

An agent is only as good as what it knows, and everything it knows is text in this repo:

| Directory | What belongs there |
|---|---|
| [`skills/`](skills/_index.md) | Repeatable plays — when to run it, what to check, what to hand back. |
| [`memory/`](memory/MEMORY.md) | Durable facts and gotchas that cost someone an afternoon. |
| [`references/`](references/) | Stable material worth citing. |
| [`agent/persona.md`](agent/persona.md) | Who Ezra is, and how Ezra behaves. |

If Ezra got something wrong for you, the correction belongs here. That is the single most
useful pull request this repo can receive.

[CONTRIBUTING.md](CONTRIBUTING.md) has the shape of a good one, and
[`python ci/check.py`](ci/README.md) runs the same checks CI does in about a second.

## License

MIT — see [LICENSE](LICENSE) and [NOTICE](NOTICE).

see `memory/does-not-exist.md`
