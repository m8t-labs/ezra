# Deploy the platform — m8t channel gateway in your Azure account

> 🤖 **Agent runbook.** Paste this into your coding agent — it executes the steps top-to-bottom and pauses only for sign-ins, `sudo`, or genuine choices. Idempotent — safe to re-run after a `git pull`.
>
> 🧑‍💻 **Operator guide.** This deploys the platform into your own Azure subscription using the **public image** — no source build, no npm publish, no local dev server. Contributing to m8t itself, or running the web app locally for development? That's [`CONTRIBUTING.md`](../CONTRIBUTING.md), not this file.

**Outcome:** the channel-connectivity gateway (Container App + Service Bus + Storage + Key Vault + Log Analytics + App Insights) running in your Foundry resource group. Once it's up: [add workers](workers.md) and [operate it](operate.md).

**Idempotent.** Re-running this file is the supported update path; each step no-ops when state already matches.

> ⚠️ **These commands need access to the m8t platform repository, which is not public.**
> They read platform content — agent definitions and deployment templates — out of a
> checkout, and this repository is not that checkout. If you run them you will get a
> refusal saying so by name, not a confusing error.
>
> Your installation still updates itself: the auto-update rail applies published releases
> without needing any checkout at all.

## Prerequisites

- Azure CLI ≥ 2.86 (`az version`), Node ≥ 20, `gh` authenticated (`gh auth status`). (`docker buildx` is only needed if you build your own image — see Step 1; the default path pulls the public image and needs no Docker.)
- Signed in to your Azure tenant (`az login`).
- **Owner or User Access Administrator at _subscription_ scope** — the deploy creates subscription-scoped read-role assignments for the dashboard managed identity (Cost Management Reader, Monitoring Reader). RG-scope rights alone are not sufficient.
- **Contributor (or Cognitive Services Contributor / Azure AI Account Owner) on the Foundry account** — the deploy connects the Foundry account to App Insights for GenAI tracing (`connections/write`). If you lack this, use the portal fallback noted in Step 2.
- **Tenant-admin role** (Global / Application / Cloud Application Administrator) — only on the very first run, for the one-time app-registration create + admin consent. If you can't create app registrations (e.g. a directory guest), pass `--client-id` (see `deploy/README.md`).
- A **hosted-agent-eligible region** — use `eastus2` (the `--location` default `eastus` is NOT eligible for hosted agents).
- Container Apps Environment quota headroom (per-region default ~20; older subscriptions 1): `az containerapp env list -o table`.
- A **Foundry project** in that tenant — **create one below** if you don't have it.

## Create the Foundry account, project, and model

Skip this if you already have a Foundry project. Otherwise create the AI Foundry (AIServices) account with project management enabled, give it a globally-unique custom subdomain (this becomes the `<acct>` in the endpoint URL), create a project, and deploy `gpt-4.1-mini`. Pick your own globally-unique `<acct>` name.

**Preferred (one command, idempotent):**

```bash
m8t foundry create --resource-group rg-m8t-stack --location eastus2
# prints the project endpoint; re-run is a clean no-op
```

Or run the `az` sequence by hand:

```bash
# (a) AI Foundry (AIServices) account — --allow-project-management enables projects
az cognitiveservices account create \
  --name <acct> \
  --resource-group rg-m8t-stack \
  --location eastus2 \
  --kind AIServices \
  --sku S0 \
  --allow-project-management \
  --yes

# (b) Globally-unique custom subdomain — sets the endpoint host to <acct>.services.ai.azure.com
az cognitiveservices account update \
  --name <acct> \
  --resource-group rg-m8t-stack \
  --custom-domain <acct>

# (c) Project under the account
az cognitiveservices account project create \
  --name <acct> \
  --resource-group rg-m8t-stack \
  --project-name <project> \
  --location eastus2

# (d) Deploy the gpt-4.1-mini model
az cognitiveservices account deployment create \
  --name <acct> \
  --resource-group rg-m8t-stack \
  --deployment-name gpt-4.1-mini \
  --model-name gpt-4.1-mini \
  --model-version "2025-04-14" \
  --model-format OpenAI \
  --sku-name GlobalStandard \
  --sku-capacity 10
```

The **project endpoint** is `https://<acct>.services.ai.azure.com/api/projects/<project>` (the `<acct>` segment is the custom subdomain from step b). It feeds the gateway deploy below.

