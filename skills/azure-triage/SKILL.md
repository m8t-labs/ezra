---
type: skill
title: "Azure triage — diagnose a broken or surprising result"
created: 2026-06-07T00:00:00Z
updated: 2026-06-07T00:00:00Z
tags: [azure, triage, debugging, errors, 429, 403, deployment]
origin: operator
---

# Azure triage

## When to run this

Something broke or surprised the founder — a deployment failed, an API call is throwing, quota is exhausted, a permission is denied. This is the skill that turns "why is this broken?" into a diagnosis and a concrete next step.

## The discipline

**Recognize the class → ground the fix → delegate the read or remediation → return the diagnosis.**

### 1. Recognize the error class

Match the symptom to the common classes:

**429 — Rate limit / quota exhausted**
- Throttle on a model deployment (TPM/RPM exceeded) or an Azure API rate limit.
- Read `memory/quota-and-mfs-reality.md` for the MFS quota ceiling and the distinction between a deployment-level limit and a subscription-level capacity limit.
- Ground current quota and usage via the Executor (Tier-0 read — look up the exact `az cognitiveservices` usage command via Learn).
- If quota is the root cause, hand off to `skills/request-quota/SKILL.md`.

**403 — Permission denied / RBAC gap**
- The calling principal lacks a required role on the target scope.
- Principle: least-privilege. Identify the missing role — do NOT recommend a broader role as a shortcut.
- Ground via the Learn MCP (`microsoft_docs_search` for the exact role that grants the needed action).
- Ground against `microsoft/azure-skills · azure-rbac`.
- A role assignment to fix this is Tier 2 — hand off to `skills/manage-access/SKILL.md` for the gated flow.
- **Abuse-monitoring 403 (not RBAC):** if instead *all* Azure OpenAI calls return 403 at once — a content-filtering / abuse-monitoring block, not a single permission denial — read `skills/aoai-unblock/SKILL.md` and run it.

**Deployment failure — capacity / region / quota**
- ARM deployment failed: look at the error code and inner error message.
- Common causes: capacity unavailable in region (try another region), SKU not available, quota exceeded, missing RP registration.
- Delegate a read to the Executor to retrieve the deployment operation logs (Tier-0 read).
- Ground the fix via Learn (`microsoft_docs_fetch` on the specific error code).

### 2. Ground the specific fix via Learn

For every class above, call the Microsoft Learn MCP to ground the exact fix — do NOT answer from memory for an Azure-specific error code or capability:
- `microsoft_docs_search` → `microsoft_docs_fetch` on the specific error + service.
- Quote the relevant passage and link it.

### 3. Delegate any read or fix to the Executor

For reads (Tier 0): `discover_workers` → `invoke_worker(target:"ezra-executor", task:<read instruction>)`.

Pass the founder context and the proof sub-folder as **tool arguments** (the Executor writes proof into your brain automatically — the repo is always your brain):

`invoke_worker(target:"ezra-executor", task:<the instruction>, inputs:"brain:memory/founder.md", deliver_to:{pathPrefix:"artifacts/azure/"})`

**Cold-start:** if the first invocation returns `storage_error` (the op did NOT run), retry once before reporting failure.

For remediations that are Tier 1 (e.g. re-deploy with corrected config, register RP, adjust deployment parameters): delegate normally via `provision-resource` play. For Tier 2 remediations (role assignments): hand off to `manage-access`.

### 4. Return the diagnosis and next step

- Lead with the **root cause**, not the symptom.
- State the **one concrete next step** — not a menu of options.
- Reference the proof artifact if a read was delegated.
- Write the learning to `memory/` if this reveals something durable about this founder's environment (a recurring quota limit, a misconfigured RG).

## Never

- Never guess an Azure error code meaning from memory — ground it via Learn.
- Never recommend a broader role (Owner, Contributor on subscription) to fix a 403 without explaining the blast radius.
- Never fabricate `az` command syntax for the fix — look it up.
