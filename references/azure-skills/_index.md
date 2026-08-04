# Azure skills — source-of-truth pointers

Source-of-truth pointers — the deployed advisor can't execute these (no Skill tool); it grounds against them via the Learn MCP + web_search. Do NOT copy or paraphrase azure-skills content here; always defer to the canonical source below.

| Routing domain | Canonical skill | MS Learn area |
|---|---|---|
| Storage / blob / files / queues / tables / Data Lake | [microsoft/azure-skills · azure-storage](https://github.com/microsoft/azure-skills/tree/main/skills/azure-storage) | https://learn.microsoft.com/azure/storage/ |
| RBAC / role assignments / role definitions / least-privilege | [microsoft/azure-skills · azure-rbac](https://github.com/microsoft/azure-skills/tree/main/skills/azure-rbac) | https://learn.microsoft.com/azure/role-based-access-control/ |
| Identity / auth / OAuth / MSAL / Entra ID / app registrations / secrets | [microsoft/azure-skills · entra-app-registration](https://github.com/microsoft/azure-skills/tree/main/skills/entra-app-registration) | https://learn.microsoft.com/entra/identity-platform/ |
| Subscription / resource group baseline / environments / landing zone | [microsoft/azure-skills · azure-prepare](https://github.com/microsoft/azure-skills/tree/main/skills/azure-prepare) | https://learn.microsoft.com/azure/cloud-adoption-framework/ready/ |
| Deploy / CI-CD / IaC / Bicep / azd / Azure Developer CLI | [microsoft/azure-skills · azure-deploy](https://github.com/microsoft/azure-skills/tree/main/skills/azure-deploy) | https://learn.microsoft.com/azure/developer/azure-developer-cli/ |
| Cost / budget / credits / burn / governance | [microsoft/azure-skills · azure-cost](https://github.com/microsoft/azure-skills/tree/main/skills/azure-cost) | https://learn.microsoft.com/azure/cost-management-billing/ |
| Quota / capacity / region limits | [microsoft/azure-skills · azure-quotas](https://github.com/microsoft/azure-skills/tree/main/skills/azure-quotas) | https://learn.microsoft.com/azure/quotas/ |
| Foundry / agents / models / Azure AI | [microsoft/azure-skills · microsoft-foundry](https://github.com/microsoft/azure-skills/tree/main/skills/microsoft-foundry) | https://learn.microsoft.com/azure/ai-foundry/ |

## How to use these pointers

1. Match the founder's intent to the routing domain above.
2. Use the Microsoft Learn MCP (`microsoft_docs_search` → `microsoft_docs_fetch`) to retrieve authoritative content from the MS Learn area listed.
3. Cite the `microsoft/azure-skills` skill name in your delegation task so the Executor grounds in the same vocabulary.
4. Never copy azure-skills content into this index or into `memory/` — pointers only.
