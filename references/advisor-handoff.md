---
type: reference
title: "Advisor handoff — the standard advisor-ready handback block"
created: 2026-06-22T00:00:00Z
updated: 2026-06-23T00:00:00Z
tags: [advisor, handoff, escalation, reference]
origin: operator
---

# Advisor handoff

When a play hits a wall only a human Microsoft advisor can clear, do **not** forward a raw
question. Assemble an advisor-*ready* package: the diagnosis you already did, the exact
gate, and the artifact the advisor needs to act in one step. A finished package is *less*
work for the advisor than a cold ping — that is the whole point.

## The block

Emit this block (renders to the founder/operator today; an outbound-email backend can send
it later — see `references/notify-advisor-contract.md`):

```
<m8t:advisor_handoff>
attempted:    what you already did — Learn-grounded diagnosis, Executor reads run, public action driven
blocked:      the specific human-only wall + WHY a Microsoft advisor is required (the exact gate, not "I can't")
package:      the assembled, advisor-ready artifact (evidence bundle / pre-filled appeal / draft) + brain artifact path
recipient:    the founder's Microsoft Startup Advisor (the `**Microsoft Startup Advisor (SA):**` bullet in memory/founder.md; degrade to a generic recipient if unknown)
next_action:  the one concrete step the advisor should take with the package
</m8t:advisor_handoff>
```

## Field discipline

- **attempted** — concrete, past-tense: what was diagnosed, read, or driven. Cite the Learn
  source(s) and any Executor proof artifact path.
- **blocked** — name the *specific* human-only gate (e.g. "only a Microsoft advisor can
  approve the partner-vetting exception"), never a vague "I can't help further."
- **package** — the assembled artifact, plus the brain path where its evidence lives
  (`artifacts/...`). This is what makes the handback advisor-ready.
- **recipient** — read `memory/founder.md` for the founder's Microsoft Startup Advisor (the
  `**Microsoft Startup Advisor (SA):**` bullet). If unknown, say so and degrade to a generic
  recipient; do not invent an address. Doctrine: `memory/startup-advisor-escalation.md`.
- **next_action** — the single step the advisor takes next.

## Offering the send (outbound email)

After you emit `<m8t:advisor_handoff>`, **if `recipient` is a real email address**, offer
to send it — do not just render to the operator:

- Read the founder's own email (`company_email` in `memory/founder.md`).
- Honor the founder gate: decisive ("send it", "notify my advisor") → `mode: submit`;
  tentative ("draft it", "show me first") → `mode: prepare`; ambiguous → ask exactly once:
  "Want me to send this to your advisor now, or show you the draft first?"
- Delegate the send to the Executor with the mapping:
  `recipient`→`to`, the founder's `company_email`→`founder_email`, a clean play-derived
  subject→`subject`, the handoff `package`→`body`. The Executor always CCs the founder and
  sets Reply-To to the founder — so you stay in the loop and any reply reaches you.

```
<m8t:notify_advisor>
to: <recipient>
founder_email: <company_email from memory/founder.md>
from_label: <founder name> via their Azure agent
subject: <clean subject>
body: |
  <the rendered advisor-handoff package>
mode: submit
</m8t:notify_advisor>
```

Pass `deliver_to:{pathPrefix:"artifacts/notify/"}` as a **tool argument** — the `<m8t:notify_advisor>` block stays in the task text; the repo is always your brain.

- Report honestly from the proof in `artifacts/notify/`: only say "sent" if the proof
  records `status: sent` with a message-id. `prepared` → show the draft and wait. If the
  Executor reports email is **not provisioned**, or `recipient` is unknown/generic, do NOT
  claim a send — render the handoff to the founder/operator as before.

## Never

- Never forward a raw founder question as a handoff — assemble the package first.
- Never claim a human will act; you produce the advisor-ready artifact, the founder/advisor acts.
- Never invent the recipient — read it from memory or degrade honestly.
