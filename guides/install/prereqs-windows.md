# Prereqs — Windows

> 🤖 **Agent runbook (component step).** Your coding agent opens this from the install flow and runs it top-to-bottom. Idempotent — safe to re-run.
>
> Prereqs the agent installs and verifies before continuing with `install.md`. For macOS, see `install/prereqs-macos.md`.

---

## Read this first (you, the agent reading this file)

**Scope.** Your only job while following this file is: install the prerequisites, install Azure CLI, and authenticate the user against Azure. **Do not modify, create, or delete any files unrelated to this scope.** Do not "improve" the user's PowerShell profile, install unrelated tooling, or touch anything in their workspace. If a step fails, report the failure and ask — don't paper over it by editing files outside this scope.

**Interaction style.** Run commands without asking when they are non-destructive and the next step is unambiguous. Pause and ask the user only when:

- A browser-based or interactive flow needs them (`az login`).
- A command requires elevated privileges (UAC) — warn the user before triggering.
- Multiple valid choices exist and the right one is non-obvious (e.g. multiple Azure subscriptions / tenants).
- Something fails in a way that needs human judgment.

None of the above applies to winget's own package/source-agreement prompt: every `winget install` in this file passes `--accept-package-agreements --accept-source-agreements`, so it never drops into that interactive prompt. Keep both flags on any winget command you add here — without them, a fresh Windows image prompts for source trust and hangs the non-interactive agent session waiting for input that never arrives.

**Verify the install method before installing — important.**

Microsoft's recommended Windows install method changes over time. Before running the install, fetch the official install doc to confirm the current recommendation:

- **Authoritative source:** <https://learn.microsoft.com/en-us/cli/azure/install-azure-cli-windows>
- **What to look for:** the page describes the currently recommended install method. As of this writing, `winget install --exact --id Microsoft.AzureCLI` is the preferred path.
- **If the official doc recommends a different method** → follow the official doc and report what changed back to the user.

---

## Goal

End state: `az --version` works in a fresh PowerShell session, `az account show` returns an active subscription, and the active tenant matches the one the user expects to use with Microsoft Foundry.

---

## Shell convention — important

