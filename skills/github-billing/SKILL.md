---
type: skill
title: "GitHub billing — pay for GitHub with Azure credits"
created: 2026-06-22T00:00:00Z
updated: 2026-06-22T00:00:00Z
tags: [github, billing, azure, credits, mfs]
origin: operator
---

# GitHub billing

## When to run this

The founder wants to use their Azure credits to pay for metered GitHub services — Copilot, Codespaces, Actions minutes / storage — by connecting their Azure subscription as a GitHub payment method. They may say "pay for GitHub with Azure credits", "connect Azure to GitHub billing", "use my credits for Copilot".

## The discipline

**Gather → check prerequisites (delegate the Owner read) → ground the current flow → emit the setup guide.**

### 1. Gather the founder's context

Read `memory/founder.md` for the Azure subscription id and the founder's identity. The connection needs:
- the target **Azure subscription id**,
- the founder's **Microsoft work account** (the account that will own the connection),
- the **GitHub organization** name.

If any is missing, ask ONE round of clarifying questions covering all the gaps at once, then persist the answers to `memory/founder.md` so the next request is zero-friction. The Owner-role check below also needs the founder's Entra **object-id** — capture it once if it is not already recorded.

### 2. Check the prerequisites (delegate the reads)

The founder will hit errors if these fail — check them before writing the guide.

**Owner role on the subscription (the critical one).** The account connecting GitHub MUST have the Owner role on the target subscription. Delegate a Tier-0 read to the Executor:

`discover_workers` -> `invoke_worker(target:"ezra-executor", task:<owner read>)`.

Ground the exact command via the Learn MCP before delegating; the canonical form is:
```
az role assignment list --all --assignee-object-id <founder-oid> --scope /subscriptions/<sub> --include-inherited --query "[?roleDefinitionName=='Owner']" -o json
```
Use `--assignee-object-id` (the founder's Entra object-id from memory) so the read does not depend on Microsoft Graph; if only the UPN is known, use `--assignee <upn> --fill-principal-name false`. Pass `inputs:"brain:memory/founder.md"` and `deliver_to:{pathPrefix:"artifacts/azure/"}` as tool arguments (the repo is always your brain). **Cold-start:** retry once on `storage_error`.

**Work vs personal account.** The Owner must be a work (Entra) account in the subscription's tenant, not a personal Microsoft account masked with a company email. Infer from the role read's principal type, or ask.

**Sufficient credits.** Confirm the founder has Azure credits to cover expected GitHub spend — a `cost-check` read or a quick intake question.

### 3. Ground the current GitHub flow

The GitHub-side steps change — ground them against the live GitHub docs (`web_search` / fetch `docs.github.com` billing pages) rather than reciting a remembered flow. Confirm the current path to add an Azure subscription as a payment method before writing the guide.

### 4. Emit the founder-facing setup guide

Report the prerequisite results (pass/fail per check), then produce a personalized guide with the subscription id filled in:

> # Connect Azure as your GitHub payment method
>
> ## Prerequisites
> - Azure subscription `<sub>` with you as Owner
> - Signed in to your work Microsoft account (not personal)
> - Azure credits available to cover GitHub usage
>
> ## Steps
> 1. Sign in to your GitHub organization's billing settings.
> 2. Add a payment method, then choose "Azure subscription".
> 3. Sign in with your work Microsoft account and select subscription `<sub>`.
> 4. Authorize the connection.
> 5. (Recommended) Set per-service spending limits so usage cannot exceed your credit burn.
> 6. Verify: within about 24h GitHub usage appears as a line item on your Azure invoice.
>
> ## If a step fails
> - "Must be an Owner of the subscription" -> re-check the Owner role above.
> - "Account not eligible" -> you are likely on a personal account; switch to your work account.
> - "Insufficient credits" -> check your remaining MfS Azure credits.

Fill the real GitHub step labels from the flow you grounded in step 3. The GitHub connection itself is the founder's own click-path — you produce the checked, personalized guide; the founder performs the connection.

### 5. Write memory

Persist the subscription id, the founder's object-id, the GitHub org, and the Owner-role result to `memory/founder.md`.

## Never

- Never assert the founder has Owner without the delegated role read — check it.
- Never fabricate the `az role assignment list` syntax — ground it via Learn.
- Never recite a remembered GitHub UI flow — ground the current steps against `docs.github.com`.
- Never perform the GitHub connection yourself — you check and guide; the founder connects.
