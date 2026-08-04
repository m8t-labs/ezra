---
type: memory
title: "Region and capacity gotchas — availability ≠ capacity"
created: 2026-06-07T00:00:00Z
updated: 2026-06-07T00:00:00Z
tags: [region, capacity, quota]
origin: operator
---

A model or SKU being listed in a region does not mean there's capacity to deploy it there. These are separate dimensions and both can fail independently.

- **Model availability varies by region.** A model that works in `eastus` may not be deployable in `westeurope`. Check the current availability matrix via the Learn MCP before recommending a region.
- **Quota can be zero even in supported regions.** The Azure portal and `az cognitiveservices usage list` show current quota; a response where `currentValue == limit` means no room, regardless of whether the model is listed. Have the Executor check before committing to a deployment region.
- **Verify before promising.** "Deploy GPT-5 in Sweden Central" is the advisor's instinct; confirming the quota is non-zero there is the Executor's job. Make them happen in that order.
- **The MFS subscription starts with default quota in select regions only.** Which regions is point-in-time and allocations shift — don't assume any region has headroom; verify via the `azure-quotas` skill before relying on one.
- **Region choice has cost and latency consequences, not just availability ones.** Egress pricing varies; latency to the founder's users matters; data-residency requirements sometimes lock the choice entirely. Ask before picking.
- **For current per-region availability and quota:** ground via the `azure-quotas` skill + Learn MCP (`microsoft_docs_search` "Azure OpenAI model availability"). Don't rely on memory — this table changes with every new model wave.
