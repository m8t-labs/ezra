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
recipient:    the owner's Microsoft advisor, read from memory/founder.md (see "Reading the recipient" below; ask if it isn't recorded)
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
- **recipient** — read `memory/founder.md` for the owner's Microsoft advisor. If it isn't
  recorded, say so and ask for the address; do not invent one and do not leave it blank.
  Doctrine: `memory/startup-advisor-escalation.md`.
- **next_action** — the single step the advisor takes next.

## Reading the recipient

`memory/founder.md` records the owner's contacts, but the exact bullet labels differ
between installs — one may say "Microsoft Startup Advisor (SA)", another "Advisor email".
**Read it for meaning, not for one exact string.** A label you don't recognise is not the
same as an address that isn't there.

If the record genuinely has no advisor, ask for the address. Never leave `recipient` blank
on the assumption something downstream will fill it — nothing will.

## Offering the send (outbound email)

After you emit `<m8t:advisor_handoff>`, **if `recipient` is a real email address**, offer
to send it — do not just render to the operator:

- Read the owner's own email from `memory/founder.md` — the address the platform was
  installed with. It is the CC and the default Reply-To.
- Honor the owner gate: decisive ("send it", "notify my advisor") → `mode: submit`;
  tentative ("draft it", "show me first") → `mode: prepare`; ambiguous → ask exactly once:
  "Want me to send this to your advisor now, or show you the draft first?"
- Confirm where replies land before sending, per `references/notify-advisor-contract.md`.
- Delegate the send to the Executor with the mapping:
  `recipient`→`to`, the owner's email→`owner_email`, a clean play-derived
  subject→`subject`, the handoff `package`→`body`. The Executor always CCs the owner, so
  you stay in the loop and any reply reaches you.

```
<m8t:notify_advisor>
to: <recipient>
owner_email: <the owner's email from memory/founder.md>
from_label: <owner name> via their Azure agent
subject: <clean subject>
body: |
  <the rendered advisor-handoff package>
mode: submit
</m8t:notify_advisor>
```

Fill every one of those fields. The Executor cannot ask you a follow-up question and will
not look anything up — a blank field is a failed send.

Pass `deliver_to:{pathPrefix:"artifacts/notify/"}` as a **tool argument** — the `<m8t:notify_advisor>` block stays in the task text; the repo is always your brain.

- Report honestly from the proof in `artifacts/notify/`: only say "sent" if the proof
  records `status: sent` with a message-id. `prepared` → show the draft and wait. If the
  Executor reports email is **not provisioned**, or `recipient` is unknown/generic, do NOT
  claim a send — render the handoff to the founder/operator as before.

## Never

- Never forward a raw founder question as a handoff — assemble the package first.
- Never claim a human will act; you produce the advisor-ready artifact, the founder/advisor acts.
- Never invent the recipient — read it from memory or degrade honestly.
