# `install/m8t.md` — wire the Architect into the host

> 🤖 **Agent runbook (component step).** Your coding agent opens this from the install flow and runs it top-to-bottom. Idempotent — safe to re-run.
>
> **Goal:** after this step, the Architect is invocable as a global skill in the user's coding-agent CLI (e.g. via Claude Code's skill list from any directory), and the Architect can locate the cloned m8t repo at runtime.
>
> Idempotent — re-running this is a no-op when state already matches.

## What this does (high-level)

1. Detect the user-scoped skills directory of the host.
2. **One-time rename migration** — if `~/.claude/skills/m8t-azure-architect/` exists from a pre-rename install, migrate it to `~/.claude/skills/m8t-architect/` (or surface a conflict if the user edited the legacy install).
3. **For each `personas/*/persona.md` whose `allowed-targets` contains `local`,** render it into a host-shaped skill artifact via the procedure in `targets/local/README.md` and drop it into the host's skills directory (under `<targets.local.name>/`). The adapter no longer auto-prefixes — the rendered directory name is the slug declared in the persona file.
4. Write `~/.m8t/repo-root` with the absolute path to the cloned repo so personas can find their dependencies (other personas, domain playbooks) at runtime.

No shell-config edits. No environment-variable mutation. Reversible by deleting under `~/.claude/skills/m8t-*/` and `~/.m8t/`.

## Per-host procedure

---

### Claude Code (validated)

**0. Rename migration (one-time — pre-Phase-7 installs only).**

The legacy install rendered the Architect at `~/.claude/skills/m8t-azure-architect/`. The new convention renders it at `~/.claude/skills/m8t-architect/`. The migration is implemented as: remove the legacy directory in this step (if its contents match the new render); step 2's per-persona loop then re-renders the Architect at the new location. There is no `mv` — re-render is the source of truth.

macOS:

```bash
test -d ~/.claude/skills/m8t-azure-architect/
```

Windows (PowerShell):

```powershell
Test-Path "$env:USERPROFILE\.claude\skills\m8t-azure-architect\"
```

If the directory does NOT exist → no migration needed; skip to step 1.

If it exists, decide what to do based on the body of its `SKILL.md`:

- **If the body of `~/.claude/skills/m8t-azure-architect/SKILL.md` (everything after the second `---` line) is byte-identical to the body of `<repo-root>/personas/m8t-architect/persona.md` (everything after the second `---` line)** → the legacy install was a stock render. Safe to delete; the new render in step 2 will replace it.

  macOS:

  ```bash
  rm -rf ~/.claude/skills/m8t-azure-architect/
  ```

  Windows (PowerShell):

  ```powershell
  Remove-Item -Recurse -Force "$env:USERPROFILE\.claude\skills\m8t-azure-architect\"
  ```

- **If the body differs** → the user edited the legacy install or a prior partial render produced something else. **STOP and ask the user** which of these applies, then proceed per their instruction. Same rule as the SKILL.md write-conflict in step 2 below.

**Also check for the round-1/round-2 `m8t-mfs-advisor` slug** (pre-Round-3 installs). The migration follows the same pattern: remove the legacy directory if its contents match the new stock render; step 2's per-persona loop then re-renders the advisor at `m8t-mfs-azure-advisor`. There is no `mv` — re-render is the source of truth.

macOS:

```bash
test -d ~/.claude/skills/m8t-mfs-advisor/
```

Windows (PowerShell):

```powershell
Test-Path "$env:USERPROFILE\.claude\skills\m8t-mfs-advisor\"
```

If the directory does NOT exist → no migration needed.

If it exists, decide based on the body of its `SKILL.md`:

- **If the body of `~/.claude/skills/m8t-mfs-advisor/SKILL.md` (everything after the second `---` line) is byte-identical to the body of `<repo-root>/personas/m8t-mfs-azure-advisor/persona.md` (everything after the second `---` line)** → safe to delete:

  macOS:

  ```bash
  rm -rf ~/.claude/skills/m8t-mfs-advisor/
  ```

  Windows (PowerShell):

  ```powershell
  Remove-Item -Recurse -Force "$env:USERPROFILE\.claude\skills\m8t-mfs-advisor\"
  ```

