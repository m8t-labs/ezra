---
type: reference
title: "MFS OpenAI quota form — field map + happy-path branch"
created: 2026-06-08T00:00:00Z
updated: 2026-06-08T00:00:00Z
tags: [azure, quota, mfs, form, reference]
origin: operator
---

# MFS OpenAI quota form — field map

Form: `aka.ms/oai/stuquotarequest` → a **public, anonymous** Dynamics 365 Customer
Voice form ("Microsoft Foundry Service: Request for Quota Increase"). It reports
"Page 1 of 2" but renders as one continuous page: selecting the branch radios reveals
the conditional questions inline, and a single **Submit** click goes straight to the
confirmation page (no second-page navigation observed live). No Azure identity is used
— this is a Tier 1 operation (a request, not an infra mutation).

## Page 1 — always-on fields

| Our key | Form question label | Type |
|---|---|---|
| `first_name` | First Name | text |
| `last_name` | Last Name | text |
| `company_email` | Company Email | text |
| `company_name` | Company Name | text |
| `company_address` | Company Address | text |
| `company_city` | Company City | text |
| `company_postal_code` | Company Postal Code | text |
| `company_country` | Company Country | text |
| `subscription_id` | Subscription Id | text |
| `justification` | Justification | multiline text |
| `model_type` | Model Type | radio — {Azure Direct Model, **Azure OpenAI**, Anthropic, Fireworks} |
| `deployment_type` | Model Deployment Quota or Fine-Tuning | radio — {**Model Deployment (PTU/RPM/TPM)**, Fine-tuning} |

## Happy path (the only branch wired)

Select **Model Type = Azure OpenAI** and **deployment = Model Deployment
(PTU/RPM/TPM)**. That reveals the conditional questions (live-confirmed):

| Our key | Form question label | Type |
|---|---|---|
| `quota_request_type` | (Azure OpenAI) Quota Request Type | radio — {**Global Standard**, Global Batch, Global Provisioned, Data Zone Standard, ...} |
| `model` | (Azure OpenAI) Global Standard Model | **dropdown** (role=listbox) — {gpt-5.5, gpt-5.4, gpt-4o, gpt-4o-mini, o3, ...} |
| `region` | Global Standard Region | **dropdown** (role=listbox) — {East US, East US 2, West US, Sweden Central, ...} |
| `requested_quota` | (Azure OpenAI) Global Standard Quota | text (TPM number) |

`model` and `region` are **dropdowns, not radios** — this is the correction that made
the runner work. The dropdown option text must match the requested model/region (e.g.
`gpt-4o`, `East US`). Choose `model`/`region` from what the dropdown actually offers
(ground via the Tier-0 usage read + Learn); a value that isn't an option goes
unfilled. The full option lists live on the form and shift over time.

## Two gotchas (load-bearing)

1. **Label-keyed only.** Every input on the Customer Voice form has empty `name`,
   `type`, and `data-automation-id` attributes. The runner matches controls
   exclusively by visible question label. Text fields → `get_by_label(label,
   exact=False)`; single-choice radios → `get_by_role("radio", name=option,
   exact=False)`; **dropdowns** → the listbox itself is only aria-labelled "Select
   your answer", so scope to the visible question wrapper
   (`.office-form-question:visible` with `has_text=label`), open the `role=listbox`,
   then click the `role=option` whose text is the value. Hidden conditional dropdowns
   for other branches also exist in the DOM — the `:visible` scope avoids them. If a
   label string changes on the live form, the field silently goes unfilled — the live
   probe catches this before submit.

2. **No shareable pre-filled URL.** Customer Voice form state is session-local to the
   headless browser. There is no way to share a partially-filled link with the
   founder. "Review before submitting" means: run with `mode: prepare` (the Executor
   screenshots the filled form and delivers the screenshot), then run again with
   `mode: submit` on approval.

## Proof convention

Delivered to `artifacts/quota/` in the advisor brain:

- `<date>-<slug>-quota-proof.md` — records: status (submitted / prepared / incomplete
  / failed), model, region, requested quota, subscription id, company name,
  justification, confirmation text (if submitted), screenshot filename, acting
  identity. Tier 1 noted (a request, not an infra mutation; anonymous form, no Azure
  identity used).
- `<date>-<slug>-quota-screenshot.png` — full-page screenshot of the form state at
  submission time (or at the filled-but-not-submitted state for `prepare` mode).

The proof is the ground truth for what happened. The advisor reports from the proof —
it does not assume the submission succeeded.

## Confirmation + timeframe (live-confirmed)

On a successful submit the form shows: **"Thanks! You've completed the request!"** The
runner treats `completed the request` (and other generic markers) as the
proof-of-submission signal — it will NOT report `submitted` without one.

The confirmation page states the authoritative timeframe: quota increases are
**"typically processed the next business day after submission, sometimes up to two
business days,"** filled in the order received, and **submission does not guarantee
the increase will be fulfilled.** The advisor + `watch-and-notify` must use this
language — do not invent a different number or imply a guarantee.
