# Install — m8t

> 🤖 **Agent runbook.** Paste this into your coding agent — it executes the steps top-to-bottom and pauses only for sign-ins, `sudo`, or genuine choices. Re-runnable after a `git pull` — see "Re-running this file" below.
>
> Two required steps get you a **live platform in your own Azure subscription**: local prereqs, then a cloud install that runs unattended. Local tooling for your coding agent (Azure MCP servers and slash-commands for talking to your deployed workers) is optional and comes last — add it now, or come back for it anytime by re-pasting this file.

## How to read this file

You're an agent. Walk the steps below in order. For each step:

1. Open the linked sub-file (`install/<x>.md`, or `bootstrap.md` for Step 2).
2. Run its pre-checks. If state already matches, log "no-op" and continue.
3. Run its mutations. Pause and tell the user only when:
   - A browser-based or interactive flow needs them (e.g. `az login`).
   - A sudo command runs.
   - Multiple valid choices exist and the right one is non-obvious (e.g. multiple Azure subscriptions or Foundry projects).
   - Something fails in a way that needs human judgment.
4. Run the verification at the end of the sub-file.

This matches the interaction style established in `install/prereqs-macos.md` (lifted from the existing Azure CLI install draft). Steps 1–2 are host-agnostic — no coding-agent-specific branching until the optional local-tooling steps below, which fork per host (Claude Code, GitHub Copilot CLI, VS Code Copilot Chat) where a sub-file says so.

## Steps

### 0. Tell the user what this costs, then STOP and wait

Before anything else, say this to the user in your own words — but cover every point:

> You are about to install the m8t platform.
>
> - It installs into **your** Azure subscription and **your** GitHub account or organization.
> - The Azure resources it creates **bill to your Azure account — this uses your budget**.
> - With your workers installed, you can ask Ezra what you're spending at any time, and you can turn on a cost report by email every two weeks.
> - You can remove it later — see `guides/uninstall.md`.
>
> **Continue?**

Then **wait for their answer**. Do not take any install or cloud action until the user has
answered — this includes installing prerequisites and running `az login`. **This is a stop, not a
notification.** If they decline, stop here and do nothing else.

### 1. Prereqs (git + Azure CLI + Node + the m8t CLI)

Detect the user's OS, then open and follow the matching prereqs file:

- If the agent runtime already identifies the host as Windows and provides a
  PowerShell tool, use the Windows path directly — do not spawn a shell merely
  to rediscover metadata the runtime already supplied.
- `uname -s` returns `Darwin` → macOS → open `install/prereqs-macos.md`.
- `$env:OS` equals `Windows_NT` (PowerShell), or `%OS%` equals `Windows_NT` (cmd), or `uname -s` starts with `MINGW` / `MSYS` / `CYGWIN` (Git Bash on Windows) → Windows → open `install/prereqs-windows.md`.
- Anything else → stop and ask the user.

End state: `az --version` works, `az account show` returns an active subscription, the active tenant matches what the user wants for Foundry, and `node --version` is ≥ 20. (On Windows, use the native PowerShell command blocks documented in `prereqs-windows.md`.)

Then install the `m8t` CLI — see [`install/m8t-cli.md`](install/m8t-cli.md) (npm is the default; brew/scoop and a contributor fallback are documented there). Verify with `m8t version`.

You don't need GitHub CLI (`gh`) here — Step 2 installs it later, and only if the user opts into brain-backed workers on a GitHub org.

With the CLI installed, run `m8t prereqs` to check the target subscription can actually complete the install (resource providers, model quota, your Azure and directory rights). It changes nothing; `m8t prereqs --fix` registers anything missing. Step 2's preflight runs the same checks, so this is an early look rather than an extra step. Full list: [`prerequisites.md`](prerequisites.md).

### 2. Deploy your platform

Open and follow [`bootstrap.md`](bootstrap.md) end-to-end. It confirms the one `az login` from Step 1, runs a loud admin-credentials preflight, then offloads the whole platform install — Foundry from zero, the gateway, the infra — to an ephemeral cloud installer and watches it to completion.

`bootstrap.md` also works as a standalone paste (its own Steps 1–2 repeat prereqs + the `m8t` CLI + `az login`), so arriving here from this file means those checks just confirm-and-continue in seconds — nothing to redo, nothing skipped.

Its final step also puts **your mates on the desktop** — a small always-on-top window per mate, each with a one-message composer. The CLI fetches the build your platform release names, checks it, and installs it; nothing here needs a decision. macOS and Windows only. To check on them, update them, or remove them later: [`install/companion.md`](install/companion.md).

Relay `bootstrap.md`'s own **"✅ Your m8t platform is live"** message when it gets there. That's the platform installed — everything below is optional.

---

