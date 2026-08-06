# `install/m8t-plugin.md` — install the m8t plugin

> 🤖 **Agent runbook (component step).** Your coding agent opens this from the install flow and runs it top-to-bottom. Idempotent — safe to re-run.
>
> **Goal:** the `m8t` plugin is installed in the user's Claude Code, so they can `/carolyn ...` to talk to deployed virtual workers from any session. Idempotent.

## Audience

The coding agent the user pasted the install line into. Follow top to bottom.

## Prerequisites

- `m8t` already installed (i.e. `~/.m8t/repo-root` exists). If not: stop and tell the user to run `install.md` first.
- `az login` valid, with access to a subscription that contains a Foundry project. The plugin will auto-discover the project on first use; no manual endpoint setup is needed for the common case.
- (Optional) at least one virtual worker deployed via `m8t-architect`. Not required for install, but `/m8t:workers` will show an empty list until one exists.

## How project-endpoint resolution works

The MCP server resolves the Foundry project endpoint on first tool call, in this order:

1. `PROJECT_ENDPOINT` environment variable, if set.
2. Any `~/.m8t/foundry/*.yaml` file's `projectEndpoint` field (written by `m8t-architect` at deploy time, by this plugin's own auto-discovery, or seeded manually by the user).
3. **Auto-discovery via the Azure ARM API.** Uses the same `az login` credentials to list Cognitive Services accounts of kind `AIServices` in the user's subscription, then lists projects per account.
   - Exactly one match → picked silently, written to `~/.m8t/foundry/_auto.yaml` for future sessions.
   - Multiple matches → returns a structured error naming all candidates; the user picks one by setting `PROJECT_ENDPOINT` or editing the yaml. The next tool call retries (no session restart needed).
   - No matches → returns "no Foundry projects found", suggests using `m8t-architect` to deploy one.
   - No `az login` → returns a clear remediation.

Auto-discovery means a brand-new colleague typically installs the plugin and runs `/m8t:workers` once — the project endpoint resolves on its own.

## Per-host procedure

### Claude Code (validated)

**Pre-check (idempotent):**

macOS:

```bash
claude plugin list 2>&1 | grep -q 'm8t@m8t'
```

Windows (PowerShell):

```powershell
claude plugin list 2>&1 | Select-String -Quiet 'm8t@m8t'
```

- Match (bash: exit 0; PowerShell: prints `True`) → already installed, skip the install step.
- No match (bash: exit 1; PowerShell: prints `False`) → continue.

**Install:**

macOS:

```bash
claude plugin marketplace add m8t-labs/m8t
claude plugin install m8t@m8t
```

Windows (PowerShell):

```powershell
claude plugin marketplace add m8t-labs/m8t
claude plugin install m8t@m8t
```

(`marketplace add` is idempotent — prints "already added" if the marketplace is registered from a previous m8t install. That's a successful no-op.)

**Verify:**

macOS:

```bash
claude plugin list 2>&1 | grep 'm8t@m8t'
```

Windows (PowerShell):

```powershell
claude plugin list 2>&1 | Select-String 'm8t@m8t'
```

Expected: a line containing `m8t@m8t`.

**After install:** the user must open a new Claude Code session for the MCP server and slash commands to load. Tell them once:

> ✅ m8t installed. Open a fresh Claude Code session, then:
>
> - Try `/m8t:workers` to list deployed virtual workers.
> - Try `/carolyn ...` (or whichever worker name is in your project) to talk to one. Worker autocomplete appears after the MCP server's first poll, ~5 seconds after session start.
> - In free text: `Hey @carolyn please research these companies` also works.
> - To **manage** the deployment — team members and channel bindings — just ask in plain English ("show me everyone on the team", "bind the cmo worker to a Telegram bot"). The bundled `m8t-cli` skill drives the `m8t` CLI for you; see [m8t-cli.md](m8t-cli.md).

### Copilot CLI / VS Code Copilot Chat / Codex / Cursor / Gemini (TODO)

Not validated this phase. The MCP server, skill, and static command should transfer to Copilot CLI directly (same plugin marketplace mechanism), but the dynamically-generated `~/.claude/commands/<name>.md` files target Claude Code's commands directory specifically. Cross-host support is phase 2.

## Contributors — enable the plugin auto-bump hook

If you contribute to m8t itself (not just deploy it), enable the
pre-commit hook that auto-bumps `plugins/m8t/server/package.json` when
any file inlined into the plugin bundle changes:

```bash
git -C "$(cat ~/.m8t/repo-root)" config core.hooksPath .githooks
```

The hook patch-bumps the version and re-stages it, ensuring
`claude plugin update` actually picks up your changes. The same check
runs in CI (`.github/workflows/plugin-version-check.yml`) so missed bumps
fail the PR.

## Failure modes

- **`~/.m8t/repo-root` missing.** m8t isn't installed. Stop and ask the user to run `install.md` first.
- **`az login` expired or never run.** `/m8t:workers` (and any worker invocation) will surface ``Could not authenticate to Azure. Run `az login` first``. User runs `az login` and retries.
- **Multiple Foundry projects in the subscription.** Auto-discovery returns a structured error listing candidates. Surface the list to the user verbatim; tell them to either set `PROJECT_ENDPOINT=<chosen URL>` or write the URL to `~/.m8t/foundry/seed.yaml` as `projectEndpoint: <url>`. After the user picks, the next `/m8t:workers` call retries automatically (no session restart needed).
- **No Foundry projects in any accessible subscription.** Auto-discovery returns "no Foundry projects found". Suggest the user run `/m8t-architect` to deploy a CMO, or set `PROJECT_ENDPOINT` if they have a project endpoint URL in hand.
