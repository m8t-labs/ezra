# `install/azure-skills.md` — install the `microsoft/azure-skills` plugin

> 🤖 **Agent runbook (component step).** Your coding agent opens this from the install flow and runs it top-to-bottom. Idempotent — safe to re-run.
>
> **Goal:** the `foundry` MCP tool (and the rest of the Azure MCP namespace) is reachable from the agent's host. Idempotent — re-running this is a no-op when the plugin is already installed.

## Why this is a separate file

`microsoft/azure-skills` is an upstream plugin maintained by Microsoft. m8t depends on it but does not vendor or fork it. This file is the single per-host install procedure; `install.md` calls into it.

## Per-host procedure

Pick the section matching your host.

---

### Claude Code (validated)

The plugin is shipped via Microsoft's marketplace.

**Pre-check (must be idempotent — do this first):**

macOS:

```bash
claude plugin list 2>&1 | grep -q 'azure@azure-skills'
```

Windows (PowerShell):

```powershell
claude plugin list 2>&1 | Select-String -Quiet 'azure@azure-skills'
```

- Match (bash: exit 0; PowerShell: prints `True`) → already installed; skip the install steps below.
- No match (bash: exit 1; PowerShell: prints `False`) → continue.

(Note: `claude plugin list` formats each plugin like `❯ azure@azure-skills`. Match the `<name>@<marketplace>` pair, not the bare name.)

**Install:**

macOS:

```bash
claude plugin marketplace add microsoft/azure-skills
claude plugin install azure@azure-skills
```

Windows (PowerShell):

```powershell
claude plugin marketplace add microsoft/azure-skills
claude plugin install azure@azure-skills
```

The `marketplace add` command may print "already added" if the marketplace is registered from a previous run — that's a successful no-op.

**Verify:**

macOS:

```bash
claude plugin list 2>&1 | grep 'azure@azure-skills'
```

Windows (PowerShell):

```powershell
claude plugin list 2>&1 | Select-String 'azure@azure-skills'
```

Expected: a line showing `❯ azure@azure-skills`.

After install, the `foundry` MCP tool becomes available in Claude Code sessions started after the install (existing sessions need a restart). The Architect skill will use it at runtime.

---

### GitHub Copilot CLI

