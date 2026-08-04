---
type: skill
title: "AOAI unblock — diagnose and escalate an Azure OpenAI abuse-monitoring block"
created: 2026-06-23T00:00:00Z
updated: 2026-06-23T00:00:00Z
tags: [azure, openai, abuse-monitoring, 403, escalation, class-b]
origin: operator
---

# AOAI unblock

> When Azure OpenAI abuse monitoring blocks a subscription, every AOAI call
> returns HTTP 403. Lifting the block is a Microsoft Responsible AI review
> decision — you diagnose it, assemble the evidence, and hand off an
> advisor-ready package. You do not lift the block and you do not contact the
> review team directly.

## When to run this

The founder reports that **all** their Azure OpenAI calls suddenly return HTTP
403 — across multiple deployments or regions at once — and it is not an
authentication failure or a quota/rate problem. This is an abuse-monitoring
block, distinct from an RBAC permission 403 (that is `skills/azure-triage/SKILL.md`).

## The discipline

**Ground the mechanism → confirm it is an abuse block → gather the evidence → drive the public filing (only if eligible) → assemble the package → hand off → arm a watch.**

### 1. Ground the block mechanism + the current public route

Call the Microsoft Learn MCP first — do not answer from memory. Ground how Azure
OpenAI content-filtering / abuse monitoring blocks a subscription, and the
*current* public remediation route (`microsoft_docs_search` →
`microsoft_docs_fetch`). Quote the relevant passage and link it.

### 2. Confirm it is an abuse-monitoring block (not auth, not quota)

Ask the founder for the exact failed response — the status code, any `Retry-After` header (its presence points at a 429 rate-limit, not a block), and the response body:
- **403 with a "blocked" / "abuse" / "responsible AI" reason** → an abuse-monitoring block; proceed.
- **403 "key missing" / "auth failed" / "invalid subscription key"** → an auth problem, not this skill; redirect to `skills/azure-triage/SKILL.md`.
- **429** → rate/quota, not a block; redirect to `skills/quota-diagnose/SKILL.md`.

Do not assemble an unblock package until the 403 is confirmed as an abuse block.

### 3. Gather the evidence (intake + an Executor account-context read)

Gather from the founder (ask once; persist durable bits to `memory/founder.md`):
- the **use case** — what they are building on Azure OpenAI;
- **sample blocked prompts**, **sanitized by the founder** (instruct them to remove secrets and personal data);
- the **remediation plan** — what they will change (content-filter configuration, prompt changes, downstream filtering).

Then delegate a **Tier-0 read** to the Executor for account context (subscription
id, AOAI resource name(s), region(s), deployments). Learn-verify the exact
`az`/SDK read syntax before delegating — never fabricate it. Delegate via
`discover_workers` → `invoke_worker(target:"ezra-executor", task:<the account-context read instruction>, inputs:"brain:memory/founder.md", deliver_to:{pathPrefix:"artifacts/azure/"})` — pass inputs + deliver_to as tool arguments (the repo is always your brain).

**Cold-start:** if the first invocation returns `storage_error` (the op did NOT
run), retry once before reporting failure.

### 4. Drive the public filing — only if the founder is eligible

Lifting an abuse-monitoring block is reviewed by Microsoft; the public channel is
an Azure support request. **A support request needs an eligible Azure support
plan** — most Microsoft for Startups sponsorship subscriptions are on the basic
plan and cannot open a technical support request. So:
- If the founder **has** an eligible support plan, guide them to open the request
  themselves in the Azure portal (Help + Support → Create a support request → the
  Azure OpenAI service), Learn-grounding the current path.
- If they **do not**, say so plainly — the assembled evidence package routed
  through their advisor is the path. **You never file the ticket via the Executor**
  (it cannot create a support ticket on a basic-plan subscription).

### 5. Assemble + save the evidence bundle

Write the advisor-ready evidence bundle to
`artifacts/azure/<YYYY-MM-DD>-aoai-unblock-evidence.md` in the brain. Include:
- the use case;
- the affected subscription id + AOAI resource name(s) + region(s) (from the read);
- the sanitized blocked-prompt sample(s);
- the exact 403 evidence (status + body proving it is a block, not 429/auth);
- the remediation plan;
- the Microsoft for Startups account context (tier, what they are building).

### 6. Escalate — emit the advisor handoff

Lifting the block is a Microsoft Responsible AI review decision you cannot make or
expedite. Follow `references/advisor-handoff.md` and emit:

```
<m8t:advisor_handoff>
attempted:    Learn-grounded diagnosis (confirmed abuse block, not auth/quota) + the Executor account-context read (cite the proof artifact path)
blocked:      lifting an Azure OpenAI abuse-monitoring block is a Microsoft Responsible AI review decision — only a Microsoft advisor can raise it for expedited review
package:      the assembled evidence bundle at artifacts/azure/<YYYY-MM-DD>-aoai-unblock-evidence.md (use case, account context, sanitized prompts, 403 evidence, remediation plan)
recipient:    the founder's MfS advisor from memory/founder.md (degrade to a generic recipient if unknown)
next_action:  open a Responsible AI re-review with the attached evidence bundle to lift the block
</m8t:advisor_handoff>
```

### 7. Arm a watch for restoration

The founder is now waiting on an async outcome (the block being lifted). Read
`skills/watch-and-notify/SKILL.md` and run it — record what is being watched and
the re-check protocol, so you confirm restoration with a live read when the
founder returns.

## Never

- Never claim you contacted the Responsible AI team, lifted the block, or spoke to Microsoft directly — you assemble the package; a human advisor raises it.
- Never file the support ticket via the Executor — a basic-plan subscription cannot create one; guide the founder if eligible, otherwise hand off.
- Never fabricate `az` syntax or the public support path — Learn-verify both.
- Never include unsanitized prompts, secrets, or personal data in the evidence bundle.
- Never forward a raw founder question as the handoff — assemble the evidence bundle first.
