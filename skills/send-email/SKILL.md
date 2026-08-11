---
type: skill
title: "Send email — compose, confirm, and send on the founder's behalf"
created: 2026-08-11T00:00:00Z
updated: 2026-08-11T00:00:00Z
tags: [email, notify, send, executor, advisor, outbound]
origin: operator
---

# Send email

## When to run this

The founder wants a message to reach a person by email. Any person — an advisor, an
account manager, a customer, a co-founder, someone they just named. "Send an email to
`<address>`", "email my advisor about this", "send them that summary."

Also run it at the end of an advisor handoff, once you have a real recipient — see
`references/advisor-handoff.md`.

You can do this. The Executor is the actuator; you compose the message and hand it over.
Never tell the founder you can't send email.

## The discipline

Three rules carry this whole play. The rest is mechanics.

**Ask rather than guess.** If you don't have an address, ask for it. Never invent one, and
never substitute a different recipient because they were easier to find in memory.

**Never emit a blank required field.** The Executor cannot ask you a follow-up question and
will not look anything up. A blank field is a failed send — and the failure reads as though
the founder forgot something, when they didn't.

**Say where replies land before you send.** You have no mailbox; Reply-To is the only route
back. State it, offer to change it, and refuse to send when there is none.

## Step 1 — resolve the recipient

Three cases, in order. Stop at the first that applies.

1. **They gave you an address** — use it verbatim. Don't look anything up, don't
   second-guess it, don't substitute someone from memory.
2. **They named a person or a role** — "my advisor", "our account manager", "Dana" — read
   the address out of memory. `memory/founder.md` holds the founder's own contacts, and any
   contact record under `memory/` is fair game.
   **Read for meaning, not for one exact label.** Bullet labels differ between installs:
   one record says `**Microsoft Startup Advisor (SA):**`, another says `**Advisor email:**`.
   A label you don't recognise is not the same as an address that isn't there.
3. **You can't find it** — ask: *"What's their email address?"* One question. Then send.

## Step 2 — settle Reply-To

You have no mailbox of your own. Reply-To decides where a reply actually lands, so it is
never a detail to skip.

It defaults to the founder's own email — the address the platform was installed with, in
`memory/founder.md`.

- **You have it.** Say where replies will go, and offer to change it:

  > "I'll send this to `<to>`. Replies will come back to `<reply_to>`. Good, or do you want
  > a different one?"

  Ask once. Take their answer. Then send.

- **You don't have it.** Do **not** send. Say the send needs a reply address, ask for one,
  and send once they give it. An email nobody can reply to is worse than no email.

The founder is CC'd on every send, always — including when they point Reply-To somewhere
else. That is how they stay in the loop on what goes out in their name. Say so if they ask;
don't offer to turn it off.

## Step 3 — gate the send

- Decisive ("send it", "email them") → `mode: submit`.
- Tentative ("draft it", "show me first") → `mode: prepare`.
- Ambiguous → ask exactly once: *"Want me to send this now, or show you the draft first?"*

`prepare` composes and shows the draft. `submit` sends.

## Step 4 — delegate

Field names and the full contract: `references/notify-advisor-contract.md`.

```
<m8t:notify_advisor>
to: <the recipient, or several separated by commas>
founder_email: <the founder's own email from memory/founder.md — always CC'd>
cc: <anyone else to copy, separated by commas; omit if none>
reply_to: <where replies go; omit to default to founder_email>
from_label: <founder name> via their Azure agent
subject: <clean subject — strip any RE:/FWD:>
body: |
  <the message>
mode: submit
</m8t:notify_advisor>
```

`to` and `cc` each take several addresses separated by commas. The founder is added to CC
on top of whatever you put there — putting your own `cc` never removes their copy, and
listing them twice doesn't send it twice.

Use `founder_email` exactly as written. The contract's canonical name for it is
`owner_email` — it is the install owner's address, whatever their title — and both names
work, but only `founder_email` is understood by every Executor currently deployed. Emitting
the newer name against an older Executor silently empties the field.

`cc`, and more than one address in `to`, need a recent Executor. On an older one:

- `cc` is dropped silently and only the founder is copied.
- Several addresses in `to` are passed on as a **single** malformed address, so the send
  **fails** rather than reaching anyone.

So: read the recipients back off the proof (step 5). **If the proof's To or CC is missing
someone the founder asked for, say so** — never report a send as done when it reached fewer
people than they named. And if a send with several `to` addresses comes back `failed`, that
is the likely reason: say the Executor on this deployment can't do multiple recipients yet,
and offer to send them one at a time.

Call `invoke_worker(target:"ezra-executor", …)` with that block as the task text, and pass
`deliver_to:{pathPrefix:"artifacts/notify/"}` as a **tool argument** — the repo is always
your brain.

**Fill every required field: `to`, `owner_email`, `subject`, `body`.** The Executor reads
the block as-is. It cannot ask you a follow-up question and it will not look anything up.
A blank field is a failed send — and the failure reads as though the founder forgot
something, when they didn't. If you're missing a value, go back to step 1 and ask.

## Step 5 — report from the proof

Read the proof back from `artifacts/notify/` with `get_file_contents`.

- `status: sent` with a message-id → say it's sent, link the proof.
- `prepared` → show the draft and wait.
- `incomplete` or `failed` → say so plainly, and say what the proof says.

If the proof names an **unrecognised field**, you got a field name wrong. Fix the name and
retry. Do not report the address as missing — the founder gave it to you.

**Read Reply-To off the proof, not off what you intended.** If the proof's Reply-To is not
the address you confirmed with the founder, say so — an Executor that did not understand
the field is exactly the case where the founder would otherwise be told replies go somewhere
they don't.

Never claim "sent" unless the proof records it.

## Never

- Never invent an address.
- Never emit the block with a required field blank.
- Never send without a reply address on file.
- Never substitute a different recipient because one was easier to find in memory.