> **Capacity note.** Brain-enabled + reasoning workers are token-heavy; the Foundry default deployment capacity of 50 (= 50k TPM) `429`s on two heavy turns within a minute. For those, deploy the reasoning model at **≥250 capacity** (`--sku-capacity 250`, subject to your `OpenAI.GlobalStandard.<model>` quota). Capacity is a per-minute rate ceiling on a pay-per-token SKU — raising it doesn't increase cost.

## GitHub App setup (for brain-enabled workers)

If you'll deploy brain-enabled workers (any persona with `targets.foundry.brain: true`), register a GitHub App + store its credentials in Key Vault. **One-time setup, ~10 min, browser-based.** See `deploy/github-app-registration-setup.md`, then verify:

```bash
m8t brain check-app
```

## Step 0 — Pre-flight (read-only)

```bash
az login
az account set --subscription <id-or-name>
az account show -o table          # confirm subscription + tenant
az version -o json                # need az >= 2.86
node --version                    # need >= 20
docker --version                  # only needed if you build your own image (Step 1)
```

**[PAUSE — operator confirm]** Is this the right subscription and tenant? If not, `az account set --subscription <id>` or `az login --tenant <id>`.

Detect the Foundry RG + endpoint, and pick a region:

```bash
cat ~/.m8t/config.yaml 2>/dev/null            # may already have projectEndpoint
az cognitiveservices account list -o table          # find the Foundry account + its RG + .location

FOUNDRY_RG=<foundry-resource-group>
FOUNDRY_ENDPOINT=https://<acct>.services.ai.azure.com/api/projects/<project>
REGION=<foundry-account-region>   # e.g. eastus2
```

CAE-quota check — the per-region Managed Environment quota default is **~20** (older subscriptions were capped at 1), so the deploy only fails if you're actually at the limit:

```bash
az containerapp env list --query "[].{name:name,rg:resourceGroup}" -o table
az rest --method GET --url "https://management.azure.com/subscriptions/$(az account show --query id -o tsv)/providers/Microsoft.App/locations/$REGION/usages?api-version=2024-03-01" --query "value[?name.value=='ManagedEnvironmentCount'].{used:currentValue,limit:limit}" -o table
```