Copilot CLI shares the same plugin marketplace mechanism Microsoft uses for Claude Code (per the [microsoft/azure-skills](https://github.com/microsoft/azure-skills) README). The slash-command shape is identical.

**Pre-check (idempotent):**

```text
/plugin list
```

Filter the output for a line containing `azure@azure-skills`. If present → already installed; skip the install step.

**Install:**

```text
/plugin marketplace add microsoft/azure-skills
/plugin install azure@azure-skills
```

The `marketplace add` command prints "already added" on re-run — that's a successful no-op.

**Verify:**

```text
/plugin list
```

Expected: a line showing `azure@azure-skills`.

After install, the `foundry` MCP tool (and the rest of the Azure MCP namespace) becomes available in Copilot CLI sessions started after the install (existing sessions need a restart). The Architect skill will use it at runtime.

---

### VS Code Copilot Chat

VS Code uses an extension-based mechanism instead of the plugin marketplace. The Azure MCP server extension is published by Microsoft on the VS Code Marketplace.

**Important — don't open new VS Code windows during install.** Only run `code` with the `--install-extension`, `--list-extensions`, `--uninstall-extension`, or `--add-mcp` flags. Never run `code` with a folder argument (`code .`, `code <path>`) during install — that opens new windows and confuses the install agent.

**Windows note:** run commands directly in the current PowerShell session per the shell convention in `install/prereqs-windows.md`.

**0. Resolve the `code` CLI (runtime probe).**

The agent invokes VS Code's CLI to install extensions. If `code` is on PATH, use it directly. Otherwise:

- macOS: `/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code`
- Windows (user-scope install): `%LocalAppData%\Programs\Microsoft VS Code\bin\code.cmd`
- Windows (machine-scope install): `C:\Program Files\Microsoft VS Code\bin\code.cmd`

Use whichever exists. On Windows, if both the user-scope and machine-scope paths exist, prefer the user-scope path (most VS Code installs are user-scope by default).

**If `code` is not on PATH and none of the fallback paths exist**: VS Code is not installed (or installed to a non-standard location). Stop and ask the user to install VS Code (or to provide the path to their `code` CLI). This is one of the unavoidable interaction boundaries.

If `code` is not on PATH on macOS but a fallback path works, after install tell the user once: *"Using VS Code's bundled `code` CLI directly. If you'd like `code` on your PATH for future use, open VS Code, run the command palette (⇧⌘P), and pick 'Shell Command: Install code command in PATH'."* Informational, not a blocker.

**Pre-check (idempotent):**

macOS:

```bash
code --list-extensions | grep -i 'ms-azuretools.vscode-azure-mcp-server'
```

Windows (PowerShell):

```powershell
code --list-extensions | Select-String -SimpleMatch 'ms-azuretools.vscode-azure-mcp-server'
```

If output contains the extension → already installed; skip install.

**Install:**

```bash
code --install-extension ms-azuretools.vscode-azure-mcp-server
```

`--install-extension` is a no-op if the extension is already installed at the latest version.

This also pulls in dependency extensions (observed: `ms-azuretools.vscode-azureresourcegroups`, `ms-azuretools.vscode-azure-github-copilot`) — expected, not an error, so don't be thrown if a `--list-extensions` diff shows more than the one extension you asked for.

**If the install fails with "extension not found":** Microsoft may have renamed it. Check the live marketplace at <https://marketplace.visualstudio.com/search?term=azure%20mcp&target=VSCode&category=All%20categories&sortBy=Relevance>, find the Microsoft-published Azure MCP entry, and use that `publisher.id` instead. Report the new ID in your success message so the next maintainer can codify it.

**Verify:**

macOS:

```bash
code --list-extensions | grep -i 'ms-azuretools.vscode-azure-mcp-server'
```

Windows (PowerShell):

```powershell
code --list-extensions | Select-String -SimpleMatch 'ms-azuretools.vscode-azure-mcp-server'
```

Expected: a line containing the extension ID.

After install, the Azure MCP servers (including `foundry`) appear in VS Code Copilot Chat's MCP server list on the next reload (`Developer: Reload Window` from the command palette).

---

### Codex CLI (TODO — not validated this phase)

Conceptual path (validate before running):

1. `git clone https://github.com/microsoft/azure-skills` somewhere stable (e.g., `~/.local/share/azure-skills`).
2. Inspect `azure-skills/.mcp.json` (or equivalent) for the Azure MCP server configuration; copy that block into Codex's MCP config (location TBD; varies by Codex version).
3. Copy `azure-skills/skills/` (or symlink) into Codex's user-scoped skills directory (location TBD).
4. Restart Codex; verify the `foundry` tool is reachable.

Not validated. Out of scope for Phase 1.

---

### Cursor (TODO — not validated this phase)

Conceptually similar to Codex (clone, copy MCP config, copy skills dir, restart). Cursor's MCP and skills directories require verification on a real install. Out of scope for Phase 1.

---

### Gemini CLI (TODO — not validated this phase)

Same shape. Specifics depend on Gemini CLI's plugin / skill model. Out of scope for Phase 1.

---

## Failure modes worth surfacing to the user

- **Plugin install requires interactive auth or sudo.** Pause and tell the user before running.
- **`claude` command not found.** Claude Code isn't installed on PATH. Stop and ask the user to install Claude Code first; this file can't bootstrap that.
- **`microsoft/azure-skills` marketplace add fails with `cross-marketplace`.** This shouldn't happen for the standalone install (we are not depending on it from another plugin); if it does, capture the full error and ask the user.
