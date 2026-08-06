# `uninstall/m8t-plugin.md` — uninstall the m8t plugin

> 🤖 **Agent runbook (component step).** Your coding agent opens this from the uninstall flow and runs it top-to-bottom. Idempotent — safe to re-run.
>
> **Goal:** remove the m8t plugin and any files it generated. Idempotent.

## Audience

The coding agent. Follow top to bottom. Each step prompts the user.

## Steps

### 1. Uninstall the Claude Code plugin

Ask: *"Uninstall the m8t plugin? (default: No)"* — only proceed on explicit yes.

```bash
claude plugin uninstall m8t@m8t
```

If the plugin isn't installed, the command no-ops (exit 0 with "not installed" message).

### 2. Remove generated slash command files

Ask: *"Remove the per-worker slash command files at `~/.claude/commands/`? (default: No)"*

If yes, delete files with the magic-key marker:

```bash
for f in ~/.claude/commands/*.md; do
  [ -f "$f" ] || continue
  if grep -q '^m8t-generated: true$' "$f"; then
    rm -f "$f"
  fi
done
```

This only removes files the plugin wrote. User-authored commands are untouched.

### 3. Remove logs and config

Ask: *"Remove `~/.m8t/logs/m8t.log` and `~/.m8t/m8t.yaml`? (default: No)"*

```bash
rm -f ~/.m8t/logs/m8t.log
rm -f ~/.m8t/m8t.yaml
```

The `~/.m8t/foundry/*.yaml` files are NOT removed by this uninstall — they're owned by the architect (and the plugin's own auto-discovery) and are useful for re-installing later.

### 4. Verify

```bash
claude plugin list | grep -q 'm8t@m8t' && echo "plugin still installed" || echo "plugin gone"
grep -l 'm8t-generated' ~/.claude/commands/*.md 2>/dev/null || echo "no generated files"
```

Expected: "plugin gone", "no generated files".