**On Windows, run shell commands in PowerShell.** If your coding-agent runtime is already running in PowerShell (for example, Claude Code's native `PowerShell` tool), run every `powershell` code block below directly. Do **not** wrap it in another `powershell -NoProfile -Command "..."`: nested shells are unnecessary, inherit the same stale environment, complicate quoting, and may be rejected by an agent's command sandbox.

If the terminal started in cmd or Git Bash, open one clean PowerShell session with `powershell -NoProfile`, then run the code blocks inside it. Keep that session for the step instead of spawning a new child for every command.

**A new child process does NOT bypass PATH caching.** It inherits its parent's already-cached environment block — it does not re-read Machine/User PATH from the registry. Live evidence: right after `winget install Git.Git` completes, `git --version` can still fail with `git : The term 'git' is not recognized...` until PATH is refreshed from the registry.

**PATH refresh — after any install in this file, refresh PATH before using the new binary.** Re-derive it from the registry and chain it onto the same command that needs the binary (a separate, later invocation won't see it — it inherits the same stale cache all over again):

```powershell
$env:Path = [System.Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [System.Environment]::GetEnvironmentVariable('Path','User')
```

Run the refresh and verification in the same PowerShell command, for example: `$env:Path = [System.Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [System.Environment]::GetEnvironmentVariable('Path','User'); git --version`. No human action or new terminal is needed. The steps below reference this as **"refresh PATH."** If a binary still isn't found after refreshing (rare), fall back to asking the user to open a brand-new PowerShell window, which starts with a fresh environment block from the OS.

All commands shown below use the direct native-PowerShell form. This convention also applies in `install/azure-skills.md`, `install/mslearn-mcp.md`, `install/m8t.md`, `install/m8t-plugin.md`, and `install/m8t-cli.md` for Windows.

**For multi-line PowerShell:** save the script to a temp `.ps1` file (e.g., `$env:TEMP\m8t-step.ps1`) via your file-write tool and invoke it from the current PowerShell session with `& "$env:TEMP\m8t-step.ps1"`. Cramming embedded newlines and nested quotes into a command string is unreliable.

---

## Step 0 — Git

Everything else in this file assumes the repo is already cloned — and cloning needs `git`. On a truly fresh Windows machine, `git` may not be installed yet, which means the very first `git clone` (from the README's quickstart) can fail before an agent ever reaches this file.

**If that's what happened:** install git with the command below, open a fresh shell so PATH picks up `git.exe`, then re-run the `git clone` command from the README's quickstart and continue from there — this file is what you land on next.

If you're reading this because the clone already succeeded, `git` is obviously present — this step exists so the file stays idempotent on re-run, and so the failure mode above has a documented fix.

```powershell
git --version
```

- Command exists → skip to Step 1.
- Command not found → install it:

```powershell
winget install --exact --id Git.Git --accept-package-agreements --accept-source-agreements
```

Refresh PATH (see **Shell convention** above), then verify:

```powershell
$env:Path = [System.Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [System.Environment]::GetEnvironmentVariable('Path','User'); git --version
```

Expected: `git version 2.x.x.windows.x`. If it's still not found, open a brand-new PowerShell window and retry — the human fallback from the Shell convention section.

## Step 1 — Pre-check

If `az` is already installed, refresh it to the latest before proceeding.

```powershell
az --version
```

- Command not found → continue with prereq install (Step 2).
- Command exists → run `az upgrade --yes` to ensure the user has the latest version. This is a non-interactive upgrade; `--yes` answers the "upgrade extensions too?" prompts automatically. If `az upgrade` fails (e.g., permission error, package-manager conflict), surface the verbatim error but **do not block** — the existing `az` will still work. Then jump to **Step 6 — Login** (and skip `az login` if `az account show` already returns a valid subscription).

```powershell
az upgrade --yes
```

## Step 2 — Pick the install method

Pre-check for winget (bundled on Windows 11 and modern Windows 10):

```powershell
winget --version
```

- Command exists → use **Step 3** (winget path, typically no admin elevation required).
- Command not found → use **Step 4** (PowerShell silent-MSI fallback, **admin required**).

## Step 3 — Install via winget (preferred)

```powershell
winget install --exact --id Microsoft.AzureCLI --accept-package-agreements --accept-source-agreements
```

The `--exact` flag ensures the official Microsoft package is installed (no fuzzy match). Skip to Step 5 (verify).

## Step 4 — Install via PowerShell silent-MSI (winget absent)

**This requires admin privileges (UAC will prompt the user).** Before running, pause and tell the user:

> "winget isn't available, so I'll download and install Azure CLI via the MSI installer. Windows will show a UAC prompt — please click Yes."

This step uses multi-line PowerShell, so use the temp-`.ps1` pattern. Save the following script to `$env:TEMP\m8t-install-msi.ps1` via your file-write tool:

```powershell
$ProgressPreference = 'SilentlyContinue'
Invoke-WebRequest -Uri https://aka.ms/installazurecliwindowsx64 -OutFile .\AzureCLI.msi
Start-Process msiexec.exe -Wait -ArgumentList '/I', 'AzureCLI.msi', '/quiet'
Remove-Item .\AzureCLI.msi
```

Then invoke:

```powershell
& "$env:TEMP\m8t-install-msi.ps1"
```

After it completes, delete the temp file.

If the user denies UAC, the install fails. Surface the cancellation verbatim and ask the user to retry with admin privileges — this is one of the unavoidable interaction boundaries.

## Step 5 — Verify the install

Refresh PATH (see **Shell convention** above), then verify:

```powershell
$env:Path = [System.Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [System.Environment]::GetEnvironmentVariable('Path','User'); az --version
```

Expected: a multi-line block starting `azure-cli 2.x.x`. If it's still not found after refreshing, something went wrong with the install — check the install logs and stop.

## Step 5b — Node.js (≥ 20)

The **local** install needs Node ≥ 20 — not only the cloud surface: `install/m8t.md` writes a render-provenance sidecar with a Node script, and the `m8t` CLI (which `m8t architect-check` invokes at the end of `install/m8t.md`, and which manages your deployment) requires Node 20+.

```powershell
node --version
```

If `node` isn't found, install it:

```powershell
winget install --exact --id OpenJS.NodeJS.LTS --accept-package-agreements --accept-source-agreements
```

Refresh PATH (see **Shell convention** above) before re-checking:

```powershell
$env:Path = [System.Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [System.Environment]::GetEnvironmentVariable('Path','User'); node --version
```

## Step 6 — Login

```powershell
az login
```

This opens the user's browser. **Pause and tell the user**: "A browser window will open for Azure sign-in. Complete the sign-in with the account that has access to the Foundry project, then come back."

### If sign-in fails

Two failure modes observed on live Windows runs:

**WAM/broker failure.** az 2.88 on Windows defaults to the Web Account Manager (WAM)
broker for sign-in. It can fail outright — no browser, no device code. Two live variants
have been observed:

```text
Unexpected exception while waiting for accounts control to finish: 'A specified logon session does not exist. It may already have been terminated.'
Unexpected exception while waiting for accounts control to finish: 'The remote procedure call failed.'. Status: Response_Status.Status_Unexpected, Error code: -2147023170
```

Fallback — bypass the broker with a device code instead:

```powershell
az login --use-device-code
```

**Pause and tell the user**: "Open the URL printed above in a browser and enter the code shown, then come back." (Same interaction boundary as the primary `az login` above.)

**If the agent runtime buffers foreground command output:** a foreground `az login
--use-device-code` can keep waiting while hiding the URL and code from both the agent and
the user. Start the same login in the background with redirected output, then poll only
until its device-code line appears. Use the temp-`.ps1` pattern from the shell convention
and save this as `$env:TEMP\m8t-start-device-login.ps1`:

```powershell
$stdoutPath = Join-Path $env:TEMP 'm8t-az-login.stdout.txt'
$stderrPath = Join-Path $env:TEMP 'm8t-az-login.stderr.txt'
Remove-Item -LiteralPath $stdoutPath,$stderrPath -ErrorAction SilentlyContinue
$az = (Get-Command az).Source
$process = Start-Process -FilePath $az -ArgumentList 'login','--use-device-code' -RedirectStandardOutput $stdoutPath -RedirectStandardError $stderrPath -WindowStyle Hidden -PassThru
$process.Id | Set-Content (Join-Path $env:TEMP 'm8t-az-login.pid.txt')
$deadline = (Get-Date).AddSeconds(60)
do {
  Start-Sleep -Seconds 1
  $loginOutput = @(Get-Content $stdoutPath -ErrorAction SilentlyContinue) + @(Get-Content $stderrPath -ErrorAction SilentlyContinue)
  $deviceLine = $loginOutput | Select-String 'https://(?:microsoft.com/devicelogin|login.microsoft.com/device)' | Select-Object -First 1
} while (-not $deviceLine -and -not $process.HasExited -and (Get-Date) -lt $deadline)
if ($deviceLine) { $deviceLine.Line } else { $loginOutput; throw 'Azure CLI did not emit a device-code line within 60 seconds.' }
```

Run the temp script. Relay the printed line immediately and leave the background login
alive while the user authorizes it. After the user returns, verify with `az account show`
below; then remove `m8t-az-login.stdout.txt`, `m8t-az-login.stderr.txt`, and
`m8t-az-login.pid.txt`. These files contain a short-lived authentication code, so do not
copy them into a repository or durable run artifact.

**Token-cache encryption failure.** Azure AD accepts the sign-in — including via `--use-device-code` above — but the login evaporates because the local token cache can't be written, surfacing:

```text
ERROR: Encryption failed: [WinError 5]  Consider disable encryption.
```

Fallback — az's own suggested mitigation:

```powershell
az config set core.encrypt_token_cache=false
```

Then re-run the login above (it needs a fresh device code — the failed attempt didn't leave a usable session). This stores the token cache unencrypted on disk; tell the user once, and note they can re-enable encryption anytime with the same command and `true`.

After login, confirm a subscription is active:

```powershell
az account show --query '{name:name, id:id, tenant:tenantId, user:user.name}' -o json
```

If the user has multiple subscriptions and the wrong one is default, list and switch:

```powershell
az account list --query '[].{name:name, id:id, isDefault:isDefault}' -o table
az account set --subscription <id-or-name>
```

When multiple subscriptions are visible, **ask the user which one to use** — don't pick for them.

### Tenant / multi-tenant note

The Foundry MCP fallback chain warns that a tenant mismatch between the MCP token and the resource tenant can cause `agent_update` to fail. If `az login` defaults to a different tenant than the one hosting the Foundry project:

```powershell
az login --tenant <tenant-id-or-domain>
```

Ask the user for the tenant ID or domain only if the current tenant clearly mismatches their stated Foundry project; don't ask preemptively.

## Step 7 — "Ready" gate

All of the following must be true before the m8t install can proceed:

- [ ] `git --version` returns a version.
- [ ] `az --version` returns a version.
- [ ] `az account show` returns a subscription (not an error).
- [ ] The active subscription / tenant matches what the user said they want to use with Microsoft Foundry.
- [ ] `node --version` returns ≥ 20 (the local install's sidecar + the `m8t` CLI need it).

If any check fails, report which one and stop. Do not attempt to fix it by editing user config files.

A model deployment (e.g. `gpt-4.1-mini`) inside the target Foundry project is also required for the spin-up skill to work end-to-end — but that's the m8t install snippet's responsibility, not this file's.

## References

- [Install the Azure CLI on Windows (authoritative)](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli-windows) — **always check this before installing**, not after.
- [`az login` reference](https://learn.microsoft.com/cli/azure/reference-index#az-login)
- [winget documentation](https://learn.microsoft.com/en-us/windows/package-manager/winget/)

## Additional prerequisites for the cloud surface

These are only needed if you'll **deploy** the platform (see `deploy.md`), not for the local install:

- **Node ≥ 20** — already installed in the base prereqs (Step 5b above); `m8t deploy` and the hosted-image build need it too.
- **Docker** (with `buildx`) — to build and push the hosted coding-agent image.
- We do **not** use `azd` — the deploy runs via `m8t deploy` (the `m8t` CLI) plus the `az` CLI.
