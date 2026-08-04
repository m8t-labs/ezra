---
type: skill
title: "Vetting escalate — work a Partner Center partner-vetting rejection"
created: 2026-06-23T00:00:00Z
updated: 2026-06-23T00:00:00Z
tags: [partner-center, vetting, verification, maicpp, escalation, class-b]
origin: operator
---

# Vetting escalate

> A founder is stuck or rejected in Partner Center partner vetting for the
> Microsoft AI Cloud Partner Program. You explain the verification type, guide
> the self-service appeal, and — if still blocked — hand off an advisor-ready
> appeal package. The escalation beyond self-service is a Microsoft-internal
> channel you cannot open directly.

## When to run this

The founder enrolled in the Microsoft AI Cloud Partner Program (or changed their
legal details) and Partner Center verification rejected them or left them stuck —
"our business verification was rejected", "domain verification keeps failing",
"we're flagged in compliance screening", "our vetting is stuck".

## The discipline

**Explain the verification type → guide the self-service appeal → assemble the appeal package → hand off if still blocked.**

### 1. Explain the verification type (Learn-grounded)

Partner Center vetting for the Microsoft AI Cloud Partner Program has distinct
checks. Classify the founder's rejection and explain it, grounded via the Learn
MCP (do not answer from memory):

| Type | What it checks |
|---|---|
| Domain Verification (DV) | ownership of the company's email domain |
| Business Verification (BV) | the business is a legitimate, registered entity |
| Do Not Engage / Trade Screening (DNE) | sanctions / trade-compliance screening |
| Human Due Diligence (HDD) | additional manual review when automated checks are inconclusive |

### 2. Guide the self-service appeal first

Partner Center has a customer-facing appeal / resubmission path — the founder can
act on it themselves, and that is the fastest route. Learn-ground the current
Partner Center verification-responses path and walk them through it: review the
specific rejection reason, correct it (matching legal name / address, a domain
they control, the right documents), and resubmit. Only assemble an advisor
handoff after self-service is exhausted or genuinely blocked.

### 3. Assemble the appeal package

Gather the fields (ask once; persist the durable bits to `memory/founder.md`),
and write the appeal package to `artifacts/vetting/<YYYY-MM-DD>-vetting-appeal.md`
in the brain:
- the company's legal details — legal entity name, registered address, primary contact;
- the verification type (DV / BV / DNE / HDD);
- the exact rejection reason / error text;
- the documents already submitted (incorporation certificate, business license, etc.);
- how long the founder has been waiting;
- the self-service appeal status — attempted? outcome?;
- a **drafted appeal / resubmission** — clean and complete, ready to submit.

### 4. Escalate — emit the advisor handoff

If self-service is exhausted and the founder is still blocked, escalation beyond
the Partner Center appeal goes through Microsoft's partner-vetting operations,
reached through the founder's Microsoft Startup Advisor — a Microsoft-internal
channel a founder cannot open directly (doctrine: `memory/startup-advisor-escalation.md`).
Follow `references/advisor-handoff.md` and emit:

```
<m8t:advisor_handoff>
attempted:    explained the verification type, guided the Partner Center self-service appeal, drafted the resubmission
blocked:      escalation beyond the Partner Center appeal goes through Microsoft's partner-vetting operations — a Microsoft-internal channel only a Microsoft advisor can open
package:      the assembled appeal package at artifacts/vetting/<YYYY-MM-DD>-vetting-appeal.md (legal details, verification type, rejection reason, documents, drafted appeal)
recipient:    the founder's Microsoft Startup Advisor (the `**Microsoft Startup Advisor (SA):**` bullet in memory/founder.md; degrade to a generic recipient if unknown)
next_action:  escalate the assembled appeal case to Microsoft's partner-vetting operations on the founder's behalf
</m8t:advisor_handoff>
```

## Never

- Never name an internal escalation alias, mailbox, internal SLA, or internal ticketing quirk — the founder-facing path is the Partner Center self-service appeal, then the advisor handoff.
- Never claim Microsoft or the advisor will approve the vetting — you produce the appeal package; the founder/advisor acts.
- Never invent the recipient — read `memory/founder.md` or degrade honestly.
- Never invent the founder's legal details or documents — intake them.
- Never forward a raw question as the handoff — assemble the appeal package first.