- **If the body differs** → **STOP and ask the user.** Same handling as the SKILL.md write-conflict in step 2 below.

After resolution, continue to step 1.

**1. Detect the skills directory.**

Claude Code's user-scoped skills directory is `~/.claude/skills/`. Confirm it (create it if missing — only the directory, not anything inside):

macOS:

```bash
mkdir -p ~/.claude/skills
```

Windows (PowerShell):

```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.claude\skills" | Out-Null
```

**2. Render and install each `local`-target persona.**

For each `<repo-root>/personas/*/persona.md`:

1. Parse the YAML frontmatter.
2. If `allowed-targets` does NOT include `local`, skip this persona.
3. If it does, follow the "Claude Code (validated)" section of `targets/local/README.md` with this persona file as input. The output is the rendered `SKILL.md` content.
4. Compute the destination: `~/.claude/skills/<targets.local.name>/SKILL.md`. (The adapter no longer auto-prefixes; the slug is rendered verbatim.)
5. **Idempotency-aware write:**
   - Destination missing → create the parent directory and write the rendered content.
   - Destination exists with byte-identical content → skip silently (no-op).
   - Destination exists with different content → **STOP and ask the user.** Likely causes: (a) user manually edited it; (b) older render from a previous install; (c) different m8t checkout wired up. Ask which, and proceed per the user's instruction.
6. **Write the provenance sidecar**: after `SKILL.md` is written, run:

   macOS:

   ```bash
   node "$(cat ~/.m8t/repo-root)/scripts/write-skill-sidecar.mjs" "$(cat ~/.m8t/repo-root)/personas/<name>/persona.md" ~/.claude/skills/<targets.local.name>
   ```

   Windows (PowerShell):

   ```powershell
   $RepoRoot = Get-Content "$env:USERPROFILE\.m8t\repo-root"
   node "$RepoRoot\scripts\write-skill-sidecar.mjs" "$RepoRoot\personas\<name>\persona.md" "$env:USERPROFILE\.claude\skills\<targets.local.name>"
   ```

   This records the source hash + version in `~/.claude/skills/<targets.local.name>/<targets.local.name>.m8t-skill.json` (the sidecar filename is scoped per persona, not a fixed `.m8t-skill.json` — see `targets/local/README.md`), which `m8t architect-check` (the final verification step below) reads to detect drift. Re-run it on every render (it always overwrites).

For Phase 7 (Personas Galore), this enumerates two personas: `personas/m8t-architect/persona.md` (renders to `~/.claude/skills/m8t-architect/SKILL.md`) and `personas/m8t-mfs-azure-advisor/persona.md` (renders to `~/.claude/skills/m8t-mfs-azure-advisor/SKILL.md`). The CMO persona is `allowed-targets: [foundry]` and is skipped here.

**3. Write `~/.m8t/repo-root`.**

This is a single-line absolute-path file the Architect reads at runtime to locate `personas/`.

**Migration from `~/.config/m8t/` (one-time).**

Before writing the new pointer, migrate any pre-Phase-3 install:

macOS:

````bash
if [ -f ~/.config/m8t/repo-root ] && [ ! -f ~/.m8t/repo-root ]; then
  mkdir -p ~/.m8t
  cp ~/.config/m8t/repo-root ~/.m8t/repo-root
  rm ~/.config/m8t/repo-root
  rmdir ~/.config/m8t 2>/dev/null || true
  echo "Migrated repo-root from ~/.config/m8t to ~/.m8t/."
fi
````

Windows (PowerShell):

```powershell
$LegacyRepoRoot = "$env:USERPROFILE\.config\m8t\repo-root"
$NewRepoRoot    = "$env:USERPROFILE\.m8t\repo-root"
if ((Test-Path $LegacyRepoRoot) -and -not (Test-Path $NewRepoRoot)) {
  New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.m8t" | Out-Null
  Copy-Item $LegacyRepoRoot $NewRepoRoot
  Remove-Item $LegacyRepoRoot
  Remove-Item "$env:USERPROFILE\.config\m8t" -ErrorAction SilentlyContinue
  Write-Output "Migrated repo-root from $env:USERPROFILE\.config\m8t to $env:USERPROFILE\.m8t\."
}
```

