# `uninstall/azure-skills.md` — remove the `microsoft/azure-skills` plugin

> 🤖 **Agent runbook (component step).** Your coding agent opens this from the uninstall flow and runs it top-to-bottom. Idempotent — safe to re-run.
>
> **Goal:** the `azure@azure-skills` plugin is unregistered from the host. **Removing this also removes the Azure MCP server (the `foundry`, `foundryextensions`, and other Azure-namespace tools).** Idempotent.

## Per-host procedure

### Claude Code (validated)

**Pre-check:**

```bash
claude plugin list 2>&1 | grep -q 'azure@azure-skills'
```

- Exit non-zero → no-op.
- Exit 0 → continue.

**Prompt (default no — surface the disclaimer FIRST):**

> "**Removing `azure@azure-skills` also removes the Azure MCP server** — the `foundry`, `foundryextensions`, and the rest of the Azure-namespace tools your coding agent has access to. Anything that depends on those tools will stop working until you re-install. Re-installable via `install/azure-skills.md`. Remove? (default: no)"

**Remove (only on yes):**

```bash
claude plugin uninstall azure@azure-skills
```

**Verify:**

```bash
claude plugin list 2>&1 | grep 'azure@azure-skills' || echo "Clean."
```

Expected: `Clean.`

## Failure modes

- **`claude plugin uninstall` rejects the format.** The plugin's slug might use a different separator on a newer Claude Code version. Capture the verbatim error and ask the user.
- **The Azure MCP server still appears in `claude mcp list` after plugin uninstall.** Some Claude Code versions leave the registered MCP server entry behind. Run `claude mcp list` and identify any remaining `plugin:azure:*` or `azure`-namespace entry, then ask the user whether to remove it explicitly via `claude mcp remove <name>` with the specific name from the list. (Don't guess the name — read the actual list.)
