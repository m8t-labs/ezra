# `uninstall/mslearn-mcp.md` — remove the Microsoft Learn MCP

> 🤖 **Agent runbook (component step).** Your coding agent opens this from the uninstall flow and runs it top-to-bottom. Idempotent — safe to re-run.
>
> **Goal:** the `microsoft-learn` MCP server is unregistered from the host. Idempotent.

## Per-host procedure

### Claude Code (validated)

**Pre-check:**

```bash
claude mcp list 2>&1 | grep -q '^microsoft-learn:'
```

- Exit non-zero → no-op. Tell the user "MS Learn MCP not registered; skipping." and continue.
- Exit 0 → continue.

**Prompt (default no):**

> "Remove the `microsoft-learn` MCP server from Claude Code? Easy to re-add via `install/mslearn-mcp.md`. (default: no)"

**Remove (only on yes):**

```bash
claude mcp remove microsoft-learn
```

If the command's scope is unclear, the default scope `--scope local` may not match the install scope (`--scope user`). If `claude mcp remove microsoft-learn` reports "not found," retry with `--scope user`:

```bash
claude mcp remove --scope user microsoft-learn
```

**Verify:**

```bash
claude mcp list 2>&1 | grep '^microsoft-learn:' || echo "Clean."
```

Expected: `Clean.`

### Other hosts (TODO)

Same shape as install — locate the host's MCP config and remove the `microsoft-learn` entry.

## Failure modes

- **`claude` not on PATH.** Surface verbatim and ask the user to fix.
- **`claude mcp remove` reports "server not found"** despite pre-check passing. The MCP might be in a different scope; retry with `--scope user` or `--scope project`.
