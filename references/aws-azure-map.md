---
type: reference
title: "AWS to Azure service map — equivalents for a migration assessment"
created: 2026-06-22T00:00:00Z
updated: 2026-06-22T00:00:00Z
tags: [migration, aws, azure, reference]
origin: operator
---

# AWS to Azure service map

The service-by-service mapping for `migration-assess`. Each row is a starting
point — ground the specific equivalent and current SKU via the Microsoft Learn
MCP before presenting it to the founder; the Learn link is where to start, not a
substitute for confirming the current service name / SKU.

## Compute
| AWS | Azure | Learn |
|---|---|---|
| EC2 | Azure Virtual Machines | https://learn.microsoft.com/azure/virtual-machines/ |
| ECS / Fargate | Azure Container Apps (or AKS) | https://learn.microsoft.com/azure/container-apps/ |
| Lambda | Azure Functions | https://learn.microsoft.com/azure/azure-functions/ |
| EKS | Azure Kubernetes Service (AKS) | https://learn.microsoft.com/azure/aks/ |

## Data
| AWS | Azure | Learn |
|---|---|---|
| RDS | Azure SQL Database, or Azure Database for PostgreSQL / MySQL | https://learn.microsoft.com/azure/postgresql/ |
| DynamoDB | Azure Cosmos DB | https://learn.microsoft.com/azure/cosmos-db/ |
| S3 | Azure Blob Storage | https://learn.microsoft.com/azure/storage/blobs/ |
| Redshift | Azure Synapse Analytics / Microsoft Fabric | https://learn.microsoft.com/azure/synapse-analytics/ |

## Identity
| AWS | Azure | Learn |
|---|---|---|
| Cognito | Microsoft Entra External ID | https://learn.microsoft.com/entra/external-id/ |
| IAM | Microsoft Entra ID + Azure RBAC | https://learn.microsoft.com/azure/role-based-access-control/ |

## Networking
| AWS | Azure | Learn |
|---|---|---|
| VPC | Azure Virtual Network | https://learn.microsoft.com/azure/virtual-network/ |
| Route 53 | Azure DNS | https://learn.microsoft.com/azure/dns/ |
| CloudFront | Azure Front Door | https://learn.microsoft.com/azure/frontdoor/ |

## AI / ML
| AWS | Azure | Learn |
|---|---|---|
| SageMaker | Azure Machine Learning | https://learn.microsoft.com/azure/machine-learning/ |
| Bedrock | Azure AI Foundry / Azure OpenAI | https://learn.microsoft.com/azure/ai-foundry/ |

## Messaging
| AWS | Azure | Learn |
|---|---|---|
| Kinesis | Azure Event Hubs | https://learn.microsoft.com/azure/event-hubs/ |
| SQS | Azure Service Bus (queues) | https://learn.microsoft.com/azure/service-bus-messaging/ |
| SNS | Azure Service Bus (topics) / Azure Event Grid | https://learn.microsoft.com/azure/event-grid/ |
