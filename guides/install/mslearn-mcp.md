# `install/mslearn-mcp.md` — install the Microsoft Learn MCP

> 🤖 **Agent runbook (component step).** Your coding agent opens this from the install flow and runs it top-to-bottom. Idempotent — safe to re-run.
>
> **Goal:** the `microsoft-learn` MCP is registered in the host and reachable. Idempotent — re-running this is a no-op when the server is already registered.

## Why this is a separate file

The Microsoft Learn MCP is a public remote MCP server (`https://learn.microsoft.com/api/mcp`) that gives the agent access to up-to-date Microsoft documentation and code samples. The MFS Azure Advisor uses it for "let me check the docs" lookups. m8t depends on it but does not vendor or host it. This file is the single per-host install procedure; `install.md` calls into it.

## Per-host procedure

Pick the section matching your host.

---

### Claude Code (validated)

The server is added via `claude mcp add --transport http`.

**Pre-check (must be idempotent — do this first):**

macOS:

```bash
claude mcp list 2>&1 | grep -q '^microsoft-learn:'
```

Windows (PowerShell):

```powershell
claude mcp list 2>&1 | Select-String -Quiet '^microsoft-learn:'
```

- Match (bash: exit 0; PowerShell: prints `True`) → already installed; skip the install steps below.
- No match (bash: exit 1; PowerShell: prints `False`) → continue.

(Note: `claude mcp list` formats user-scope servers like `microsoft-learn: https://learn.microsoft.com/api/mcp (HTTP) - <status>`. The `(HTTP)` segment is the transport label injected by Claude Code. Match the bare name at line-start to avoid false positives from in-line text — the regex stays robust against the transport label.)

**Install:**

macOS:

```bash
claude mcp add --scope user --transport http microsoft-learn https://learn.microsoft.com/api/mcp
```

Windows (PowerShell):

```powershell
claude mcp add --scope user --transport http microsoft-learn https://learn.microsoft.com/api/mcp
```

`--scope user` makes the server available across all projects on this machine (not scoped to one cwd). The endpoint is the public anonymous MCP; no auth or token needed.

**Verify:**

macOS:

```bash
claude mcp list 2>&1 | grep '^microsoft-learn:'
```

Windows (PowerShell):

```powershell
claude mcp list 2>&1 | Select-String '^microsoft-learn:'
```

Expected: a line showing `microsoft-learn: https://learn.microsoft.com/api/mcp (HTTP) - <status>`. Status `Connected` (✓) is the expected steady state. A transient `Needs authentication` (!) right after install can clear on the next session restart; if it persists, see Failure modes below.

After install, the `microsoft-learn` MCP becomes available in Claude Code sessions started after the install (existing sessions need a restart).

---

### GitHub Copilot CLI

Copilot CLI registers MCP servers via an `/mcp` slash-command (exact syntax is resolved by a runtime probe — see Step 0).

**Step 0 — Resolve `/mcp` add syntax (runtime probe).**

In an interactive Copilot CLI session, run `/help` or `/mcp` to see the live subcommand list. As of this writing, the expected verb is `/mcp add`, but the exact flag set (e.g. `--transport http`, `--scope user`) may differ. **Use the live `/help` output as the source of truth.** Report the resolved syntax in your success message.

**Pre-check (idempotent):**

```text
/mcp list
```

Filter for a line starting with `microsoft-learn:` (or whatever bare-name format Copilot CLI uses). If present → already installed; skip the install step.

**Install (illustrative — adapt to the syntax `/help` revealed):**

```text
/mcp add microsoft-learn --transport http --url https://learn.microsoft.com/api/mcp
```

The endpoint is the public anonymous Microsoft Learn MCP; no auth or token needed.

**Verify:**

```text
/mcp list
```

Expected: a line showing `microsoft-learn` and the URL.

After install, the `microsoft-learn` MCP becomes available — existing Copilot CLI sessions need a restart to see it.

---

### VS Code Copilot Chat

VS Code Copilot Chat registers MCP servers via a JSON config file at `~/Library/Application Support/Code/User/mcp.json` (macOS) or `%APPDATA%\Code\User\mcp.json` (Windows). On macOS we use `code --add-mcp` for registration; on Windows we write the file directly to avoid shell JSON-quoting fragility.

**Important — don't open new VS Code windows during install.** Only run `code` with the `--install-extension`, `--list-extensions`, `--uninstall-extension`, or `--add-mcp` flags. Never run `code` with a folder argument (`code .`, `code <path>`) during install — that opens new windows and confuses the install agent.

**Windows note:** run commands directly in the current PowerShell session per the shell convention in `install/prereqs-windows.md`.

**0. Resolve the `code` CLI (runtime probe).**

Same probe as `install/azure-skills.md` VS Code Copilot Chat section: prefer `code` on PATH; fall back to absolute paths (`/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code` on macOS, `%LocalAppData%\Programs\Microsoft VS Code\bin\code.cmd` or `C:\Program Files\Microsoft VS Code\bin\code.cmd` on Windows). On Windows, if both paths exist, prefer user-scope. If none exist, stop and ask the user — VS Code isn't installed.

