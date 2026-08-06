# `uninstall/bootstrap-teardown.md` — tear down a cloud-bootstrap install

> 🤖 **Agent runbook.** Use this ONLY if you installed via [`bootstrap.md`](../bootstrap.md) — i.e.
> the platform lives in its **own dedicated resource group** (Foundry + gateway + workers all
> together). If instead you deployed the comms infra **into an existing Foundry RG**, use the
> tag-scoped [`azure-infra.md`](azure-infra.md) — deleting the RG there would destroy your Foundry
> agents. Every destructive step is gated on an explicit operator confirmation.

## What this removes

The whole dedicated install: the resource group (Foundry account + project + model, gateway
Container App + Service Bus + Storage + Key Vault + Log Analytics + App Insights + Container Apps
Environment), the worker agents, **and** the two cloud artifacts that outlive an RG-delete (the
soft-deleted Foundry account's quota hold, and the gateway identity's subscription-scoped reader
roles). Your GitHub App + brain repos are your data and are left in place (see the end).

## 1. Identify the install (read-only)

```bash
RG=<install-rg>                 # the dedicated RG bootstrap created (e.g. from ~/.m8t/bootstrap.json)
SUB=$(az account show --query id -o tsv)

# The Foundry account in that RG (its name is what you must PURGE in step 4):
ACCT=$(az cognitiveservices account list -g "$RG" --query "[?kind=='AIServices'].name | [0]" -o tsv)
REGION=$(az cognitiveservices account list -g "$RG" --query "[?kind=='AIServices'].location | [0]" -o tsv)
echo "RG=$RG  ACCT=$ACCT  REGION=$REGION"

# Show everything that will be deleted. CONFIRM this is a bootstrap-created dedicated RG
# (it holds the Foundry account) and NOT a shared/Foundry RG you want to keep:
az resource list -g "$RG" --query "[].{name:name,type:type}" -o table
```

**[PAUSE — operator]** Confirm the RG is the throwaway/dedicated install and contains the Foundry
account. Stop if anything unexpected appears.

## 2. Capture the gateway identity's principal id BEFORE deleting (load-bearing)

The gateway holds **subscription-scoped** reader roles (Cost Management Reader + Monitoring Reader)
that an RG-delete does **not** remove. Capture the principal now so you can delete exactly those —
and nothing else (other gateways in the same subscription hold the same role names).

```bash
GW_PID=$(az containerapp show -g "$RG" \
  -n "$(az containerapp list -g "$RG" --query '[0].name' -o tsv)" \
  --query "identity.principalId" -o tsv)
echo "gateway principalId = $GW_PID"   # must be non-empty
```

> ⚠️ If the gateway uses a user-assigned identity instead, get its principalId from
> `az identity list -g "$RG"`. Either way you need **this install's** principal — never delete
> another gateway's sub-scope roles.

## 3. Remove the gateway's subscription-scoped roles (cleaner BEFORE the RG-delete)

While the principal still resolves, a normal delete works (no REST fallback needed). Do this first:

```bash
for ROLE in "Cost Management Reader" "Monitoring Reader"; do
  az role assignment delete --assignee "$GW_PID" --role "$ROLE" --scope "/subscriptions/$SUB"
done
# verify none remain for this principal at sub scope:
az role assignment list --all --query "[?principalId=='$GW_PID' && scope=='/subscriptions/$SUB'].roleDefinitionName" -o tsv
```

(The gateway's other roles are scoped to resources **inside** the RG and cascade away with it.)

> **Recovery path** — if you already deleted the RG and skipped this, the principal is gone and
> `az role assignment delete --assignee/--ids/--name` all fail. Delete by assignment id via REST:
>
> ```bash
> az role assignment list --all --query "[?principalId=='$GW_PID'].id" -o tsv | while IFS= read -r id; do
>   az rest --method delete --url "https://management.azure.com${id}?api-version=2022-04-01"
> done
> ```

## 4. Delete the resource group

**[PAUSE — operator]** *"Delete the entire resource group `$RG` and everything in it (Foundry +
gateway + workers)? (default: No)"* — proceed only on explicit yes.

```bash
az group delete -n "$RG" --yes      # cascades the Foundry project + account (account → soft-delete)
```

## 5. PURGE the soft-deleted Foundry account (REQUIRED)

An RG-delete only **soft-deletes** the AIServices account, and a soft-deleted account keeps holding
its model-capacity quota for ~48h — so the *next* install in this subscription fails with a vague
`(715-123420)` that is actually quota exhaustion. Purge it:

```bash
az cognitiveservices account purge -n "$ACCT" -g "$RG" -l "$REGION"
az cognitiveservices account list-deleted --query "[?name=='$ACCT'].name" -o tsv   # expect: empty
```

If you skip this, the next install does not fail silently: `m8t prereqs` (and `m8t bootstrap
preflight`) refuse when a soft-deleted account sits in the region you are installing into, and name it
along with this purge command.

## 6. Reap any leftover installer scaffolding (if an install was interrupted)

```bash
m8t bootstrap reap     # idempotent; removes a leftover installer ACI + its MI + the MI's role assignments
```

> **If the install failed** (`m8t bootstrap status` shows `failed`), `m8t bootstrap reap` refuses by default (it leaves the installer up for diagnosis). Reap it anyway with:
>
> ```bash
> m8t bootstrap reap --force
> ```
>
> **Note — the gateway uses a *system-assigned* identity.** For the roles-first cleanup, read its principalId with `az containerapp show -g <rg> -n <gateway> --query identity.principalId -o tsv` (not `az identity list`, which only shows user-assigned identities).

## 7. Verify

```bash
az group show -n "$RG" 2>/dev/null || echo "RG gone ✓"
az cognitiveservices account list-deleted --query "[?name=='$ACCT']" -o table   # expect empty
az role assignment list --all --query "[?principalId=='$GW_PID'].id" -o tsv      # expect empty
```

> **Note — orphaned sub-scope roles from past throwaway installs.** If several principals hold
> Cost Management Reader / Monitoring Reader at subscription scope, some may be leftovers from
> earlier installs that skipped step 3/the recovery path (the principal is long gone). Clean a
> confirmed-orphan with the REST recovery path above — but **never** remove a role belonging to a
> gateway you still run.

## GitHub App + brain repos (your data — left in place)

Teardown does **not** touch your per-founder GitHub App or the brain repos it created — they are
yours and reusable on the next install. To remove the App: open
`https://github.com/settings/installations` → Configure → Uninstall, then delete it at
`https://github.com/settings/apps/<slug>/advanced`. Delete brain repos only if you want the data
gone: `gh repo delete <org>/<repo>`.
