---
type: skill
title: "Quota diagnose — pre-flight an AOAI quota decision before filing"
created: 2026-06-22T00:00:00Z
updated: 2026-06-22T00:00:00Z
tags: [azure, openai, quota, diagnose, mfs, class-b]
origin: operator
---

# Quota diagnose

> The pre-flight for an Azure OpenAI quota decision. Most "I'm quota-blocked"
> asks fall into one of four buckets — run them BEFORE filing. Only an eligible
> case hands off to `skills/request-quota/SKILL.md` (the form-filling play).

## When to run this

The founder is blocked, denied, or unsure about Azure OpenAI quota — "I can't
get more gpt-4o quota", "my quota request was denied", "am I capped?", "is it
even worth asking for more quota?". This is the front door for quota; the actual
filing lives in `skills/request-quota/SKILL.md`, reached only from the eligible
branch below.

## The discipline

**Ground the ceiling → read current usage → walk the four buckets → route (eligible → request-quota) or hand off (EA-tier).**

Never assert a tier maximum or a current quota from memory — Learn the ceiling
and delegate the usage read.

### 1. Q1 — already at the Tier-5 maximum?

First confirm the target subscription + region from `memory/founder.md` (ask once
if absent) — you need both for the read. Learn the model + region Tier-5 maximum:
`https://learn.microsoft.com/azure/ai-foundry/openai/quotas-limits`. Then ground
the founder's actual current quota with a Tier-0 Executor read (Learn-verify the
exact syntax before delegating) — call `invoke_worker(target:"ezra-executor")`
with a self-contained task that runs:

```
az cognitiveservices usage list --location <region> --subscription <sub>
```

passing `inputs:"brain:memory/founder.md"` and `deliver_to:{pathPrefix:"artifacts/azure/"}` as tool arguments so the Executor has the founder context and writes proof (the repo is always your brain).

On a cold-start `storage_error` (the op did NOT run), retry once. If a recent
usage read is already in `memory/founder.md`, you may cite it instead of
re-delegating.

**If at the Tier-5 max → STOP. Do NOT file.** A standard quota request would be
denied. Recommend exactly one architecture move, Learn-grounded:
- distribute the workload across regions,
- put an APIM gateway in front for rate-limiting / retries,
- move to Provisioned Throughput Units (PTU) for predictable high throughput,
- or use batch deployments for non-realtime work.

### 2. Q2 — does the founder look EA-tier-capped?

You cannot read the internal EA-tier flag. But if the founder is on an MfS tier
that should grant more and the usage read shows a ceiling at the default sponsorship cap rather than what their MfS tier should grant, the
likely cause is an unset EA-tier flag — **a Microsoft-side action you cannot
perform.** Explain what EA-tier is, recommend the flip, and hand off (the
advisor-handoff block below). Never promise the flip.

### 3. Q3 — are they looking at the right UI?

Azure OpenAI quota lives in **Azure AI Foundry Studio → Quotas**, not the classic
Azure Portal Quotas blade (which does not surface some models). If they are
checking the wrong surface, point them to the right one.

### 4. Q4 — are they on the right subscription?

Some founders have multiple subscriptions and AOAI is provisioned on one. Confirm
the subscription by asking (intake — never a lookup); persist it to
`memory/founder.md` so you do not re-ask. If this reveals a different subscription than the Q1 read used, re-run the usage read on the confirmed subscription before deciding.

### 5. Eligible → hand off to request-quota

If Q1 = not at max, the subscription + UI are correct, and they genuinely need
more than their current standard cap, they are eligible to file. Read
`skills/request-quota/SKILL.md` and run it — it re-grounds current usage, gathers
the form fields, composes the justification, and fills + submits the MFS OpenAI
quota form via the Executor. Tell the founder you are filing, then follow that
skill.

### 6. The EA-tier handoff (Q2 only)

When Q2 is the diagnosis, follow `references/advisor-handoff.md` and emit:

```
<m8t:advisor_handoff>
attempted:    the Tier-5-max Learn check + the Executor usage read (current quota vs the tier ceiling)
blocked:      the EA-tier flag is a Microsoft-side action — only the founder's MfS advisor can set it
package:      the founder's MfS tier + current vs expected quota by model/region + the usage-read artifact path
recipient:    the founder's MfS advisor from memory/founder.md (degrade to a generic recipient if unknown)
next_action:  set the EA-tier flag on the subscription, then the founder can file a standard increase
</m8t:advisor_handoff>
```

## Never

- Never assert a tier maximum or current quota from memory — Learn the ceiling, delegate the read.
- Never file (or hand off to request-quota) when the founder is already at the Tier-5 max — recommend an architecture change instead.
- Never perform the EA-tier flip yourself — it is a Microsoft-side action; hand off.
- Never fabricate `az cognitiveservices` syntax — Learn-verify it before delegating.
