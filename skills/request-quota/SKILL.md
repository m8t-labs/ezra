---
type: skill
title: "Request quota — MFS OpenAI quota-request play (form wired)"
created: 2026-06-07T00:00:00Z
updated: 2026-06-08T00:00:00Z
tags: [azure, quota, mfs, form, delegation]
origin: operator
---

# Request quota

> The MFS OpenAI quota-request form at `aka.ms/oai/stuquotarequest` is wired: the
> Executor fills + submits it in a headless browser and returns proof-of-submission.
> See `references/quota-form-fieldmap.md` for the exact fields + happy-path branch.
> When the founder has a Microsoft Startup Advisor on file (`memory/founder.md`), you
> **also** email them the filled request so a human can push it — file the form first
> (Step 5), then send the SA email (Step 6). Both run under the one gate in Step 4.
> Doctrine: `memory/startup-advisor-escalation.md`.

## When to run this

The founder wants more Azure OpenAI quota — TPM, RPM, or PTU — for a specific model
and region. They may say "I'm hitting my quota", "I need more capacity for gpt-4o",
"request more OpenAI quota", or simply "bump my quota".

## The discipline

**Check → gather → justify → delegate → prove → watch — in that order.**

### 1. Check current usage FIRST (never promise from memory)

Before quoting any number, delegate a Tier-0 read to the Executor to ground actual
usage and quota for the model + region in question:

```
az cognitiveservices usage list --location <region> --subscription <sub>
```

Confirm the exact syntax via Microsoft Learn before including it in the delegation.
This is the gpt-5.5-zero-quota lesson — see `memory/quota-and-mfs-reality.md` for
the MFS quota ceiling and the difference between a deployment-level limit and a
subscription-level capacity limit. Never assert a quota value from memory.

### 2. Gather the founder's form fields

Read `memory/founder.md`. The form requires:

- **Personal:** First Name, Last Name, Company Email
- **Company:** Company Name, Company Address, Company City, Company Postal Code,
  Company Country
- **Azure:** Subscription Id
- **Request:** Model, Region, Requested Quota (TPM), Justification

The company-address fields (Address, City, Postal Code, Country) are often NOT yet
recorded in `memory/founder.md`. If any required field is missing, ask ONE round of
clarifying questions covering all the gaps at once — never ask field-by-field. Then
persist every answer to `memory/founder.md` (the usual way: re-read the file, add the
fields, write it back) so the next request is zero-friction.

Subscription Id should already be in `memory/founder.md` from the advisor onboarding
— do not ask for it again if it is present.

### 3. Compose the justification (Learn-grounded framing)

Ground justification framing via Microsoft Learn: search what MFS reviewers look for
(production use case, current vs. needed TPM, concurrent users, launch timeline). Then
write a crisp single paragraph that weaves:
- The founder's current usage (from the Executor read in Step 1).
- The gap between current quota and what's needed.
- The production use case and user volume.
- Launch stage or timeline if known from `memory/founder.md`.

A compelling justification is the difference between a fast grant and a slow one.

### 4. Decide submit vs prepare (intent-driven — ask once if ambiguous)

Read the founder's intent from the conversation. **One decision drives both the form
submission (Step 5) and the Startup-Advisor email (Step 6)** — the founder approves the
quota ask once, not twice.

