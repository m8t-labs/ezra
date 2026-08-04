---
type: skill
title: "Manage access — gated Tier-2 play"
created: 2026-06-07T00:00:00Z
updated: 2026-06-07T00:00:00Z
tags: [azure, rbac, access, tier-2, gated]
origin: operator
---

# Manage access

## When to run this

The founder wants to grant, revoke, or change role assignments — adding a collaborator, removing a departed employee, scoping a service principal, adjusting Key Vault policies. Any mutation of role assignments or RBAC is **Tier 2**.

## The discipline

This is a **gated Tier-2 play** — the most consequential thing you do. Follow these steps in order; never skip the confirm.

### 1. Classify

Identify the exact operation:
- Role assignment create / delete → Tier 2 (privilege group + write/delete verb).
- Role definition create / update → Tier 2.
- Key Vault set-policy → Tier 2.
- `az ad` mutations → Tier 2.
- Role assignment list / show (reads) → Tier 0, safe to delegate for information only.

Ground the exact command shape via the Microsoft Learn MCP (`microsoft_docs_search` → `microsoft_docs_fetch`). Do NOT fabricate a command — look it up. Ground against `microsoft/azure-skills · azure-rbac` and `entra-app-registration`.

### 2. State the exact effect in plain English

Before asking anything, tell the founder exactly what this operation does:
- Who is affected (principal name + object ID).
- What permission they gain or lose.
- On which scope (subscription / resource group / resource).
- Whether it's reversible and how.

Example: *"This adds Contributor to the subscription for the service principal `my-app-sp` — it gains write access to all resources in the subscription."*

### 3. Ask the founder to confirm

One explicit confirmation question. Do not proceed until the founder says yes.

### 4. On "yes" — stamp the approval and delegate

Gated execution is wired. After the founder confirms:

1. **Ground the exact `az` command** via the Learn MCP (`microsoft_docs_search` → `microsoft_docs_fetch`). Never fabricate it — you have no `az`. Ground against `microsoft/azure-skills · azure-rbac` and `entra-app-registration`.
2. **Stamp an `<m8t:approved>` marker** whose `op:` is that exact command (real principal object id + real scope ARM id — no placeholders, or the Executor's match fails and the op is refused).
3. **Delegate** via `invoke_worker(target:"ezra-executor", task:<instruction with the `<m8t:approved>` marker>, deliver_to:{pathPrefix:"artifacts/azure/"})` — the `<m8t:approved>` marker stays in the task text; pass `deliver_to` as a tool argument (the repo is always your brain).
4. **Read the proof back** (`get_file_contents <path>`, prefix `artifacts/azure/`) and return the assignment id + portal link to the founder.

If the founder says no, stop — change nothing.

### The `<m8t:approved>` marker contract

The flow: advisor confirms → stamps the approval marker with the Learn-grounded exact command → delegates it to the Executor in the task text. The marker shape:

```
<m8t:approved>
op: az role assignment create --assignee <oid> --role Reader --scope <arm-id>
tier: 2
approved-by: advisor-chat-confirm
</m8t:approved>
```

The `op:` field must echo the **exact command** the Executor will run — real values, not placeholders. The Executor canonically matches `op:` against the command it classifies as Tier-2 (flag order doesn't matter; the role, scope, and assignee must match exactly); on a match it executes and captures proof, otherwise it returns `needs_approval`. `approved-by: advisor-chat-confirm` is the canonical literal the Executor requires — only stamp it after a real human confirm. This binding prevents replaying one approval onto a different command.

## Never

- Never fabricate a role assignment command — look it up via Learn.
- Never stamp `<m8t:approved>` without an explicit human confirm in this conversation — the marker IS the human approval.
- Never use placeholder values (`<oid>`, `<arm-id>`) in the `op:` you delegate — fill the real principal id and scope, or the Executor refuses on a failed match.
- Never skip the plain-English effect statement — the founder must understand what they are confirming.
- Never route around a refusal — surface it honestly.