Idempotent: if `~/.m8t/repo-root` already exists, the block is a no-op. If both exist with different content, the existing-content check in the next sub-step handles it (asks the user).

macOS:

```bash
mkdir -p ~/.m8t
```

Windows (PowerShell):

```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.m8t" | Out-Null
```

Compute the cloned-repo absolute path (the directory containing this `install/m8t.md`'s parent). Then:

- If `~/.m8t/repo-root` does NOT exist → write the absolute path (single line; a trailing `\n` is fine).
- If it exists and matches → no-op.
- If it exists and differs → **STOP and ask the user.** Likely cause: a different m8t checkout was previously installed. Ask: replace pointer? Keep old pointer? Abort install? Proceed per user instruction.

**4. Verify.**

macOS:

```bash
test -f ~/.claude/skills/m8t-architect/SKILL.md && echo "m8t-architect SKILL.md ok"
test -f ~/.claude/skills/m8t-mfs-azure-advisor/SKILL.md && echo "m8t-mfs-azure-advisor SKILL.md ok"
test -f ~/.m8t/repo-root && echo "repo-root ok"
cat ~/.m8t/repo-root
```

Windows (PowerShell):

```powershell
if (Test-Path "$env:USERPROFILE\.claude\skills\m8t-architect\SKILL.md") { "m8t-architect SKILL.md ok" }
if (Test-Path "$env:USERPROFILE\.claude\skills\m8t-mfs-azure-advisor\SKILL.md") { "m8t-mfs-azure-advisor SKILL.md ok" }
if (Test-Path "$env:USERPROFILE\.m8t\repo-root") { "repo-root ok" }
Get-Content "$env:USERPROFILE\.m8t\repo-root"
```

Expected: three `ok` lines, plus the cloned-repo absolute path.

**Update path:** when the user runs `git pull` in the cloned repo, re-run this section to re-render the SKILL.md. The idempotency rules in step 2 mean a no-change pull is a no-op; a change in the persona file produces a new rendered SKILL.md (and triggers the "differs" branch — agent prompts user to overwrite, which is the right behavior since the source-of-truth changed).

**Final verification — architect in sync.**

> ⚠️ **This section needs access to the m8t platform repository, which is not public.**
> Rendering a `local`-target persona reads it from `personas/` in a platform checkout,
> and `m8t architect-check` reads the same place. In this repository they refuse by name.
> The rest of the install — the platform itself, and talking to your workers — does not
> depend on this step; it is optional tooling for your coding agent.

After all renders complete, verify the install. This uses the `m8t` CLI (Node ≥ 20). If it isn't installed yet, install it first — `npm install -g @m8t-stack/cli` (see [`install/m8t-cli.md`](m8t-cli.md)):

macOS:

```bash
m8t architect-check
```

Windows (PowerShell):

```powershell
m8t architect-check
```

Expected: exit 0 with `✓ m8t-architect is in sync (vX.Y)`. If exit 1, the
rendered SKILL.md doesn't match the source persona — re-run the **"Render and install each `local`-target persona"** step above (step 2 in this section) and try again. (`m8t architect-check` is the same gate the architect itself
runs at activation.)

---

### GitHub Copilot CLI

**0. Resolve the skills directory (runtime probe).**

Copilot CLI's user-scope skills directory isn't fully publicly documented as of this writing. Probe candidate paths in this order, and use the first one that exists:

```bash
for p in ~/.copilot/skills/ ~/.config/github-copilot/skills/ ~/.github/copilot/skills/; do
  [ -d "$p" ] && echo "RESOLVED: $p" && break
done
```

Equivalent PowerShell:

```powershell
$Candidates = @(
  "$env:USERPROFILE\.copilot\skills\",
  "$env:USERPROFILE\.config\github-copilot\skills\",
  "$env:USERPROFILE\.github\copilot\skills\"
)
foreach ($p in $Candidates) {
  if (Test-Path $p) { Write-Output "RESOLVED: $p"; break }
}
```

