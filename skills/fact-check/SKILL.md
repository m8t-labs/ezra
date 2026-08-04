---
type: skill
title: "Fact-check — verify a founder's technical draft against Microsoft Learn"
created: 2026-06-22T00:00:00Z
updated: 2026-06-22T00:00:00Z
tags: [fact-check, learn, accuracy, draft, review]
origin: operator
---

# Fact-check

## When to run this

The founder pastes a technical draft — an email, a message, a doc, a blog post — and wants it checked for accuracy before they send or publish. They may say "fact-check this", "verify this email", "is this technically correct?", or paste a draft about Azure, Microsoft 365, GitHub, .NET, or any Microsoft technology and ask for review.

## The discipline

**Extract claims → verify each against Learn → score → report → corrected rewrite → ask before send.**

`learn.microsoft.com` is the only source of truth. Verify every claim against the live Microsoft Learn docs via the Learn MCP (`microsoft_docs_search` → `microsoft_docs_fetch`); use `web_search` only for public non-docs facts (pricing pages, GA announcements). If a claim cannot be verified against a Learn page, mark it Unverifiable — never substitute your own recollection.

### 1. Extract the verifiable claims

Read the draft and pull out discrete, checkable factual claims — especially:
- Service / product names and exact branding (e.g. "Azure AI Foundry" vs "Azure AI Studio" vs "Azure OpenAI").
- Feature availability, GA vs preview status, region availability.
- SKU / tier names and what they include (vCPU, GPU count, memory).
- Quotas, limits, default values.
- API surface, SDK package names, CLI command names.
- Deprecations and end-of-life dates.
- Pricing model claims (per-token, per-hour, per-request).
- Integration claims ("X works with Y") and step-by-step instructions.

Skip subjective statements, opinions, and business framing.

### 2. Verify each claim against Microsoft Learn

For each claim, search Learn for the authoritative page, fetch it if needed, and record:
- the exact quote from the draft,
- what Learn says (one-line paraphrase),
- a verdict: Correct / Inaccurate / Outdated / Misleading / Unverifiable,
- the citation URL on `learn.microsoft.com`.

Run independent lookups in parallel. If a Learn page's "Last updated" date is older than ~12 months in a fast-moving area (AI, GPU SKUs, Azure OpenAI), flag it "worth confirming, doc may be stale".

### 3. Score the draft (1-10)

Compute an integer Accuracy Score:
- **10** — every verifiable claim correct and current.
- **9** — all correct, minor imprecise wording.
- **8** — one cosmetic inaccuracy that does not mislead.
- **7** — one material inaccuracy, or several minor; the reader still gets the right takeaway.
- **5-6** — multiple material inaccuracies, or one that could mislead a real decision (wrong limit / SKU / region).
- **3-4** — a critical claim is flat wrong (e.g. a feature that does not exist).
- **1-2** — mostly inaccurate; hallucinated services, fabricated APIs, deprecated guidance presented as current.

Modifiers: subtract 1 if a claim is asserted as documented fact but is Unverifiable; subtract 1 more if the inaccuracies would directly affect an architecture or spending decision. Do not penalize tone or business framing. If the draft has zero verifiable technical claims, do not score — say so and stop.

### 4. Report

Output, in order:
1. **Accuracy Score: X/10** — one sentence explaining it.
2. **Findings** — a compact table of every non-Correct claim: `| Claim (quoted) | Verdict | What's actually correct | Source (learn.microsoft.com URL) |`. If everything checks out, say so and skip the table.
3. **Corrected rewrite** — a clean rewrite fixing every inaccuracy, preserving the founder's voice, structure, and non-technical content. Match the original length within about 10 percent. No em or en dashes, no emojis. Do not add new claims except to replace an inaccurate one. Keep the subject line, greeting, and sign-off if it is an email.

### 5. Ask before send

After the report, ask: "Want me to refine any of these corrections, or are you good to send?" Never send, reply to, or update any draft automatically — the founder approves the outbound action.

## Never

- Never verify a claim from your own memory — ground every one against `learn.microsoft.com`.
- Never substitute your recollection for an Unverifiable claim — mark it Unverifiable.
- Never score a draft that has no verifiable technical claims — say so and stop.
- Never send or edit the draft automatically — ask first.
