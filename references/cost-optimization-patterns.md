---
type: reference
title: "Cost optimization patterns — per-service moves for a deep cost review"
created: 2026-06-22T00:00:00Z
updated: 2026-06-22T00:00:00Z
tags: [cost, optimization, reference, deep-review]
origin: operator
---

# Cost optimization patterns

The per-service catalog for `cost-check`'s deep-review mode. Each pattern is a hypothesis to test against THIS founder's actual usage — never a generic checklist to dump. Ground the specific recommendation via the Microsoft Learn MCP before presenting it; the Learn link beside each row is the starting point, not a substitute for confirming current syntax / SKUs.

## Compute — Virtual Machines (usually the top spender)
- Rightsize: compare the VM size to actual CPU / memory over the last 30 days; drop to a smaller SKU, or a B-series burstable for low, spiky utilization.
- Reserved Instances / savings plans for steady 24x7 production (1yr or 3yr). https://learn.microsoft.com/azure/cost-management-billing/reservations/save-compute-costs-reservations
- Auto-shutdown schedules for dev/test outside business hours.

## Storage
- Move infrequently-accessed Blob data to Cool / Cold / Archive tiers; set lifecycle policies for logs. https://learn.microsoft.com/azure/storage/blobs/access-tiers-overview
- Delete orphaned, unattached managed disks (premium SSDs are a common silent cost).

## AI / ML
- Azure OpenAI: provisioned throughput (PTU) vs pay-as-you-go when traffic is predictable; batch deployments for non-realtime workloads. https://learn.microsoft.com/azure/ai-foundry/openai/how-to/provisioned-throughput-onboarding
- Azure AI Search: drop unnecessary replicas / partitions.
- AKS: cluster autoscaler + spot node pools for non-critical workloads.

## Databases
- Azure SQL: serverless tier for variable workloads; reserved capacity for steady ones. https://learn.microsoft.com/azure/azure-sql/database/serverless-tier-overview
- Cosmos DB: autoscale RU/s vs manual provisioned; integrated cache for read-heavy.

## Networking
- Delete idle Public IPs (billed hourly even when unattached). https://learn.microsoft.com/azure/virtual-network/ip-services/public-ip-addresses
- Colocate chatty resources to cut cross-region egress.

## Azure Advisor
- `az advisor recommendation list --category Cost` surfaces Azure's own idle / underutilized-resource findings with savings estimates. https://learn.microsoft.com/azure/advisor/advisor-reference-cost-recommendations
