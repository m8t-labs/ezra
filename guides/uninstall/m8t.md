# `uninstall/m8t.md` — remove m8t skills

> 🤖 **Agent runbook (component step).** Your coding agent opens this from the uninstall flow and runs it top-to-bottom. Idempotent — safe to re-run.
>
> **Goal:** `~/.claude/skills/m8t-*/` directories are removed from the host. Idempotent — re-running this is a no-op if nothing is there.

## Per-host procedure

### Claude Code (validated)

**Pre-check:**

```bash
shopt -s nullglob
m8t_skills=(~/.claude/skills/m8t-*/)
echo "${#m8t_skills[@]}"
```

- Output `0` → no m8t skills installed. Tell the user "No m8t skills installed; skipping." and continue.
- Output `1` or higher → m8t skills present. Print the list to the user (`printf '%s\n' "${m8t_skills[@]}"`), then ask:

  > "Found these m8t skills: `<list>`. Remove all of them? (default: no)"

  Wait for explicit yes/no. **Do not silently default** — show the default in the prompt but require an explicit answer.

**Remove (only on yes):**

```bash
for d in ~/.claude/skills/m8t-*/; do
  test -d "$d" && rm -rf "$d" && echo "Removed: $d"
done
```

**Verify:**

```bash
shopt -s nullglob
remaining=(~/.claude/skills/m8t-*/)
[ "${#remaining[@]}" -eq 0 ] && echo "Clean." || printf 'Remaining: %s\n' "${remaining[@]}"
```

Expected: `Clean.`

### Codex / Cursor / Copilot / Gemini (TODO)

Conceptually the same — locate the host's user-scope skills directory and remove `m8t-*` entries. Not validated this phase.

## Failure modes

- **Permission denied on `rm -rf`.** Surface the error verbatim. The user might need to fix file permissions before retrying.
- **Directory disappears between pre-check and remove (race).** No-op; the verification will still pass.
