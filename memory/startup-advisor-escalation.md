---
type: memory
title: "Startup-advisor escalation — the SA is the Microsoft escalation contact"
created: 2026-07-01T00:00:00Z
updated: 2026-07-01T00:00:00Z
tags: [escalation, advisor, notify, quota, mfs]
origin: operator
---

# Startup-advisor escalation

The founder's **Microsoft Startup Advisor (SA)** — name + email in `memory/founder.md`
(the `**Microsoft Startup Advisor (SA):**` bullet) — is your one named human inside
Microsoft. When a need can only be met by a human decision at Microsoft, the SA is who you
reach, by email, on the founder's behalf. This note is the *when/why*; the *mechanics* live
in `references/advisor-handoff.md` (assembling the package) and
`references/notify-advisor-contract.md` (the `<m8t:notify_advisor>` send).

## Loop the SA in (email them, founder-gated)

- **Quota / credit-increase asks** — always email the SA the filled request *alongside*
  filing the official form (`skills/request-quota/SKILL.md`). The form is the tracked system
  of record; the SA is the human who can push it.
- **Exceptions only Microsoft can grant** — a partner-vetting exception
  (`skills/vetting-escalate/SKILL.md`), an Azure OpenAI human-review unblock
  (`skills/aoai-unblock/SKILL.md`), a policy exception.
- **Microsoft-internal walls** — an unanswered support ticket on a managed tier
  (`skills/support-routing/SKILL.md`), or any play whose next step only a Microsoft advisor
  can open.
- **"I don't have the answer and Microsoft has to decide."**

## Handle it yourself (no SA)

Tier-0 reads, cost reads, architecture advice, doc lookups, Tier-1 provisioning via the
Executor, and drafting a ticket/form the founder submits themselves. Escalating a routine
task the founder did not ask to escalate wastes the SA relationship — reach for them only
when the wall is genuinely Microsoft-only.

## Always

- **Founder-gate every outbound send** — decisive ("send it") → `mode: submit`; tentative
  ("draft it / show me first") → `mode: prepare`; ambiguous → ask exactly once. No silent
  email.
- **Read the SA from `memory/founder.md`; never invent a recipient.** If the SA bullet is
  blank (the founder skipped it at onboarding), say so and degrade — do the part you can
  (e.g. file the form), and tell the founder they can add the SA by running
  `m8t bootstrap profile --advisor-name "<name>" --advisor-email <email>` so you can loop
  them in next time. (`seed-profile` only re-publishes what has already been collected —
  it cannot ask for anything, so it can never fill a blank on its own.)
- The Executor CCs + sets Reply-To to the founder on every send, so the founder stays in the
  loop.
- **Report only from the proof** in `artifacts/notify/` — never claim "sent" without a
  `status: sent` and a message-id.
