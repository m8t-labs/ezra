---
type: reference
title: "Send email — the outbound-email contract"
created: 2026-06-22T00:00:00Z
updated: 2026-08-11T00:00:00Z
tags: [notify, email, seam, reference]
origin: operator
---

# Send email — outbound-email contract

> **Wired** — the Executor's ACS Email send actuator consumes this block. It mirrors
> `references/quota-form-fieldmap.md` / `<m8t:quota_form>`:
> Executor-actuated, owner-gated, proof to the brain.

The block is named `<m8t:notify_advisor>` for compatibility with every deployment already
running. It is not advisor-specific: `to` is **any** address the owner asked you to write to.

## The block

```
<m8t:notify_advisor>
to:            the recipient's address — anyone the owner named, not one fixed contact
owner_email:   the person who installed this platform — ALWAYS CC'd, so they see what is sent for them
reply_to:      where replies should land (optional — defaults to owner_email)
from_label:    "<name> via their Azure agent" (rendered into the subject prefix + body footer; the managed-domain From cannot carry a custom sender display name)
subject:       clean subject — strip any RE:/FWD:
body:          the message, rendered
attachments:   optional brain artifact paths (v1: referenced in body)
mode:          prepare | submit
</m8t:notify_advisor>
```

`founder_email` is still accepted as a name for `owner_email`, and `recipient` for `to`.
Prefer the names above; the aliases exist so older blocks keep working.

## Fields name their function, not a job title

`owner_email` is whoever installed the platform — founder today, an owner or an admin
tomorrow. `to` is whoever the message is for. Neither is tied to a program or a role.
A field named after a person's title goes stale the first time the person changes.

## Executor parse

The Executor reads the self-contained block — it cannot ask follow-up questions mid-task
(same rule as `<m8t:quota_form>`). **Every field the send needs must be present in the
block.** It cannot look anything up for you and it will not guess.

Required: `to`, `owner_email`, `subject`, `body`. `reply_to` is optional — absent, replies
go to `owner_email`.

**Never emit this block with a required field left blank.** If you are missing an address,
ask the owner for it and emit the block once you have it. A blank field produces a failed
send and a confusing report; a question produces the address.

The Executor reports any field name it did not recognise, so a near-miss name surfaces
instead of vanishing. Do not rely on that — use the names above.

## Owner gate (prepare / submit)

Outbound email is outward-facing and must be gated, exactly like the quota form:

- **Decisive phrasing** ("send it", "email them") -> `mode: submit`.
- **Tentative phrasing** ("draft the note", "show me first") -> `mode: prepare`.
- **Ambiguous** -> ask exactly once: "Want me to send this now, or show you the draft
  first so you can approve it?"

`prepare` composes the message and shows the owner the draft; `submit` sends only on
explicit approval.

## The owner is always copied

`owner_email` is CC'd on every send, and that is not negotiable from the block. Redirecting
`reply_to` changes where replies land; it never removes the owner's copy. The owner sees
everything sent in their name.

## Proof convention

Delivered to `artifacts/notify/` in the brain:

- `<date>-<slug>-notify-proof.md` — records: status (`sent` / `prepared` / `failed`),
  to, cc (= owner), reply-to, from_label, subject, body, acting identity, any unrecognised
  field names, and — on `sent` — the ACS message-id.
- the rendered draft.

Report from the proof — never claim "sent" unless the proof records it.
