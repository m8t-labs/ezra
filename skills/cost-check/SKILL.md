---
type: skill
title: "Cost check — quick burn read or a deep cost review"
created: 2026-06-07T00:00:00Z
updated: 2026-06-22T00:00:00Z
tags: [azure, cost, credits, burn, mfs, optimization]
origin: operator
---

# Cost check

## When to run this

The founder wants to know what's eating their credits, whether they're on track, or what to cut. Two depths:

- **Quick** ("what's eating my credits?", "how much runway do I have?") — read current spend, flag runway against the MFS credit ceiling, return one high-leverage move.
- **Deep** ("do a full cost review", "deep dive on my spend", "help me optimize", "quarterly review") — 2-3-month trend, top-5 services, per-service optimization patterns, and a structured founder-facing memo.

Default to quick unless the founder asks for a review or the spend clearly warrants one.

## The discipline

**Delegate the read → interpret → flag runway → recommend.** Never fabricate a cost number or an `az` command — delegate the read to the Executor and ground commands via the Learn MCP.

### 1. Delegate the cost read to the Executor

Read `memory/founder.md` for subscription and resource group. Delegate a Tier-0 cost/usage read:

`discover_workers` -> `invoke_worker(target:"ezra-executor", task:<cost read instruction>)`.

Pass the founder context and the proof sub-folder as **tool arguments** (the Executor writes proof into your brain automatically — the repo is always your brain):

`invoke_worker(target:"ezra-executor", task:<the instruction>, inputs:"brain:memory/founder.md", deliver_to:{pathPrefix:"artifacts/azure/"})`

For a **quick** read: current spend plus the top one or two cost drivers. For a **deep** read: the 2-3-month monthly trend, the top-5 services by spend, and the Azure Advisor cost recommendations (`az advisor recommendation list --category Cost`). Do NOT fabricate the exact `az` cost command — ground it via the Learn MCP (`microsoft_docs_search` for the Azure Cost Management / Consumption CLI, then `microsoft_docs_fetch`); the Executor runs it, you interpret the result.

**Cold-start:** if the first invocation returns `storage_error` (the op did NOT run), retry once before reporting failure.

### 2. Flag runway against the MFS credit ceiling

Read `memory/quota-and-mfs-reality.md` for the MFS credit ceiling and any recorded burn rate. Compare current spend to the ceiling: how many days / months of runway at the current rate, and is it sustainable for the founder's stage? State the runway number plainly; do not soften it if it is short. If the founder needs **more credits** — an actual grant increase, not an optimization — that is a Microsoft-must-decide ask: escalate it to the Startup Advisor per `memory/startup-advisor-escalation.md`. Optimizing the burn stays your lane.

### 3. Quick mode — one move

Pick the single highest-leverage optimization for this founder's actual spend profile (not a generic list), ground it via the Learn MCP and `microsoft/azure-skills · azure-cost`, and return a plain-English burn summary:
1. **Current burn:** `$X/month`, sourced from the proof artifact.
2. **Runway:** `~N months` at the current rate against the MFS ceiling.
3. **Top line by resource:** the one or two biggest drivers.
4. **One move:** the highest-leverage optimization, Learn-grounded.
5. The proof artifact path.

### 4. Deep mode — the structured memo

When the founder asked for a review, after the deep read:
1. For each of the top services, test the relevant patterns in `references/cost-optimization-patterns.md` against this founder's actual usage — ground every recommendation you keep via the Learn MCP before presenting it.
2. Fold in the Azure Advisor cost recommendations from the read.
3. Write a founder-facing memo:
   - **Current state:** total spend (last 2-3 months), trend (growing N% / flat / declining N%), credits remaining and runway vs the MFS ceiling.
   - **Top spending services:** the top 5 with their share of total.
   - **Recommendations:** grouped **quick-wins (this week)** / **medium (this month)** / **strategic (next quarter)**, each with a savings framing.
   - **Estimated total savings** if all applied.
   - **Next step:** one concrete action.

### 5. Write memory

If the numbers change what you know about this founder's burn rate or resource inventory, write the learning to `memory/` the usual way (re-read, add, write back).

## Never

- Never fabricate a cost number — delegate the read.
- Never give a generic optimization list — in quick mode pick one move; in deep mode tie every recommendation to this founder's actual top services.
- Never state runway without comparing to the MFS credit ceiling in `memory/quota-and-mfs-reality.md`.
- Never fabricate `az` syntax (cost or `az advisor`) — look it up via Learn.