**Everything from here is optional local tooling for your coding agent** — Azure-capable MCP servers and the ability to talk to your deployed workers from inside your agent sessions. None of it gates the platform: add it now, or skip to [Done](#done) and come back later by re-pasting this file. (Want to deploy more workers conversationally? That's the `m8t-architect` skill — an opt-in render documented in [`workers.md`](workers.md), not part of this install.)

### 3. (Optional) Install `microsoft/azure-skills`

Open and follow `install/azure-skills.md`. End state: the `foundry` MCP tool (and the rest of the Azure MCP namespace) is reachable from the host.

### 4. (Optional) Install the Microsoft Learn MCP

Open and follow `install/mslearn-mcp.md`. End state: the `microsoft-learn` MCP is registered in the host and reachable.

### 5. (Optional) Install the m8t plugin

If the user wants to talk to deployed virtual workers from inside their coding-agent sessions (e.g. `/carolyn please research these companies`), open and follow `install/m8t-plugin.md`. Needs `~/.m8t/repo-root` to exist first — `m8t bootstrap status --watch` wrote it when Step 2's install reached `done`. (Skipped Step 2 because you're joining a teammate's deployment? Write it yourself: a single line containing this clone's absolute path, at `~/.m8t/repo-root`.) End state: the `m8t` plugin is installed in Claude Code; `/m8t:workers` lists deployed workers; per-worker slash commands like `/carolyn` appear in `/` autocomplete after a fresh session starts and the MCP server's first poll completes.

If the user hasn't deployed any virtual workers yet, this step is purely setup — the plugin will show an empty list until a worker exists. The plugin auto-discovers the Foundry project endpoint on first use, so no manual configuration is needed in the common case.

The plugin also bundles the `m8t-cli` skill, which drives the `m8t` CLI for team / channel-binding management and for deploying the hosted coding agent (`m8t coder deploy`). You already have the CLI binary from Step 1; see [`install/m8t-cli.md`](install/m8t-cli.md) if you need it again.

## Done

Once Step 2 completes, the platform is live — relay `bootstrap.md`'s own done message as described above.

If the user also ran any of the optional Steps 3–5 and they all verify, also tell the user:

> **✅ Local tooling installed.**
>
> **Next step: open a brand new chat/session in your coding agent.** New MCP servers and plugins won't appear in your current session — they only load on fresh start.
>
> Then try:
>
> - `/m8t:workers` — lists your deployed workers; talk to one with `/<worker>` (e.g. `/ezra`).
> - Ask your agent an Azure question — if you installed them (Steps 3–4), the Azure and Microsoft Learn MCP servers ground it in your subscription and the official docs.

## Joining a platform someone else installed

You do not need to run any of this. Ask whoever installed it for the webapp URL, open it, and sign in with
your work account — the platform reaches Azure with its own identity, so **using it in the browser needs no
Azure permissions of your own**.

Only if you also want the `m8t` CLI or the coding-agent plugin on your machine:

1. Do Step 1 above (prereqs + the `m8t` CLI), then `az login`.
2. Ask whoever administers the Azure subscription to run `m8t prereqs --fix --for you@example.com` once.
3. Run `m8t prereqs` to confirm, then `printf %s "<path-to-this-clone>" > ~/.m8t/repo-root` and continue
   from Step 5.

See [`prerequisites.md`](prerequisites.md) for what those steps grant and why they are needed.

## Re-running this file

Re-running `install.md` after a `git pull` is the supported update path. Most of it is idempotent:

- Prereqs + the `m8t` CLI: no-ops if already satisfied.
- Deploying the platform: `m8t bootstrap launch` always runs the from-zero installer, so it's safe to
  re-run only against an **empty** target — the steps converge and nothing is duplicated. If the
  target resource group already holds resources (including an already-live platform), `launch` stops
  instead of re-entering it — see `bootstrap.md`'s own "Re-running" section for the consent flag that
  continues deliberately. To update an already-live platform, use `m8t platform update` instead —
  it converges the running gateway, hosted agents, personas, and infra to a release manifest.
  `m8t bootstrap status` and `reap` remain safe to re-run regardless.
- `microsoft/azure-skills`: no-op if already installed.
- mslearn-mcp: no-op if the server is already registered; adds it otherwise.
- m8t plugin (if installed): `claude plugin update` is a no-op when the plugin version is unchanged; bump + reinstall to force-refresh (see `install/m8t-plugin.md`).
- m8t CLI (if installed): `npm install -g @m8t-stack/cli@latest` to update to the published release; contributors can rebuild + repack from the clone instead (see `install/m8t-cli.md`).
- Desktop companions: they have their own version and their own release. `m8t companion status` says whether a newer one is out; `m8t companion install` takes it, and is a no-op when what is installed already matches (see `install/companion.md`).

Reversal: [`uninstall.md`](uninstall.md) walks through removing both the local extras and (optionally) the deployed platform. There are no shell-config edits to undo.
