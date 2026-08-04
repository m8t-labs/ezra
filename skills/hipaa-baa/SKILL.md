---
type: skill
title: "HIPAA BAA — guide an HCLS founder to a Business Associate Agreement"
created: 2026-06-22T00:00:00Z
updated: 2026-06-22T00:00:00Z
tags: [hipaa, baa, compliance, hcls, class-b]
origin: operator
---

# HIPAA BAA

## When to run this

A Healthcare / Life-Sciences founder asks about HIPAA compliance — "do you sign a BAA?", "we handle PHI, are we covered?", "how do we get a HIPAA Business Associate Agreement?".

## The discipline

**Establish the MCA-E prerequisite (intake) → ground the eligible services (Learn) → draft the reply → hand off if it is genuinely complex.**

### 1. The load-bearing prerequisite: MCA-E

The HIPAA BAA from Microsoft is **an amendment to the Microsoft Customer Agreement, Enterprise (MCA-E)** — NOT a standalone agreement. The customer MUST be on a signed MCA-E first. A founder still on sponsorship-only / Founders Hub credits with no MCA-E cannot get a standalone BAA.

Check status by asking the founder directly (this is intake, not a lookup): "Are you on a signed MCA-E, or on sponsorship credits only right now?" Persist the answer to `memory/founder.md`.

- **No MCA-E** -> state plainly that MCA-E is the prerequisite, that you cannot promise a standalone BAA, and that the path is to get onto MCA-E first. Do not hand off yet — this is the answer.
- **Has MCA-E** -> proceed.

### 2. Ground the HIPAA-eligible services (Learn, live)

When the founder names the Azure services their PHI-touching subsystems use, check each against the current HIPAA-eligible list via the Learn MCP — do NOT recite a remembered list (it goes stale). Start at `https://learn.microsoft.com/azure/compliance/offerings/offering-hipaa-us` and confirm each named service is eligible. Any subsystem touching PHI must rely on eligible services.

### 3. The BAA download path (public)

Once on MCA-E, the BAA template is downloadable from the Service Trust Portal (`https://servicetrust.microsoft.com`, Compliance section) and executed as an amendment to the MCA-E. The general Trust Center HIPAA page is `https://www.microsoft.com/en-us/trust-center/compliance/hipaa`.

### 4. Draft the founder reply

> Hi <founder>,
>
> Happy to help with the HIPAA BAA. Two things up front:
>
> 1. The HIPAA BAA from Microsoft is an amendment to the Microsoft Customer Agreement, Enterprise (MCA-E), not a standalone document. Your subscription needs to be on MCA-E for the BAA to apply.
> 2. If you are not yet on MCA-E (for example, still on sponsorship credits), we set that up first. Tell me your current commerce setup and I will point you at the path.
>
> Once on MCA-E, the BAA template is in the Service Trust Portal (Compliance section), executed as an amendment. A list of HIPAA-eligible Azure services is at learn.microsoft.com/azure/compliance/offerings/offering-hipaa-us — any subsystem touching PHI should use services from that list.
>
> Want me to check your specific architecture against the eligible-services list?

### 5. Hand off only when it is genuinely complex

If the case is beyond the self-serve path — complex multi-region PHI, a BAA chain with downstream processors, or a large customer that needs a Microsoft account or compliance specialist — assemble an advisor-ready handback rather than guessing. Follow `references/advisor-handoff.md` and emit:

```
<m8t:advisor_handoff>
attempted:    the MCA-E status you established + the eligible-services check you ran (cite the Learn page)
blocked:      the specific reason a Microsoft advisor is required (e.g. a downstream-processor BAA chain beyond the standard amendment)
package:      the assembled summary — architecture, PHI subsystems, services checked — + any brain artifact path
recipient:    the founder's MfS advisor from memory/founder.md (degrade to a generic recipient if unknown)
next_action:  the one concrete step the advisor takes with the package
</m8t:advisor_handoff>
```

## Never

- Never promise a standalone BAA — it is an MCA-E amendment; confirm MCA-E first.
- Never recite a remembered HIPAA-eligible-services list — ground it live via Learn.
- Never forward a raw question as a handoff — assemble the advisor-ready package first (`references/advisor-handoff.md`).
