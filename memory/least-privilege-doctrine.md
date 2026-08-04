---
type: memory
title: "Least-privilege doctrine — narrowest scope that works"
created: 2026-06-07T00:00:00Z
updated: 2026-06-07T00:00:00Z
tags: [security, least-privilege, rbac]
origin: operator
---

Every permission grant is a future attack surface. Start narrow; expand with evidence.

- **Prefer resource-group scope over subscription.** A `Contributor` assignment on a single RG means a mistake in dev can't touch prod. Subscription-scope bleeds across environments. Use `--scope /subscriptions/<id>/resourceGroups/<rg>` unless there's a concrete reason to go higher.
- **Reads are safe; mutations are scoped; privilege grants are gated.** That's the whole hierarchy. A read that returns data the founder didn't expect is a learning. A write in the wrong scope is an incident.
- **Managed identity over service principal.** When code runs inside Azure (App Service, Container App, AKS, Function App), there's no secret to rotate and no credential to leak. Service principals are for clients outside Azure.
- **Never `Owner` when `Contributor` is enough. Never `Contributor` when a data-plane role is enough.** The Executor itself holds `Contributor` at RG scope — that's already the upper bound of what it can delegate. For workloads, look up the right built-in role via `azure-rbac` rather than guessing from the name.
- **The Executor can't grant roles — by design.** Its identity is `Contributor`, not `Owner` or `User Access Administrator`. If the founder needs a new role assignment, that's a Tier-2 operation: classify → state effect → confirm → the advisor looks up the exact command via the Learn MCP; the founder runs it, or it waits for the gated-execution path (shipping later).
- **Ground RBAC specifics via `azure-rbac` + Learn.** Azure has hundreds of built-in roles. Don't guess from the name; `az role definition list --name <role>` confirms scope and permissions. For the full picture, the Learn MCP.
