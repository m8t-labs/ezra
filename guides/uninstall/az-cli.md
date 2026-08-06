# `uninstall/az-cli.md` — remove the Azure CLI

> 🤖 **Agent runbook (component step).** Your coding agent opens this from the uninstall flow and runs it top-to-bottom. Idempotent — safe to re-run.
>
> **Goal:** the Azure CLI package is uninstalled (Homebrew on macOS, winget on Windows). Idempotent. **Default is NO** — the Azure CLI is foundational tooling that the user almost certainly wants to keep if they use Azure for anything outside this project.

## Per-host procedure

### macOS

**Pre-check:**

```bash
which az >/dev/null 2>&1 && brew list azure-cli >/dev/null 2>&1
```

- Either command exits non-zero → no-op. Tell the user "Azure CLI not installed via Homebrew; skipping." and continue.
- Both succeed → continue.

**Prompt (default no — surface the disclaimer FIRST and prominently):**

> "**`az` is the foundational Azure CLI.** If you use Azure for anything outside this project — other coding agents, scripts, manual administration via the terminal, occasional `az login` to check resource state — you almost certainly want to keep it. m8t's removal does not require uninstalling `az`. Remove anyway? (default: NO)"

**Remove (only on explicit yes):**

```bash
brew uninstall azure-cli
```

If the cask form was installed instead of the formula, fall back to:

```bash
brew uninstall --cask azure-cli
```

**Verify:**

```bash
which az >/dev/null 2>&1 || echo "Clean."
```

Expected: `Clean.`

### Windows

**Pre-check:**

```powershell
powershell -NoProfile -Command "az --version"
```

- Command not found → no-op. Tell the user "Azure CLI not installed; skipping." and continue.
- Command exists → continue.

**Prompt (default no — surface the disclaimer FIRST and prominently):**

> "**`az` is the foundational Azure CLI.** If you use Azure for anything outside this project — other coding agents, scripts, manual administration via the terminal, occasional `az login` to check resource state — you almost certainly want to keep it. m8t's removal does not require uninstalling `az`. Remove anyway? (default: NO)"

**Remove (only on explicit yes):**

```powershell
powershell -NoProfile -Command "winget uninstall --exact --id Microsoft.AzureCLI"
```

If `az` was installed via the MSI fallback (`install/prereqs-windows.md` Step 4, used when winget wasn't available) rather than through winget, `winget uninstall` may report the package as not winget-managed. Fall back to Windows' own uninstaller: open **Settings → Apps → Installed apps**, search "Azure CLI", and remove it from there.

**Verify:**

```powershell
powershell -NoProfile -Command "if (Get-Command az -ErrorAction SilentlyContinue) { 'Still present.' } else { 'Clean.' }"
```

Expected: `Clean.`

### Linux (TODO)

Out of scope for this phase — the install pipeline doesn't support Linux yet.

## Failure modes

- **`brew uninstall` reports "azure-cli not installed".** Pre-check should have caught this; if it didn't, the formula vs cask split might be misdetected. Try the alternate form (formula → cask, or vice versa).
- **Other tools depend on `az` and Homebrew refuses the uninstall.** Capture the verbatim error and ask the user.
- **`winget uninstall` reports the package isn't found or isn't winget-managed.** It was likely installed via the MSI fallback — use Windows Settings → Apps → Installed apps instead (see the Windows Remove step above).
