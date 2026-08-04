---
type: memory
title: "Quota and MFS reality — credits are a budget, not a marketing allowance"
created: 2026-06-07T00:00:00Z
updated: 2026-06-07T00:00:00Z
tags: [quota, mfs, models]
origin: operator
---

The MFS credit grant is real money with a hard ceiling. Treat it like a runway, not a coupon.

- **Check quota before promising a model.** A model can appear in a region's catalog but have zero allocated capacity there. Before telling a founder "just use GPT-5 in this region," have the Executor check current usage (via `az cognitiveservices` usage or the `azure-quotas` skill) and confirm non-zero remaining quota. Promising a model without this check is the fastest way to burn trust.
- **Quota and availability are separate dimensions.** A model can be *available* (deployable) in a region and still show `currentValue == limit` in the usage response — no room. Verify both.
- **Quota increases are async.** The MFS Startups OpenAI quota request form is at `aka.ms/oai/stuquotarequest`; the general form is `aka.ms/oai/quotaincrease`. Approval takes days, not minutes. Plan around this — don't block a launch on a grant that hasn't landed.
- **Help the founder write a strong justification.** Quota requests without clear expected usage ("we're launching X, expecting Y RPM at Z context length") are lower priority. A crisp justification improves turnaround.
- **For current limits and regional availability:** ground via the `azure-quotas` skill + the Learn MCP. Don't guess from memory — limits change.

The underlying instinct: before making a commitment to the founder, verify it with the Executor.
