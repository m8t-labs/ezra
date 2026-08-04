---
type: skill
title: "Support routing — route + prepare a Founders Hub or Azure support ticket"
created: 2026-06-22T00:00:00Z
updated: 2026-06-22T00:00:00Z
tags: [support, founders-hub, ticket, routing, class-b]
origin: operator
---

# Support routing

## When to run this

The founder has a support issue and isn't sure where it goes — "my credits show
the wrong amount", "I was charged for usage I didn't expect", "my Founders Hub
login is broken", "is my sponsorship applied?", "how do I file a support ticket?".

## The discipline

**Classify the issue → route or draft the ticket → escalate to a human advisor only when warranted.**

### 1. Classify: Founders Hub support vs Azure support

| Issue | Route to |
|---|---|
| Azure technical break-fix (service down, errors, deployment fails) | Azure support |
| Credits mismatch / wrong amount showing | Founders Hub support |
| Unexpected / wrong usage charged | Founders Hub support |
| Founders Hub portal / login / account-profile issue | Founders Hub support |
| Tier or program-status question | Founders Hub support |
| Sponsorship not applied | Founders Hub support |

### 2. Azure-technical → route to triage

If the issue is an Azure technical break-fix, this is not a Founders Hub ticket.
Hand off to `skills/azure-triage/SKILL.md` to diagnose it, or guide the founder
to open an Azure support request in the Azure portal if it needs Microsoft
support to act.

### 3. Founders Hub issue → draft the ticket body

For a credits / billing / portal / program issue, produce a paste-ready ticket
body the founder submits through their Founders Hub portal. Intake any missing
identifiers (ask once, persist to `memory/founder.md` — never a lookup):

> ## Subject
> [one line — what is wrong]
>
> ## Description
> Expected: [what should be true]
> Actual: [what is happening]
> Steps to reproduce: [steps, if any]
>
> ## Affected account
> - Founders Hub account ID: [id]
> - Microsoft for Startups tier: [tier]
> - Subscription ID(s): [ids]
>
> ## Urgency
> [Production-blocking / Time-sensitive / Standard]
>
> ## Attachments
> [screenshots, error messages]

### 4. Escalate to a human advisor only when warranted (conditional handoff)

You are the founder's day-to-day advisor — helping them file correctly is the
job, not handing the ticket to a human. Only when the founder is on a **managed
MfS tier with an assigned human advisor** AND the ticket has gone unanswered does
looping that advisor add value. That advisor is the founder's Microsoft Startup
Advisor — see `memory/startup-advisor-escalation.md`. In that case follow
`references/advisor-handoff.md` and emit:

```
<m8t:advisor_handoff>
attempted:    the routing decision (FH vs Azure) + the ticket body you drafted
blocked:      the ticket is unanswered and the founder is on a managed tier with an assigned advisor who can escalate
package:      the drafted ticket body + the ticket id/age + the affected-account identifiers + any brain artifact path
recipient:    the founder's Microsoft Startup Advisor (the `**Microsoft Startup Advisor (SA):**` bullet in memory/founder.md; degrade to a generic recipient if unknown)
next_action:  escalate the unanswered ticket with the support team
</m8t:advisor_handoff>
```

## Never

- Never file an Azure-technical issue as a Founders Hub ticket — route it to `skills/azure-triage/SKILL.md` or Azure support.
- Never invent the founder's Founders Hub account ID, tier, or subscription — intake them.
- Never loop a human advisor by default — that is conditional on a managed tier with an assigned advisor and an unanswered ticket.
