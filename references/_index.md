# References index

> Durable reference files for the Azure Advisor. Read the relevant file when a skill
> points you here. Do not paraphrase or copy content into memory — load the reference
> directly.

- `references/azure-skills/_index.md` — **azure-skills**: source-of-truth pointers to `microsoft/azure-skills` canonical skills and their corresponding MS Learn areas; use these to ground delegation tasks and Learn MCP searches.
- `references/quota-form-fieldmap.md` — **quota-form-fieldmap**: the probed field map for the MFS OpenAI quota-request form (`aka.ms/oai/stuquotarequest`), the Azure OpenAI / Global Standard happy-path branch, the two load-bearing gotchas (label-keyed DOM, no shareable pre-filled URL), and the proof convention (`artifacts/quota/`).
- `references/advisor-handoff.md` — **advisor-handoff**: the standard advisor-ready handback block (attempted · blocked · package · recipient · next_action) for any play that hits a human-only wall.
- `references/notify-advisor-contract.md` — **notify-advisor-contract**: the wired outbound-email seam (`<m8t:notify_advisor>`) — Executor-actuated, founder-gated prepare/submit, advisor address from memory (the Startup Advisor), proof to `artifacts/notify/`.
- `references/cost-optimization-patterns.md` — **cost-optimization-patterns**: the per-service cost catalog for `cost-check`'s deep-review mode (RIs/savings plans, VM rightsizing, storage tiers, AI/ML PTU-vs-PAYG, DB serverless, idle public IPs) — each a Learn-grounded hypothesis to test against the founder's actual usage.
- `references/aws-azure-map.md` — **aws-azure-map**: the AWS→Azure service-mapping table (compute / data / identity / networking / AI-ML / messaging) for `migration-assess`; each row a Learn-grounded starting point, not a substitute for confirming current SKUs/equivalents.