**Pre-check (idempotent):**

Read VS Code's user MCP config and check for an existing `microsoft-learn` entry.

- macOS: `~/Library/Application Support/Code/User/mcp.json`
- Windows: `%APPDATA%\Code\User\mcp.json`

If the file exists and contains a `servers.microsoft-learn` entry where `servers.microsoft-learn.type` matches `type` = `"http"` AND `url` = `https://learn.microsoft.com/api/mcp` → no-op; skip install.

If it exists with a `microsoft-learn` entry pointing somewhere ELSE (different URL or different transport type) → **STOP and ask the user.** Likely cause: a prior install with a non-default endpoint or transport. Don't silently overwrite.

If absent → continue.

**Install (macOS):**

```bash
code --add-mcp '{"name":"microsoft-learn","type":"http","url":"https://learn.microsoft.com/api/mcp"}'
```

Bash single-quotes preserve the double-quoted JSON literally — this just works.

**Install (Windows):**

Smoke test showed `code --add-mcp` has JSON-quoting fragility in PowerShell and cmd. Skip the CLI and write to `mcp.json` directly. Save the following PowerShell script to `$env:TEMP\m8t-add-mslearn-mcp.ps1` via your file-write tool:

```powershell
$mcpFile = "$env:APPDATA\Code\User\mcp.json"
$mcpDir  = Split-Path $mcpFile

if (-not (Test-Path $mcpDir)) { New-Item -ItemType Directory -Force -Path $mcpDir | Out-Null }

$mlEntry = @{
  type = 'http'
  url  = 'https://learn.microsoft.com/api/mcp'
}

if ((Test-Path $mcpFile) -and -not [string]::IsNullOrWhiteSpace((Get-Content $mcpFile -Raw))) {
  # Parse existing JSON. Use ConvertFrom-Json (without -AsHashtable, which is PS 6.2+).
  $existing = Get-Content $mcpFile -Raw | ConvertFrom-Json

  # Convert top-level PSCustomObject to hashtable so we can index by string key.
  $config = @{}
  foreach ($prop in $existing.PSObject.Properties) { $config[$prop.Name] = $prop.Value }

  # Ensure 'servers' exists and is a hashtable. Convert if it's a PSCustomObject from JSON.
  if (-not $config.ContainsKey('servers') -or $null -eq $config['servers']) {
    $config['servers'] = @{}
  } elseif ($config['servers'] -is [PSCustomObject]) {
    $serversHash = @{}
    foreach ($prop in $config['servers'].PSObject.Properties) { $serversHash[$prop.Name] = $prop.Value }
    $config['servers'] = $serversHash
  }
} else {
  $config = @{ servers = @{} }
}

$config['servers']['microsoft-learn'] = $mlEntry

$config | ConvertTo-Json -Depth 10 | Set-Content -Path $mcpFile -Encoding utf8
```

Invoke it:

```powershell
& "$env:TEMP\m8t-add-mslearn-mcp.ps1"
```

After it completes, delete the temp file. This achieves the same end state as `code --add-mcp` (the CLI writes to the same `mcp.json`) but sidesteps all shell-quoting concerns. The PowerShell builds JSON from a native hashtable, so it can't be malformed.

If VS Code is running when this script executes, you may need to reload the window (`Developer: Reload Window`) for the new entry to be picked up — but the install line already tells the user to open a new session at the end (per `install.md`'s Done message), so this usually doesn't matter.

**Verify:**

Re-read the user MCP config and confirm:

- `servers.microsoft-learn.type` is `"http"`.
- `servers.microsoft-learn.url` is `https://learn.microsoft.com/api/mcp`.

After install, the `microsoft-learn` MCP appears in VS Code Copilot Chat's MCP server list on the next window reload (`Developer: Reload Window` from the command palette).

---

### Codex CLI (TODO — not validated this phase)

Conceptual path (validate before running):

1. Find Codex's MCP config file location.
2. Add an entry for `microsoft-learn` pointing at `https://learn.microsoft.com/api/mcp` over HTTP transport.
3. Restart Codex; verify the server is reachable.

Not validated. Out of scope for this phase.

---

### Cursor / Gemini CLI (TODO — not validated this phase)

Same shape — add an HTTP-transport MCP server pointing at `https://learn.microsoft.com/api/mcp`. Specifics depend on each host's MCP config model. Out of scope for this phase.

---

## Failure modes worth surfacing to the user

- **`claude` command not found.** Claude Code isn't installed on PATH. Stop and ask the user to install Claude Code first; this file can't bootstrap that.
- **`claude mcp add` fails with a transport / auth error.** The endpoint might be temporarily unreachable, or a firewall is blocking outbound HTTPS to `learn.microsoft.com`. Capture the verbatim error and ask the user.
- **`claude mcp list` returns the server but with "! Needs authentication".** The Microsoft Learn MCP is anonymous; this status implies a misconfigured client. Try `claude mcp remove microsoft-learn` then re-add.
- **The server name conflicts with an existing entry.** If `claude mcp list` already shows `microsoft-learn: ...` pointing at a different URL, the user has a prior install with a non-default endpoint. Ask before overwriting.