If none exist, default to `~/.copilot/skills/` (`$env:USERPROFILE\.copilot\skills\` on Windows) — most likely per Copilot CLI's naming conventions; create it with `mkdir -p` (`New-Item -ItemType Directory -Force` on Windows). **Report the resolved path in your success message** so the next maintainer can codify it.

**0a. Rename migration (one-time — pre-Round-3 installs only).**

Round-1/Round-2 installs rendered the MFS advisor at `<resolved-skills-dir>/m8t-mfs-advisor/`. The new convention renders it at `<resolved-skills-dir>/m8t-mfs-azure-advisor/`. Migration follows the same pattern as the Claude Code section: remove the legacy directory if its contents match the new stock render; step 1's per-persona loop then re-renders the advisor at the new slug.

```bash
test -d <resolved-skills-dir>/m8t-mfs-advisor/
```

If the directory does NOT exist → no migration needed.

If it exists, decide based on the body of its `SKILL.md`:

- **If the body is byte-identical to `<repo-root>/personas/m8t-mfs-azure-advisor/persona.md`'s body (everything after the second `---` line)** → safe to delete:

  ```bash
  rm -rf <resolved-skills-dir>/m8t-mfs-advisor/
  ```

- **If the body differs** → **STOP and ask the user.** Same handling as the SKILL.md write-conflict in step 1 below.

After resolution, continue to step 1.

**1. Render and install each `local`-target persona.**

**Use your file-manipulation tools (Read, Write, Edit), not shell scripts, for the rendering steps below.** Persona rendering is read-parse-write — your agent file tools handle this far more reliably than a PowerShell one-liner. Cramming multi-step procedures into single shell commands is the leading cause of terminal crashes and state confusion in agent sessions (this was a documented failure mode in the round-1 Windows smoke test).

If your runtime requires shell (e.g., a hard constraint of your agent), save the logic to a temp `.ps1` file via your file-write tool and invoke it from the current PowerShell session with `& "$env:TEMP\m8t-render.ps1"` — never inline.

For each `<repo-root>/personas/*/persona.md`:

1. Parse the YAML frontmatter.
2. If `allowed-targets` does NOT include `local`, skip this persona.
3. If it does, follow the "GitHub Copilot CLI" section of `targets/local/README.md` with this persona file as input. The output is the rendered `SKILL.md` content.
4. Compute the destination: `<resolved-skills-dir>/<targets.local.name>/SKILL.md`.
5. **Idempotency-aware write:**
   - If the destination does not exist → create the parent dir and write the rendered artifact.
   - If the destination exists with byte-identical content → no-op (skip, do not touch the mtime).
   - If the destination exists with different content → **STOP and ask the user.** Likely causes: (a) the user manually edited the file; (b) a previous install rendered an older version; (c) a different m8t checkout is wired up. Ask which of the three it is and proceed per the user's instruction.

For Phase 7 (Personas Galore), this enumerates two personas: `personas/m8t-architect/persona.md` → `<resolved-skills-dir>/m8t-architect/SKILL.md`, and `personas/m8t-mfs-azure-advisor/persona.md` → `<resolved-skills-dir>/m8t-mfs-azure-advisor/SKILL.md`. The CMO persona is `allowed-targets: [foundry]` and is skipped here.

**2. Write `~/.m8t/repo-root`.** Identical to the Claude Code section — see steps "Migration from `~/.config/m8t/`" and the existing-content check above. The pointer file is host-agnostic.

**3. Verify.**

```bash
# Substitute <resolved-skills-dir> with the path resolved in Step 0.
test -f <resolved-skills-dir>/m8t-architect/SKILL.md && echo "m8t-architect SKILL.md ok"
test -f <resolved-skills-dir>/m8t-mfs-azure-advisor/SKILL.md && echo "m8t-mfs-azure-advisor SKILL.md ok"
test -f ~/.m8t/repo-root && echo "repo-root ok"
cat ~/.m8t/repo-root
```

Expected: three `ok` lines plus the cloned-repo absolute path.

**Update path:** when the user runs `git pull` in the cloned repo, re-run this section. Idempotency rules in step 1 mean a no-change pull is a no-op; a change in a persona file produces a new rendered SKILL.md (and triggers the "differs" branch, which prompts the user).

If Copilot CLI's frontmatter format turns out to differ from Claude Code's `{name, description}` shape (e.g. Copilot CLI expects an additional required field), surface that in the success message and consider updating `targets/local/README.md` accordingly.

---

### VS Code Copilot Chat

**0. Resolve the VS Code user data directory and prompts subfolder.**

Detect the OS:

- macOS: VS Code user data dir = `~/Library/Application Support/Code/User/`
- Windows: VS Code user data dir = `%APPDATA%\Code\User\`

Probe the prompts subfolder (`prompts/` is the default; older VS Code versions used `prompt-files/`):

```bash
# macOS example — adapt for Windows with PowerShell
USER_DATA="$HOME/Library/Application Support/Code/User"
if [ -d "$USER_DATA/prompts" ]; then
  SUBFOLDER="prompts"
elif [ -d "$USER_DATA/prompt-files" ]; then
  SUBFOLDER="prompt-files"
else
  SUBFOLDER="prompts"  # default; will be created
  mkdir -p "$USER_DATA/$SUBFOLDER"
fi
echo "RESOLVED: $USER_DATA/$SUBFOLDER"
```

Equivalent PowerShell:

```powershell
$UserData = "$env:APPDATA\Code\User"
if (Test-Path "$UserData\prompts") {
  $Subfolder = "prompts"
} elseif (Test-Path "$UserData\prompt-files") {
  $Subfolder = "prompt-files"
} else {
  $Subfolder = "prompts"
  New-Item -ItemType Directory -Force -Path "$UserData\$Subfolder" | Out-Null
}
Write-Output "RESOLVED: $UserData\$Subfolder"
```

**Report the resolved subfolder name in your success message** so the next maintainer can codify it.

**0a. Rename migration (one-time — pre-Round-3 installs only).**

Round-1/Round-2 installs rendered the MFS advisor at `<resolved-user-data>/<subfolder>/m8t-mfs-advisor.prompt.md`. The new convention renders it at `<resolved-user-data>/<subfolder>/m8t-mfs-azure-advisor.prompt.md`. Migration is file-level (not directory-level like Claude Code / Copilot CLI): remove the legacy `.prompt.md` if its body matches the new stock render; step 1's per-persona loop then re-renders the advisor at the new slug.

macOS:

```bash
test -f "$USER_DATA/$SUBFOLDER/m8t-mfs-advisor.prompt.md"
```

Windows (PowerShell):

```powershell
Test-Path "$env:APPDATA\Code\User\$Subfolder\m8t-mfs-advisor.prompt.md"
```

If the file does NOT exist → no migration needed.

If it exists, decide based on the body (everything after the second `---` line):

- **If the body is byte-identical to `<repo-root>/personas/m8t-mfs-azure-advisor/persona.md`'s body** → safe to delete:

  macOS:

  ```bash
  rm "$USER_DATA/$SUBFOLDER/m8t-mfs-advisor.prompt.md"
  ```

  Windows (PowerShell):

  ```powershell
  Remove-Item "$env:APPDATA\Code\User\$Subfolder\m8t-mfs-advisor.prompt.md"
  ```

- **If the body differs** → **STOP and ask the user.** Same handling as the prompt-file write-conflict in step 1 below.

After resolution, continue to step 1.

**1. Render and install each `local`-target persona.**

**Use your file-manipulation tools (Read, Write, Edit), not shell scripts, for the rendering steps below.** Persona rendering is read-parse-write — your agent file tools handle this far more reliably than a PowerShell one-liner. Cramming multi-step procedures into single shell commands is the leading cause of terminal crashes and state confusion in agent sessions (this was a documented failure mode in the round-1 Windows smoke test).

If your runtime requires shell (e.g., a hard constraint of your agent), save the logic to a temp `.ps1` file via your file-write tool and invoke it from the current PowerShell session with `& "$env:TEMP\m8t-render.ps1"` — never inline.

For each `<repo-root>/personas/*/persona.md`:

1. Parse the YAML frontmatter.
2. If `allowed-targets` does NOT include `local`, skip this persona.
3. If it does, follow the "VS Code Copilot Chat" section of `targets/local/README.md` with this persona file as input. The output is the rendered `<slug>.prompt.md` content.
4. Compute the destination: `<resolved-user-data>/<subfolder>/<targets.local.name>.prompt.md`.
5. **Idempotency-aware write:**
   - If the destination does not exist → create the parent dir and write the rendered artifact.
   - If the destination exists with byte-identical content → no-op (skip, do not touch the mtime).
   - If the destination exists with different content → **STOP and ask the user.** Likely causes: (a) the user manually edited the file; (b) a previous install rendered an older version; (c) a different m8t checkout is wired up. Ask which of the three it is and proceed per the user's instruction.

For Phase 7 (Personas Galore), this renders `personas/m8t-architect/persona.md` → `<dir>/m8t-architect.prompt.md` and `personas/m8t-mfs-azure-advisor/persona.md` → `<dir>/m8t-mfs-azure-advisor.prompt.md`. The CMO persona is skipped (foundry-only).

**2. Write `~/.m8t/repo-root`.** Identical to the Claude Code section. Host-agnostic.

**3. Verify.**

macOS:

```bash
# $SUBFOLDER must be set (from Step 0 probe). If running in a fresh shell, re-run the probe or substitute the resolved value (typically "prompts").
SUBFOLDER="${SUBFOLDER:-prompts}"
test -f "$HOME/Library/Application Support/Code/User/$SUBFOLDER/m8t-architect.prompt.md" && echo "m8t-architect prompt ok"
test -f "$HOME/Library/Application Support/Code/User/$SUBFOLDER/m8t-mfs-azure-advisor.prompt.md" && echo "m8t-mfs-azure-advisor prompt ok"
test -f ~/.m8t/repo-root && echo "repo-root ok"
cat ~/.m8t/repo-root
```

Windows (PowerShell):

```powershell
# $Subfolder must be set (from Step 0 probe). If running in a fresh shell, re-run the probe or substitute the resolved value (typically "prompts").
if (-not $Subfolder) { $Subfolder = "prompts" }
Test-Path "$env:APPDATA\Code\User\$Subfolder\m8t-architect.prompt.md"
Test-Path "$env:APPDATA\Code\User\$Subfolder\m8t-mfs-azure-advisor.prompt.md"
Test-Path "$env:USERPROFILE\.m8t\repo-root"
Get-Content "$env:USERPROFILE\.m8t\repo-root"
```

Tell the user once: *"New prompt files installed. If VS Code Copilot Chat doesn't see them, run `Developer: Reload Window` from the command palette."* Informational, not a blocker.

**Update path:** when the user runs `git pull` in the cloned repo, re-run this section. Idempotency rules in step 1 mean a no-change pull is a no-op; a change in a persona file produces a new rendered `.prompt.md` (and triggers the "differs" branch, which prompts the user).

**Final verification — architect in sync.**

After all renders complete, verify the install. This uses the `m8t` CLI (Node ≥ 20). If it isn't installed yet, install it first — `npm install -g @m8t-stack/cli` (see [`install/m8t-cli.md`](m8t-cli.md)):

```bash
m8t architect-check
```

Expected: exit 0 with `✓ m8t-architect is in sync (vX.Y)`. If exit 1, the
rendered prompt file doesn't match the source persona — re-run the **"Render and install each `local`-target persona"** step above (step 1 in this section) and try again. (`m8t architect-check` is the same gate the architect itself
runs at activation.)

### Codex CLI (TODO — not validated this phase)

Same shape:

1. Detect Codex's user-scoped skills directory (location TBD; verify on a real install).
2. Render the Architect via `targets/local/README.md`'s Codex section (also TODO).
3. Idempotency-aware write.
4. Write `~/.m8t/repo-root` (same as Claude Code).

Out of scope for Phase 1.

### Cursor (TODO — not validated this phase)

Same shape; Cursor's skills directory and any frontmatter conventions need verification. Out of scope for Phase 1.

### Gemini CLI (TODO — not validated this phase)

Same shape. Out of scope for Phase 1.

---

## Uninstall (informational)

The new uninstall flow is `uninstall.md` (paste-into-coding-agent, walks through prompts in safest-first order). Manual reversal:

```bash
rm -rf ~/.claude/skills/m8t-architect/ ~/.claude/skills/m8t-mfs-azure-advisor/
rm -rf ~/.m8t/
```

The `microsoft/azure-skills` plugin and the `microsoft-learn` MCP are uninstalled separately (see `uninstall/azure-skills.md`, `uninstall/mslearn-mcp.md`).
