# `install/m8t-cli.md` — the `m8t` CLI

> 🤖 **Agent runbook (component step).** Your coding agent opens this from the install flow and runs it top-to-bottom. Idempotent — safe to re-run.
>
> **Goal:** the `m8t` CLI binary is on PATH — `guides/bootstrap.md` and day-to-day platform management (`team`, `bind`, `doctor`, `coder deploy`) all need it. Further down: the optional `m8t-cli` *skill*, which teaches your coding agent to drive the CLI conversationally — "add Ilan to the team", "bind the cmo worker to a Telegram bot."

## The `m8t` CLI binary

Install it from npm (any OS with Node 20+).

macOS / Linux:

```bash
npm install -g @m8t-stack/cli      # or: brew install m8t-labs/tap/m8t  ·  scoop bucket add m8t https://github.com/m8t-labs/scoop-bucket; scoop install m8t
m8t version
```

Windows (PowerShell):

```powershell
$env:Path = [System.Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [System.Environment]::GetEnvironmentVariable('Path','User'); npm install -g @m8t-stack/cli
$env:Path = [System.Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [System.Environment]::GetEnvironmentVariable('Path','User'); m8t version
```

The first refresh exposes `npm` when Node was installed earlier in the same long-lived
agent session. The second exposes npm's global binary directory immediately after the
install. A child PowerShell process inherits stale PATH, so merely opening a nested shell
does not fix either handoff.

If `m8t` still isn't on PATH, open a brand-new terminal. For contributors / unreleased
changes, it can be built as a tarball from your clone via `~/.m8t/repo-root` instead of
the published npm package. See `apps/cli/README.md` for all
options.

The CLI is also what installs and updates the **desktop companions** — the mate
windows that sit at the edge of your screen. They are their own software with their
own version, published separately and named by each platform release, so the CLI fetches
one rather than carrying it. See [`companion.md`](companion.md).

### Prerequisites for using the CLI

`m8t version` works with no further setup. Everything else — `m8t bootstrap ...`, and day-to-day management (`m8t team`, `m8t bind`, `m8t doctor`) — needs `az login` first; team/binding management additionally needs a deployed m8t gateway, which the CLI discovers via Azure Resource Manager.

## (Optional) The `m8t-cli` skill — manage your deployment conversationally

`m8t-cli` teaches your coding agent to drive the `m8t` CLI for you — "add Ilan to the team", "bind the cmo worker to a Telegram bot" — instead of typing commands yourself. It lives at `plugins/m8t/skills/m8t-cli/SKILL.md` inside the `m8t` plugin. If you've installed that plugin (see [`m8t-plugin.md`](m8t-plugin.md)) to talk to your virtual workers, **you already have this skill** — there is nothing extra to install. If not, install the plugin:

### Claude Code (validated)

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

(`marketplace add` is idempotent — "already added" is a successful no-op.) Then **open a fresh Claude Code session** so the skill loads.

**Confirm it's working:** ask *"show me everyone on the team."* The agent should reach for `m8t team list`. If `m8t` isn't on your PATH, the agent will offer to install it — that's expected on a fresh machine.

### Copilot CLI / VS Code / Codex / Cursor / Gemini (phase 2)

Not validated this phase — same status as the rest of the `m8t` plugin (see [m8t-plugin.md](m8t-plugin.md)). The skill is a plain `SKILL.md` and should transfer once the plugin's cross-host story lands.
