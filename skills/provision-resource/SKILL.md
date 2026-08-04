---
type: skill
title: "Provision resource — Tier-1 delegation play"
created: 2026-06-07T00:00:00Z
updated: 2026-06-07T00:00:00Z
tags: [azure, provisioning, delegation, executor, tier-1]
origin: operator
---

# Provision resource

## When to run this

The founder wants to create, configure, or deploy an Azure resource — storage account, container app, database, Key Vault, Foundry project, or any other Tier-1 operation. You advise on the right choice and delegate the execution to the Executor.

## The discipline

**Frame → ground → delegate → proof — in that order.**

### 1. Frame what's needed

Read `memory/founder.md`. Confirm:
- What resource, in which subscription + resource group.
- Any constraints (region, SKU, naming, existing resources to connect to).
- One round of sharp clarifying questions if you need context; don't over-ask.

### 2. Ground the right resource

Match the founder's intent to the routing table in `persona.md` and ground the specific resource type + configuration options via the Microsoft Learn MCP:
- `microsoft_docs_search` → `microsoft_docs_fetch` for the definitive API shape.
- For storage: ground against `microsoft/azure-skills · azure-storage`.
- For identity / Key Vault: ground against `microsoft/azure-skills · azure-rbac` + `entra-app-registration`.
- For landing zone / RG baseline: ground against `microsoft/azure-skills · azure-prepare`.
- For deploy / IaC: ground against `microsoft/azure-skills · azure-deploy`.
- For Foundry resources: ground against `microsoft/azure-skills · microsoft-foundry`.

Do NOT fabricate `az` command syntax — derive it from Learn. If you're not certain of a flag, look it up.

### 3. Delegate to the Executor

1. `discover_workers` — confirm the Executor is available and read its card.
2. `invoke_worker(target:"ezra-executor", task:<complete, self-contained instruction>)`.

Pass the founder context and the proof sub-folder as **tool arguments** (the Executor writes proof into your brain automatically — the repo is always your brain):

`invoke_worker(target:"ezra-executor", task:<the instruction>, inputs:"brain:memory/founder.md", deliver_to:{pathPrefix:"artifacts/azure/"})`

The task must be self-contained — the Executor cannot ask follow-ups mid-task. Include the resource name, subscription, resource group, region, SKU, and any required configuration. Ground the exact command shape in the Learn MCP result before including it.

**Cold-start:** if the first invocation returns `storage_error` (the op did NOT run — the Executor's container pays `az login --identity` latency on the first turn), **retry once**. If it fails again, surface the error honestly.

### 4. Read proof back and close

After a successful delegation:
- `get_file_contents artifacts/azure/<date>-<slug>-proof.md` — read the proof artifact.
- Return to the founder: the **resource id**, a **portal link** (`https://portal.azure.com/#@/resource<arm-id>/overview`), and the **proof path**.
- If the result changes what you know about this founder (subscription, RG, resource inventory), write the learning to `memory/` the usual way (re-read `MEMORY.md`, name only the path, never a commit hash).

## Never

- Never run `az` yourself. You advise; the Executor executes.
- Never fabricate command syntax — ground it via Learn or defer.
- Never delegate a vague task ("set up something for me") — frame the specific resource first.
- Never skip the proof read-back — the founder needs the resource id and portal link.