- **Decisive phrasing** ("submit my quota request", "go ahead and request it", "bump
  my quota") → use `mode: submit` for both.
- **Tentative phrasing** ("prepare a quota request", "draft it", "fill it in so I
  can review it") → use `mode: prepare` for both (form screenshot + email draft shown
  together; send on approval).
- **Ambiguous** → ask exactly once: "Want me to submit the request in your name — I'll
  file the form and email your Microsoft Startup Advisor the request — or fill it in and
  show you first so you can approve?"

There is **no shareable pre-filled link** — the browser runs server-side and state is
session-local. "Review first" means the Executor screenshots the filled form; on the
founder's approval, a second delegation re-fills and submits. Be honest about this if
asked.

### 5. Delegate to the Executor

Call `invoke_worker(target:"ezra-executor", task:<below>)`. The task block must be
fully self-contained — the Executor cannot ask follow-up questions mid-task.

```
<m8t:quota_form>
first_name: <value>
last_name: <value>
company_email: <value>
company_name: <value>
company_address: <value>
company_city: <value>
company_postal_code: <value>
company_country: <value>
subscription_id: <value>
model_type: Azure OpenAI
deployment_type: Model Deployment (PTU/RPM/TPM)
quota_request_type: Global Standard
model: <model, e.g. gpt-4o>
region: <region, e.g. East US>
requested_quota: <TPM number>
mode: submit
justification: |
  <one paragraph>
</m8t:quota_form>
```

Pass `inputs:"brain:memory/founder.md"` and `deliver_to:{pathPrefix:"artifacts/quota/"}` as **tool arguments** — the `<m8t:quota_form>` block stays in the task text; the repo is always your brain.

Important: put `justification: |` **last** in the block — it consumes the lines that
follow until the closing tag.

See `references/quota-form-fieldmap.md` for the exact field labels, the happy-path
branch (Azure OpenAI / Global Standard), and the two load-bearing gotchas.

**Cold-start:** if the first invocation returns `storage_error` (the op did NOT run —
the Executor's container pays `az login` latency on the first turn), retry once before
surfacing an error.

### 6. Also email the Startup Advisor the filled request

Filing the form puts the request in Microsoft's queue; the **Microsoft Startup Advisor
(SA)** is the human who can push it. So after the form delegation, **also email the SA the
same request**. Read the recipient from `memory/founder.md`: the
`**Microsoft Startup Advisor (SA):**` bullet is the `to:` address and
`**Founder email (company_email):**` is the `founder_email`. Follow the packaging
discipline in `references/advisor-handoff.md` and delegate a `<m8t:notify_advisor>` send to
the Executor (contract: `references/notify-advisor-contract.md`):

`invoke_worker(target:"ezra-executor", task:<the block below>, deliver_to:{pathPrefix:"artifacts/notify/"})`

```
<m8t:notify_advisor>
to: <SA email from memory/founder.md>
founder_email: <company_email from memory/founder.md>
from_label: <founder name> via their Azure agent
subject: Azure OpenAI quota increase request — <model> in <region>
mode: <same mode as the form in Step 4>
body: |
  I'm requesting an Azure OpenAI quota increase and would value your help pushing it through.

  - Model: <model>
  - Region: <region>
  - Current usage / quota: <from the Step 1 usage read>
  - Requested quota (TPM): <number>
  - Subscription: <subscription_id>

  Justification: <the one-paragraph justification from Step 3>

  I've also filed this through the official Microsoft for Startups quota request
  form (aka.ms/oai/stuquotarequest), so it's in the standard queue — anything you
  can do to expedite or advocate for it internally is appreciated.
</m8t:notify_advisor>
```

- **One gate, both sends.** Use the **same `mode`** you chose in Step 4. Put `body: |` LAST
  in the block — it consumes the lines that follow until the closing tag.
- **The form errored?** Still email the SA — a human can file it. Say so in the body ("the
  automated form submission hit an error; details in the proof") instead of the "also filed"
  line. Do not block the human ask on the robot form.
- **No SA on file?** Skip this step. Tell the founder: "I filed the official request. I
  couldn't also email your Microsoft Startup Advisor because I don't have their email — add
  it via `m8t bootstrap seed-profile` and I'll loop them in next time." Never invent a
  recipient.
- **Cold-start:** if the first invocation returns `storage_error` (the op did NOT run),
  retry once before surfacing an error.

### 7. Present the proof honestly

Read **both** proofs — the form proof from `artifacts/quota/` and (when you emailed the SA)
the send proof from `artifacts/notify/` — and report each honestly.

The form (`artifacts/quota/`):

- **submitted** → "Submitted in your name — proof saved at `artifacts/quota/<file>`.
  I'll tell you when it's approved."
- **prepared** → "Filled the form but did not submit — here is the screenshot. Say
  'go ahead and submit' when you're ready."
- **incomplete** → "Could not submit — the following required fields were missing:
  `<list>`. Please provide them so I can try again."
- **failed** → "The form runner encountered an error — see the proof for details. NOT
  submitted."

The SA email (`artifacts/notify/`), when sent:

- **sent** → "Emailed your Microsoft Startup Advisor the request (you're CC'd) — proof at
  `artifacts/notify/<file>`."
- **prepared** → "Drafted the email to your advisor — here it is. Say 'send it' when ready."
- **failed / not provisioned** → surface it honestly; the form is still filed.

Never claim "submitted" unless the form proof records `status: submitted`, and never claim
the advisor was emailed unless the notify proof records `status: sent`. The Executor is the
authority on what happened — the advisor reports, not assumes.

### 8. Arm the watch

Run `skills/watch-and-notify/SKILL.md` immediately after a successful submission to
record the pending grant and set the re-check protocol. Do not skip this — async
grants need a durable note or the founder has no path back.

## Never

- Never promise a quota value without a live usage read from the Executor.
- Never claim "submitted" unless the form proof says so — it may be `prepared` or
  `incomplete`.
- Never claim you emailed the Startup Advisor unless the notify proof records `status: sent`.
- Never invent the SA's email — read it from `memory/founder.md`, or degrade honestly and
  file the form alone.
- Never fabricate `az cognitiveservices` syntax — look it up via Learn.
- Never skip the watch after a submission.
- Never ask for Subscription Id if it is already in `memory/founder.md`.
