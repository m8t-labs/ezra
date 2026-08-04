---
type: skill
title: "Migration assess — assess an AWS-to-Azure migration"
created: 2026-06-22T00:00:00Z
updated: 2026-06-22T00:00:00Z
tags: [azure, migration, aws, assessment, class-b]
origin: operator
---

# Migration assess

## When to run this

The founder is evaluating or planning a move from AWS to Azure — "we're on AWS,
thinking about Azure", "map our AWS stack to Azure", "what would our architecture
look like on Azure?", "is it worth migrating?".

## The discipline

**Intake the AWS profile → map each service (Learn-grounded) → recommend an approach → hand off if assisted/funded.**

### 1. Intake the AWS workload profile

Gather what they run on AWS — compute (EC2 / ECS / Fargate / Lambda / EKS), data
(RDS / DynamoDB / Aurora / S3 / Redshift), identity (Cognito / IAM), networking
(VPC / Route 53 / CloudFront), AI/ML (SageMaker / Bedrock), messaging (Kinesis /
SQS / SNS). Ask once; persist the salient bits to `memory/founder.md`. If the
profile is already in memory, read it rather than re-asking.

### 2. Map each service to its Azure equivalent

Use `references/aws-azure-map.md` for the service-by-service mapping. The table
is a starting point — ground the specific equivalent and current SKU via the
Microsoft Learn MCP before presenting it (`microsoft_docs_search` →
`microsoft_docs_fetch`). For database and migration-tooling specifics, ground
against the `azure-migrate` and `azure-database-migration` skills' Learn areas
(you cannot invoke those skills — there is no Skill tool here — but you cite them
and verify the specifics via Learn).

### 3. Recommend a migration approach

Pick the one approach that fits the profile, and say why:
- **Lift-and-shift** (rehost) — EC2 → Azure VMs; fastest, least change; good when the priority is getting off AWS quickly.
- **Replatform** — adopt managed PaaS equivalents (RDS → Azure Database for PostgreSQL/MySQL, ECS → Container Apps) for lower ops without a rewrite.
- **Refactor** — re-architect to cloud-native (AKS, Functions); highest effort, best long-term fit.

State the recommended approach, not a menu.

### 4. Microsoft-assisted or funded migration → hand off

If the founder wants Microsoft-assisted or funded migration support (FastTrack
for Azure, or the Microsoft Migration Program), that enrollment is a
Microsoft-side action. Explain that the programs exist and what they cover, then
follow `references/advisor-handoff.md` and emit:

```
<m8t:advisor_handoff>
attempted:    the AWS→Azure mapping you produced + the approach you recommended (cite the Learn pages)
blocked:      assisted/funded migration (FastTrack / Migration Program) enrollment is a Microsoft-side action
package:      the mapped target architecture + the AWS profile + the chosen approach + any brain artifact path
recipient:    the founder's MfS advisor from memory/founder.md (degrade to a generic recipient if unknown)
next_action:  assess the founder for FastTrack / Migration Program eligibility and enroll them
</m8t:advisor_handoff>
```

## Never

- Never assert an Azure equivalent or SKU from memory — ground it live via Learn.
- Never enroll the founder in a funded/assisted program yourself — that is the advisor handoff.
- Never recommend a menu of approaches — pick the one that fits and say why.

