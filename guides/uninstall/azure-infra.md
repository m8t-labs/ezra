# `uninstall/azure-infra.md` — tear down the m8t comms infra

> 🤖 **Agent runbook.** Paste this into your coding agent — it executes the steps top-to-bottom and pauses only for sign-ins, `sudo`, or genuine choices. Idempotent — safe to re-run.
>
> **Goal:** delete ONLY the channel-connectivity resources m8t created,
> leaving the resource group and any Foundry resources untouched. Idempotent.

## Audience

The coding agent (or the operator). Follow top to bottom. Every delete is
gated on an explicit operator confirmation.

## Why tag-scoped, not "delete the RG"

The comms infra is deployed into the operator's **Foundry resource group**, so
deleting the RG would also destroy the Foundry agents. Every m8t resource
carries the tag `m8t=<role>`; this runbook deletes by tag only.

## Steps

### 1. Pick the resource group

```bash
RG=<foundry-resource-group>   # the RG the comms infra was deployed into
```

### 2. List what would be deleted (read-only)

```bash
az resource list -g "$RG" --query "[?tags.\"m8t\"!=null].{name:name,type:type,tag:tags.\"m8t\"}" -o table
```

Show this list to the operator. Confirm every row is an m8t resource and
nothing Foundry-related appears. **Stop and ask if anything looks unexpected.**

### 3. Delete the resources

Ask: *"Delete the N m8t resources listed above? The resource group and
Foundry resources are NOT touched. (default: No)"* — proceed only on explicit yes.

```bash
az resource list -g "$RG" --query "[?tags.\"m8t\"!=null].id" -o tsv \
  | while IFS= read -r id; do
      echo "Deleting: $id"
      az resource delete --ids "$id" --verbose
    done
```

Container Apps Environment can only be deleted after the Container App inside it
is gone; if a delete fails on ordering, re-run this step — it is idempotent and
the second pass removes the now-empty environment.

The `AgentLedger` table lives in the same `m8t`-tagged storage account and
is removed with the tag-scoped storage teardown — no separate action.

### 3b. Remove the out-of-RG observability grants + tracing connection

The deploy adds resources that live **outside** the deployment RG, so the
tag-scoped delete above does not catch them. Remove them explicitly.

**Subscription-scoped role assignments on the gateway's managed identity** (Cost
Management Reader + Monitoring Reader):

```bash
SUB=$(az account show --query id -o tsv)
# Resolve the gateway MI principalId BEFORE step 3 (post-delete it can't be looked
# up by name); or find the assignments by role + scope and confirm the principal:
az role assignment list --all --scope "/subscriptions/$SUB" \
  --query "[?roleDefinitionName=='Cost Management Reader' || roleDefinitionName=='Monitoring Reader'].{role:roleDefinitionName,principal:principalId,id:id}" -o table
# Delete the two assignments whose principalId is the gateway MI (confirm first):
# az role assignment delete --ids <id>
```

**The Foundry account's App Insights tracing connection** (`m8t-appinsights`):

```bash
FOUNDRY_ID=<foundry-account-resource-id>   # e.g. .../Microsoft.CognitiveServices/accounts/<name>
az rest --method DELETE \
  --url "https://management.azure.com${FOUNDRY_ID}/connections/m8t-appinsights?api-version=2025-06-01"
```

Both are gated on operator confirmation. Deleting the connection stops GenAI traces
flowing to App Insights; it does not affect the Foundry agents or their runs.

### 3c. Remove a worker (any kind) — full cascade

`m8t agent remove` is the preferred way to tear down any worker (prompt or hosted). It removes
bindings, a2a connection, brain connection, the Foundry agent, and the local yaml in one pass.
Idempotent and partial-failure resilient.

```bash
# Full cascade — removes bindings, a2a, brain connection, agent, local yaml:
m8t agent remove <name> --yes

# Also delete the brain GitHub repo (default: keep repo):
m8t agent remove <name> --yes --delete-brain-repo

# Skip binding teardown (e.g. already cleaned up separately):
m8t agent remove <name> --yes --keep-bindings

# Skip a2a teardown:
m8t agent remove <name> --yes --keep-a2a

# JSON output (scriptable):
m8t agent remove <name> --yes --output json
```

Flags:

- `--yes` — required for non-interactive use; otherwise the command lists what will be removed and
  asks for confirmation.
