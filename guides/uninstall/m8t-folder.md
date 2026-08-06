# `uninstall/m8t-folder.md` — remove `~/.m8t/`

> 🤖 **Agent runbook (component step).** Your coding agent opens this from the uninstall flow and runs it top-to-bottom. Idempotent — safe to re-run.
>
> **Goal:** the `~/.m8t/` operational folder is removed. Includes `repo-root`, `founder.yaml`, and `foundry/<agent-name>.yaml` files. The live Foundry agents themselves are NOT affected — only the local metadata files are removed.

## Procedure

**Pre-check:**

```bash
test -d ~/.m8t/
```

- Exit non-zero → no-op. Tell the user "No `~/.m8t/` folder; skipping." and continue.
- Exit 0 → continue.

**Branch on whether `~/.m8t/foundry/` has metadata files.**

```bash
ls -1 ~/.m8t/foundry/ 2>/dev/null | wc -l | tr -d ' '
```

### Branch A — count > 0: foundry metadata files exist

Ask the user explicitly (no default — user must answer):

> "Found `<N>` foundry agent metadata files under `~/.m8t/foundry/`. These are the only local record of what's deployed in your Foundry project — the live agents in Foundry are unaffected by this removal, but you'll lose the local map of which agents you deployed when. Delete `~/.m8t/` (including the foundry metadata, `repo-root`, and `founder.yaml`)?"

**No default.** Wait for an explicit yes or no.

- **Yes** → proceed to the **Remove** step below. (No second confirmation; the user already answered with the foundry metadata in scope.)
- **No** → **stop here.** Tell the user "`~/.m8t/` left in place to preserve the foundry metadata. Re-run when ready, or remove the foundry files manually first." Do NOT remove the folder.

### Branch B — count is 0: no foundry metadata files

Ask the user:

> "Remove `~/.m8t/` (`repo-root`, `founder.yaml`, and any other contents)? (default: no)"

- **Yes** → proceed to the **Remove** step below.
- **No** → stop here. Folder left in place.

### Remove (only on yes from Branch A or Branch B)

```bash
rm -rf ~/.m8t/
```

### Verify

```bash
test -d ~/.m8t/ || echo "Clean."
```

Expected: `Clean.`

## Failure modes

- **Permission denied.** Surface verbatim.
- **Folder contains files outside the expected set.** The user added something there manually. Don't silently delete; ask.
