# Memory index

> Your memories, newest first. The summary on each line is usually enough to answer — open the linked file only when you need full detail. Each path is repo-root; copy it verbatim, never invent one.

- `memory/startup-advisor-escalation.md` — **Startup-advisor escalation**: the Microsoft Startup Advisor (from `memory/founder.md`) is THE Microsoft escalation contact — email them (founder-gated) for quota/credit asks, exceptions, and Microsoft-must-decide walls; handle reads/provisioning yourself; degrade if no SA. (2026-07-01 · escalation, advisor, notify)
- `memory/founder.md` — **Founder & install context**: the founder's identity, contact email, Microsoft Startup Advisor, Azure subscription, and team size (operator-seeded at onboarding; authoritative). (2026-06-30 · founder, install-context)
- `memory/quota-and-mfs-reality.md` — **Quota and MFS reality**: credits are a budget; check quota before promising a model (`az cognitiveservices usage list`); MFS quota form at `aka.ms/oai/stuquotarequest`; grants are async; ground specifics via `azure-quotas` + Learn. (2026-06-07 · quota, mfs, models)
- `memory/least-privilege-doctrine.md` — **Least-privilege doctrine**: narrowest scope that works; RG scope over subscription; managed identity over service principal; the Executor can't grant roles by design; ground RBAC specifics via `azure-rbac` + Learn. (2026-06-07 · security, least-privilege, rbac)
- `memory/tiered-authority-rules.md` — **Tiered authority rules**: group-first then verb, deny-by-default; Tier 0 = read; Tier 1 = provision; Tier 2 = destructive or privilege-group write; on Tier 2 classify → state effect → confirm → STOP. (2026-06-07 · tiers, authority, gating)
- `memory/region-and-capacity-gotchas.md` — **Region and capacity gotchas**: availability ≠ capacity; verify quota in the target region before promising; ground via `azure-quotas` + Learn. (2026-06-07 · region, capacity, quota)
- `memory/when-to-delegate.md` — **When to delegate**: advice + doc lookups stay with the advisor; mutations + live reads go to the Executor; never work around a refusal; advisor never runs `az` itself. (2026-06-07 · delegation, a2a, executor)