- `--keep-bindings` — skip binding deletion (useful when bindings were already removed separately).
- `--keep-a2a` — skip disabling a2a.
- `--delete-brain-repo` — also delete the brain GitHub repo via `gh repo delete`. Default: keep repo.
- `--kv-uri <uri>` — Key Vault URI (inferred from `AZURE_KEYVAULT_URI` / `KEYVAULT_URI` when omitted).
- `--endpoint <url>` — explicit Foundry project endpoint.
- `--subscription <id>` — target subscription override.
- `--output json|pretty` — machine-readable output (emits `{ agentName, steps }`).

If any step fails the command exits 1. Re-run the same command to retry — each step is idempotent.

For a hosted-coder-only teardown (no binding/brain/a2a cleanup):

```bash
# Agent-only teardown (prefer `m8t agent remove` for a full cleanup):
m8t coder teardown <name> [--yes]

# Raw fallback (data-plane delete; removes the container + identity + role assignment too):
az rest --method DELETE \
  --url "https://<account>.services.ai.azure.com/api/projects/<project>/agents/<name>?api-version=v1" \
  --resource "https://ai.azure.com"
```

The agent's dedicated Entra identity and its Foundry User role assignment are cleaned up
automatically when the agent is deleted.

Notes:

- Hosted-worker container images you pushed to your ACR are **not** removed by this delete. Delete a
  repo with `az acr repository delete -n <youracr> --repository <repo>` once you no longer need it.
- After all hosted workers are torn down, the ACR itself may be deleted (if you created it solely for
  m8t): `az acr delete -n <youracr> -g "$RG" --yes`.

### 3d. Remove the A2A bridge

The A2A bridge adds Foundry-side artifacts that carry no `m8t` tag, so step
3 does not catch them. The `/api/a2a/mcp` route is part of the web image — there
is no separate resource to remove. Delete the `a2a-<agent>` project
connection(s); unset `A2A_CALLER_TOKENS` / `A2A_INVOKE_BUDGET_SECONDS` on the
gateway Container App.

- **A2A connections** (`a2a-<agent>`): CustomKeys project connections created by `m8t a2a enable`. Remove per-worker with `m8t a2a disable <agent>`, or they are torn down with the project. They hold only an opaque bearer (no Azure resource).

### 4. (Optional) Remove the operator's data-plane role assignments

```bash
OBJ=$(az ad signed-in-user show --query id -o tsv)
# Only the two roles this stack granted, scoped to the (now-deleted) resources.
az role assignment list --assignee "$OBJ" -g "$RG" -o table
# Delete any that remain (Azure usually cascades these when the scope is deleted).
```

### 5. (Optional) Remove the deployed FQDN from the app registration

The `m8t-webapp` app reg's SPA redirect URIs may still list the deleted
Container App FQDN. Harmless, but to clean up:

```bash
az ad app show --id <client-id> --query spa.redirectUris -o json
# PATCH out the deleted https://<fqdn> entry if desired (see deploy/README.md step 7).
```

### 6. Verify

```bash
az resource list -g "$RG" --query "[?tags.\"m8t\"!=null]" -o table
```

Expected: empty. The RG and Foundry resources remain.

## GitHub App + KV secrets (brain feature)

The platform teardown does NOT touch:

- The GitHub App registration (it's in your GitHub account, not Azure).
- The three Key Vault secrets (`github-app-id`, `github-app-slug`, `github-app-private-key`) — they remain even after Bicep teardown if KV is preserved.

To remove the App:

1. **Uninstall App from all repos** (browser):
   - Open `https://github.com/settings/installations`
   - For each m8t-brain installation: **Configure → Uninstall**.

2. **Delete the App** (browser):
   - Open `https://github.com/settings/apps/<slug>/advanced`
   - **Delete GitHub App** at the bottom.

3. **Delete the KV secrets:**

   ```bash
   az keyvault secret delete --vault-name <kv> --name github-app-id
   az keyvault secret delete --vault-name <kv> --name github-app-slug
   az keyvault secret delete --vault-name <kv> --name github-app-private-key
   ```

   (Optionally purge: `az keyvault secret purge --vault-name <kv> --name <secret-name>` for each.)

4. **(Optional) Delete brain repos** — these are your data; cleanup is up to you:

   ```bash
   gh repo list --visibility private --limit 1000 | grep -- '-brain$' | awk '{print $1}'
   # then: gh repo delete <owner>/<repo-name> for any you want gone
   ```
