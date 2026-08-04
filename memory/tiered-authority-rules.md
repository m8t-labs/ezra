---
type: memory
title: "Tiered authority rules — group-first, verb-second, deny-by-default"
created: 2026-06-07T00:00:00Z
updated: 2026-06-07T00:00:00Z
tags: [tiers, authority, gating]
origin: operator
---

The advisor's chat boundary must mirror the Executor's tool boundary. The same classifier governs both.

Classification order (group-first, then verb, case-insensitive):

1. **`az rest`** — by `--method`: GET → Tier 0. Anything else → Tier 2.
2. **Tier 0 — read (auto-proceed).** Verb ∈ {`list`, `show`, `get`, `exists`}, or `list-*` / `*-list` / `check*`. Reads are Tier 0 **even on privilege groups** — reading RBAC is safe.
3. **Tier 2 — destructive or privileged (refuse / gate).** Destructive verb ∈ {`delete`, `remove`, `purge`}; OR a privilege group (`role assignment`, `role definition`, `ad`, `policy assignment`, `keyvault set-policy`) with a write or unknown verb.
4. **Tier 1 — provision (delegate normally).** Verb ∈ {`create`, `update`, `set`, `configure`, `scale`, `deploy`, `add`, `enable`, `disable`, `start`, `stop`, `restart`}.
5. **Anything else → refuse as ambiguous.** Deny-by-default; the Executor's tool does the same.

**Known classifier gap — be more conservative than the tool:** `policy definition <write>` currently lands Tier 1 (only `policy assignment` is a privilege group in the classifier; tightening is deferred). At the advisory layer, treat creating or updating a policy *definition* as Tier-2 intent — state the effect and confirm before any delegation.

**What to do at each tier:**

- **Tier 0:** advise freely; delegate to the Executor for the actual read if the founder wants live data.
- **Tier 1:** delegate to the Executor normally via `invoke_worker`.
- **Tier 2:** classify the request → state the exact effect in plain English (e.g. *"this removes Bob's Contributor role on the subscription — he'd lose write access"*) → ask the founder to confirm → **STOP and wait**. Only after an explicit yes: Learn-ground the exact `az` command (never guess it), stamp the `<m8t:approved>` marker with that exact command, and delegate. The Executor re-classifies independently and refuses if the marker does not match. If they say no, change nothing.

Shell metacharacters (`;`, `&&`, `||`, `|`, backtick, `$(`, `>`, `<`, newline) in a command → reject outright regardless of tier.

The two-layer gate is intentional: the model self-refuses at the chat layer; the Executor tool refuses at the tool layer. Both layers enforce the same boundary.
