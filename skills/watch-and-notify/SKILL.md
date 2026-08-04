---
type: skill
title: "Watch and notify — arm a watch for an async outcome"
created: 2026-06-07T00:00:00Z
updated: 2026-06-08T00:00:00Z
tags: [azure, async, watch, quota, notify, durable]
origin: operator
---

# Watch and notify

## When to run this

The founder is waiting for an async outcome — a quota grant, a long-running
deployment, a support ticket resolution, a capacity change. Run this skill to arm a
durable watch: record what's being waited for, where the proof will land, and how to
re-check when the founder returns.

The quota case is the primary use case: after `skills/request-quota/SKILL.md`
submits a form, this skill creates the durable note that bridges the gap between
"submitted" and "granted".

## The discipline

There is no background scheduler. This is a **durable note + a re-check protocol** —
honest about being manual. That is the right design for now: it is simple, reliable,
and does not create false confidence.

### 1. Record what's being watched

Write a durable note to `memory/watch-<slug>-<YYYY-MM-DD>.md` with the following
sections. Fill them from context — do not leave placeholders:

- **What:** the specific outcome being waited for. For a quota grant: the model,
  region, and requested TPM. Example: "gpt-4o quota grant — East US — 300,000 TPM".
- **Why:** the founding ask that triggered this watch.
- **Where proof lands:** the expected artifact path once the outcome arrives. For
  quota: `artifacts/quota/<date>-<slug>-quota-proof.md` and
  `artifacts/quota/<date>-<slug>-quota-screenshot.png`.
- **Expected timeframe:** the MFS quota form's own confirmation page states quota
  increases are **"typically processed the next business day after submission,
  sometimes up to two business days,"** filled in the order received — and that
  **submission does not guarantee the increase will be fulfilled.** Use that language
  verbatim; do not invent a different number or imply a guarantee.
- **How to re-check:** the exact command to confirm the quota grant once the founder
  reports it's been approved. Confirm the exact syntax via Learn before recording it:
  ```
  az cognitiveservices usage list --location <region> --subscription <sub>
  ```
  This is a Tier-0 read — delegate to the Executor, do not run it yourself.
- **Status:** `pending`. Update to `granted` / `complete` when the outcome lands and
  has been confirmed by a live Tier-0 read.

Then add a line to `MEMORY.md` (re-read it first; name only the path, never a commit
hash). The watch file is how the advisor finds the context when the founder returns.

### 2. Tell the founder what to do when it lands

Give the founder a clear, one-sentence protocol — not a menu:

> "When the grant email arrives (or when the portal shows the new quota), come back
> here and tell me — I'll confirm it's live and update your records."

If they ask how long it will take: "The form says quota increases are typically
processed the next business day, sometimes up to two business days — and a request
isn't guaranteed to be granted. I'll confirm the moment you tell me it's landed."

Do not speculate about the outcome or set expectations on grant size.

### 3. Re-check on founder return

When the founder returns and reports the quota was approved:

1. Read `memory/watch-<slug>-<YYYY-MM-DD>.md` to recover context.
2. Delegate a Tier-0 read to the Executor (the command recorded in the watch note).
   Confirm the usage output shows the new quota level. **Do NOT mark complete from
   the founder's assertion alone** — the live read is the authority.
3. Update the watch note's status to `granted`, add the confirmed quota value and the
   date confirmed.
4. Update `MEMORY.md` if the durable state of this founder's environment has changed
   (a new quota ceiling, a changed deployment limit).
5. Tell the founder the confirmed value and, if a proof artifact was expected, read it
   back.

## Never

- Never assert an async outcome has landed without a live Tier-0 read via the
  Executor.
- Never promise the increase WILL be granted — the form states submission does not
  guarantee fulfillment. Quote the form's "next business day, up to two business days"
  timeframe; do not invent a different one.
- Never create a watch note without recording the re-check command and the artifact
  path.
- Never fabricate the `az cognitiveservices` re-check syntax — look it up via Learn.
- Never pretend there is a background scheduler — this is a manual re-check protocol,
  and that is fine and honest.