If `used` has reached `limit`, **stop and ask** the operator to free a slot or request a quota bump. (An existing m8t CAE in another RG does not block a new one as long as you're under the limit.)

## Step 1 — Choose your gateway image

**Default (recommended): the public image.** `m8t deploy` pulls
`ghcr.io/m8t-labs/m8t:latest` from GitHub Container Registry **anonymously** — no
registry to create, no image to build, no credentials. **Skip straight to Step
2.**

> **Bring-your-own-image (optional)** — only if you run a fork, custom patches, or a
> private-only tenant. Build the web image into your own registry and pass
> `--image-ref <your-registry>/m8t:<tag>` to `m8t deploy` (for a `*.azurecr.io` ref it
> auto-provisions an AcrPull identity). Full guide:
> `publish/self-build.md`.

(The hosted-coder image is a separate artifact built in [`workers.md`](workers.md) — you don't need it to bring the gateway up.)

## Step 2 — Deploy the gateway

```bash
m8t deploy \
  --resource-group "$FOUNDRY_RG" \
  --foundry-endpoint "$FOUNDRY_ENDPOINT" \
  --location "$REGION"
# Default image is the public ghcr.io/m8t-labs/m8t:latest (anonymous pull).
# Bringing your own image? add: --image-ref "<youracr>.azurecr.io/m8t-web:<tag>"
```

`m8t deploy` is 7 idempotent steps (app reg → Expose-an-API → `config.yaml` → ensure RG → Bicep → capture FQDN → PATCH redirect URIs). For `*.azurecr.io` image refs it auto-provisions the AcrPull user-assigned identity + grant; pass `--acrpull-identity <id>` to reuse one, or `--acr-resource-id <id>` if the registry host can't be resolved from the image ref. **[PAUSE — operator]** may be required for `az login` re-auth or, on the very first run in a fresh tenant, tenant-admin consent for the `m8t-webapp` app registration. The command prints the deployed FQDN + resource names at the end. Full flag + resource reference: `deploy/README.md`.

**Bicep sets the Container App env vars automatically** (subscription/RG/Log-Analytics IDs, gateway URL) — no manual `.env.local` entry needed. The table is in `deploy/README.md`.

**Foundry tracing connection.** The Bicep deploy creates an `AppInsights` connection on your Foundry account (`m8t-appinsights`) so agent runs emit GenAI traces to the m8t Application Insights — this powers the Observability dashboard's per-worker detail.

- **Verify:** `az rest --method GET --url "https://management.azure.com<FOUNDRY_RESOURCE_ID>/connections?api-version=2025-06-01" --query "value[?properties.category=='AppInsights'].name" -o tsv` returns `m8t-appinsights`.
- **Portal fallback** (if you lack `connections/write`, or traces don't appear): Foundry portal → your project → **Agents → Traces → Connect**, select the `m8t-ai-*` Application Insights resource, **Connect**.

To enable agent-to-agent delegation on the gateway, see the A2A sections of [`workers.md`](workers.md) and `deploy/README.md`.

## Step 3 — Grant your user the data-plane roles

Chat uses your browser's delegated Foundry token, so you need only the two data-plane roles the local gateway uses (table + secret access):

```bash
OBJ=$(az ad signed-in-user show --query id -o tsv)
# `az resource list` rejects --tag together with -g, so filter the RG in the query.
STORAGE_ID=$(az resource list --tag m8t=storage  --query "[?resourceGroup=='$FOUNDRY_RG'].id | [0]" -o tsv)
KV_ID=$(az resource list --tag m8t=keyvault --query "[?resourceGroup=='$FOUNDRY_RG'].id | [0]" -o tsv)

az role assignment create --assignee "$OBJ" --role "Storage Table Data Contributor" --scope "$STORAGE_ID"
az role assignment create --assignee "$OBJ" --role "Key Vault Secrets Officer"      --scope "$KV_ID"
```

Re-runs print `RoleAssignmentExists` — that is success, not an error.

> **This is also the MCP ledger-write path.** The local MCP server (`plugins/m8t/`) authenticates to Azure as your user via `DefaultAzureCredential`; the `Storage Table Data Contributor` grant above is exactly what lets `emitLedgerEvent()` write `AgentLedger` rows from the MCP. No separate grant is needed.

## Step 4 — Verify

Resolve the gateway FQDN and check it serves:

```bash
APP=$(az resource list --tag m8t=gateway --query "[?resourceGroup=='$FOUNDRY_RG'].name | [0]" -o tsv)
FQDN=$(az containerapp show -g "$FOUNDRY_RG" -n "$APP" --query properties.configuration.ingress.fqdn -o tsv)
curl -sS -o /dev/null -w "deployed HTTP %{http_code}\n" "https://$FQDN"   # expect 200 or 3xx
```

**[PAUSE — operator]** Open `https://$FQDN`, sign in with Entra, confirm the app loads.

(`~/.m8t/config.yaml` was written by `m8t deploy` in Step 2, so the CLI already has your tenant/client/Foundry config.)

> Developing the web app locally against these live resources is a **contributor**
> workflow, not an operator one — see [`CONTRIBUTING.md`](../CONTRIBUTING.md).

## Next steps

- **Add workers** — deploy a CMO or a hosted coder onto this platform: [`workers.md`](workers.md).
- **Operate it** — manage team, channel bindings, updates, and health: [`operate.md`](operate.md).

## Re-running / updating

- **Public image (default):** `m8t platform update` rolls the gateway to the newest `vX.Y.Z` published on `ghcr.io/m8t-labs/m8t` (`m8t platform status` previews without changing anything). No rebuild, no redeploy. The roll pins the exact image by digest, so the version you see stays the code you run — see [What your gateway is pinned to](operate.md#what-your-gateway-is-pinned-to).
- **Bring-your-own-image:** rebuild a fresh-tagged image (Step 1) and re-run `m8t deploy` with the new `--image-ref` (a fresh tag is required to roll in single-revision mode).
- **Infra / env / role changes (any path):** re-run this file — `m8t deploy` and the data-plane role assignments are idempotent and no-op where state already matches.

## Teardown

See [`uninstall/azure-infra.md`](uninstall/azure-infra.md) — deletes only `m8t`-tagged resources; never the RG, never Foundry. A single worker: `m8t coder teardown <name>` (see [`workers.md`](workers.md)).
