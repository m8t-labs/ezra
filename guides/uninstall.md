# Uninstall — m8t

> 🤖 **Agent runbook.** Paste this into your coding agent — it walks these removal steps top-to-bottom, asks before each removal, and never removes anything silently. Re-runnable anytime.

## How to read this file

You're an agent. Walk the steps below in order. For each step:

1. Open the linked sub-file under `uninstall/`.
2. Run its pre-check (does the thing exist?). If not, log "no-op" and continue to the next step.
3. If it exists, ask the user the prompt described in that file. **Defaults are NO across every step** — the user explicitly opts in to what they want removed. Wait for an explicit yes/no answer; never assume the default. It's entirely reasonable for a user to say *"yes — remove the m8t skills, but keep everything else"* — these prompts are independent.
4. Run the removal only if the user says yes.
5. Run the verification at the end of the sub-file.
6. **If the user says "no" at any step, log it and continue to the next step.** Each step is independent — a "no" on one removal does not abort the whole flow. The user can re-run the orchestrator anytime to revisit "no" answers.

This mirrors the interaction style of `install.md` but in reverse — and biased toward preservation.

## First: do you also want to remove the cloud platform?

The steps below remove only **local** artifacts (skills, the desktop companions, the `~/.m8t/` folder,
MCPs, the CLI).
If you also deployed a platform into Azure and want it gone, pick the matching cloud teardown first —
the two have **opposite** semantics, so choosing wrong is a footgun:

- **Installed via [`bootstrap.md`](bootstrap.md)** — the platform is in its **own dedicated resource
  group** (Foundry + gateway + workers together). Use
  [`uninstall/bootstrap-teardown.md`](uninstall/bootstrap-teardown.md): it deletes the whole RG,
  purges the Foundry account, and removes the gateway's subscription-scoped roles.
- **Deployed the comms infra into an existing Foundry RG** — use the **tag-scoped**
  [`uninstall/azure-infra.md`](uninstall/azure-infra.md): it deletes only `m8t`-tagged
  resources and **never** touches your RG or Foundry agents.

Keeping the cloud platform? Skip straight to the local steps below.

## Steps (safest first)

### 1. Remove m8t skills

Open and follow `uninstall/m8t.md`. Removes `~/.claude/skills/m8t-*/` directories. Cheap, no shared dependencies, easy to re-add via `install.md`. Default: no.

### 1b. Remove the desktop companions

Ask: *"Remove your mates from your desktop?"* If yes, run `m8t companion uninstall`. It removes
the app, the start-at-login registration, and the records under `~/.m8t/companion/` — and only those;
it refuses to remove a target it did not install. Nothing in the cloud is touched, and re-adding them
is `m8t companion install`. If `m8t companion status` already reports `not-installed`, log "no-op"
and continue. Default: no.

Do this before step 2 — that step offers to remove `~/.m8t/`, which is where the companions' records
live, and removing the folder first leaves the app on the desktop with nothing pointing at it.

### 2. Remove the `~/.m8t/` operational folder

Open and follow `uninstall/m8t-folder.md`. Handles `~/.m8t/` including `founder.yaml`, `repo-root`, and `foundry/<agent-name>.yaml` files (the only local record of what's deployed in your Foundry project — the live agents themselves are unaffected). Default: no for the folder, **no default** on the `foundry/` sub-prompt — the user must explicitly answer.

### 3. Remove the Microsoft Learn MCP

Open and follow `uninstall/mslearn-mcp.md`. Removes the `microsoft-learn` MCP server registration. Cheap, easy to re-add. Default: no.

### 4. Remove the `microsoft/azure-skills` plugin

Open and follow `uninstall/azure-skills.md`. **Disclaimer to surface to the user before asking:** *"This also removes the Azure MCP server (the `foundry` and other Azure-namespace tools) — anything in your environment that depends on those tools will stop working until you re-install."* Default: no.

### 5. Remove the Azure CLI

Open and follow `uninstall/az-cli.md`. **Disclaimer to surface to the user before asking:** *"`az` is the foundational Azure CLI. If you use Azure for anything outside this project — other coding agents, scripts, manual administration — you almost certainly want to keep it."* Default: **no.**

## Done

When every step completes, tell the user:

> m8t removal complete. Anything you said "no" to is still in place; you can re-run this file anytime to remove what's left.
