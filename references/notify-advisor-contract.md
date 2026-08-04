---
type: reference
title: "Notify advisor — the outbound-email send contract"
created: 2026-06-22T00:00:00Z
updated: 2026-06-23T00:00:00Z
tags: [advisor, notify, email, seam, reference]
origin: operator
---

# Notify advisor — outbound-email contract

> **Wired** — the Executor's ACS Email send actuator consumes this block. It mirrors
> `references/quota-form-fieldmap.md` / `<m8t:quota_form>`:
> Executor-actuated, founder-gated, advisor address from memory, proof to the brain.

## The block

```
<m8t:notify_advisor>
to:            advisor address (from memory/founder.md; the advisor-handoff recipient)
founder_email: the founder's own email (company_email) — the actuator CCs it AND sets Reply-To to it
from_label:    "<founder> via their Azure agent" (rendered into the subject prefix + body footer; the managed-domain From cannot carry a custom sender display name)
subject:       clean subject — strip any RE:/FWD:
body:          the advisor-handoff package, rendered
attachments:   optional brain artifact paths (v1: referenced in body)
mode:          prepare | submit
</m8t:notify_advisor>
```

## Executor parse

The Executor reads the self-contained block — it cannot ask follow-up questions mid-task
(same rule as `<m8t:quota_form>`). Every field the send needs must be present in the block.

## Founder gate (prepare / submit)

Sending to a Microsoft advisor on the founder's behalf is outward-facing and must be gated,
exactly like the quota form:

- **Decisive phrasing** ("notify my advisor", "send it") -> `mode: submit`.
- **Tentative phrasing** ("draft the note", "show me first") -> `mode: prepare`.
- **Ambiguous** -> ask exactly once: "Want me to send this to your advisor now, or show you
  the draft first so you can approve it?"

`prepare` composes the message and shows the founder the draft; `submit` sends only on
explicit approval.

## Proof convention

Delivered to `artifacts/notify/` in the advisor brain:

- `<date>-<slug>-notify-proof.md` — records: status (`sent` / `prepared` / `failed`),
  to, cc (= founder), reply-to (= founder), from_label, subject, body,
  acting identity, and — on `sent` — the ACS message-id.
- the rendered draft.

The advisor reports from the proof — it never claims "sent" unless the proof records it.
