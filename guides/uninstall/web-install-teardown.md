# `uninstall/web-install-teardown.md`: tear down an install made from the web page

> 🤖 **Agent runbook.** Use this if you installed from the install page in your browser (`m8t.run/ezra/install` or `wazari.ai/ezra/install`). That install put the platform in its **own resource group**, named `rg-m8t-<8 hex>` unless you chose another name. Every destructive step is gated on an explicit operator confirmation. Steps 1–3 are read-only.

## What an install leaves outside its resource group

Deleting the resource group removes everything inside it. These objects live outside it, so this runbook removes them one by one:

| Object | Where it lives | Removed in |
|---|---|---|
| The install's sign-in app registration and its service principal | Your Entra directory | Step 5 |
| The platform's address, as a sign-in redirect URI on that app registration | On the app registration | Step 5 (goes with it) |
| About three `…-AgentIdentityBlueprint` app registrations, created by Foundry | Your Entra directory | Step 6 |
| The gateway identity's two subscription-scope reader roles | Your subscription | Step 4 |
| The installer identity's subscription-scope Owner role, if the install did not remove it when it finished | Your subscription | Step 4 |
| The soft-deleted Foundry account's quota hold | Your subscription | Step 8 |

Your GitHub App and brain repo are your data and are left in place (see the end).

## 1. Identify the install (read-only)

```bash
RG=<install-rg>                  # shown on the install page's done screen; also in the Azure portal
SUB=$(az account show --query id -o tsv)
ACCT=$(az cognitiveservices account list -g "$RG" --query "[?kind=='AIServices'].name | [0]" -o tsv)
REGION=$(az cognitiveservices account list -g "$RG" --query "[?kind=='AIServices'].location | [0]" -o tsv)
GW=$(az containerapp list -g "$RG" --query "[?tags.m8t=='gateway'].name | [0]" -o tsv)
APP_ID=$(az containerapp show -g "$RG" -n "$GW" \
  --query "properties.template.containers[0].env[?name=='AZURE_CLIENT_ID'].value | [0]" -o tsv)
echo "RG=$RG ACCT=$ACCT REGION=$REGION GW=$GW APP_ID=$APP_ID"
az resource list -g "$RG" --query "[].{name:name,type:type}" -o table
```

**[PAUSE, operator]** Confirm the group is the one the install created, and that it holds the Foundry account and a gateway. Stop if anything unexpected appears.

## 2. List the identities in the group (read-only)

Capture these **before** the group is deleted. Afterwards, the principals no longer resolve.

```bash
PRINCIPALS=$( {
  az resource list -g "$RG" --query "[?identity.principalId!=null].identity.principalId" -o tsv
  az identity list -g "$RG" --query "[].principalId" -o tsv
} | sort -u )
echo "$PRINCIPALS"
```

## 3. List what those identities hold at subscription scope (read-only)

```bash
for P in $PRINCIPALS; do
  az role assignment list --all --assignee-object-id "$P" \
    --query "[?scope=='/subscriptions/$SUB'].{role:roleDefinitionName,description:description,id:id}" -o tsv
done
```

You should see two lines for the gateway, **Cost Management Reader** and **Monitoring Reader**, each with the description `m8t-gateway auto-reap (bootstrap)`. You may also see **Owner** with the description `m8t-installer auto-reap (bootstrap)`. Newer versions of the install page delete that role when the install finishes, and older ones leave it.

## 4. Remove the subscription-scope roles

**[PAUSE, operator]** *"Delete the subscription-scope role assignments listed in step 3? They belong only to identities inside `$RG`. (default: No)"* Proceed only on an explicit yes.

```bash
for P in $PRINCIPALS; do
  az role assignment list --all --assignee-object-id "$P" \
    --query "[?scope=='/subscriptions/$SUB'].id" -o tsv \
  | while IFS= read -r id; do
      az rest --method delete --url "https://management.azure.com${id}?api-version=2022-04-01"
    done
done
```

These are the same gateway roles [`bootstrap-teardown.md`](bootstrap-teardown.md) step 3 removes. If the group is already gone, use the recovery path there: delete by assignment id, never by role name. Other gateways in the subscription hold the same role names.

## 5. Remove the install's sign-in app registration

Your platform signs people in with one app registration. `APP_ID` from step 1 is its client id. Deleting it also removes its service principal and the platform's redirect URI.

```bash
az ad app show --id "$APP_ID" --query "{name:displayName, tags:tags, redirects:spa.redirectUris}" -o json
```

- **Named `m8t-install-<resource group>`, with `m8t-install-created` in `tags`:** it belongs to this install alone.
- **Named `m8t-webapp`** (older versions of the install page): several platforms in one directory can share it. Delete it only if no other platform you keep uses it. Check each other gateway's `AZURE_CLIENT_ID` with the step 1 command. If another platform shares it, don't delete it; remove only this platform's redirect URI (below).

**[PAUSE, operator]** *"Delete the app registration `<name>` (`$APP_ID`)? (default: No)"*

```bash
az ad app delete --id "$APP_ID"
```

Deleting it needs Application Administrator, Cloud Application Administrator or Global Administrator, or ownership of the app registration. A deleted app registration can be restored for 30 days:

```bash
az rest --method POST --url "https://graph.microsoft.com/v1.0/directory/deletedItems/<object-id>/restore"
```

**Keeping a shared `m8t-webapp` and removing only this platform's redirect URI:**

```bash
FQDN=$(az containerapp show -g "$RG" -n "$GW" --query properties.configuration.ingress.fqdn -o tsv)
OBJ=$(az ad app show --id "$APP_ID" --query id -o tsv)
KEEP=$(az ad app show --id "$APP_ID" --query spa.redirectUris -o json | jq -c --arg u "https://$FQDN" '. - [$u]')
az rest --method PATCH --url "https://graph.microsoft.com/v1.0/applications/$OBJ" \
  --headers "Content-Type=application/json" --body "{\"spa\":{\"redirectUris\":$KEEP}}"
```

## 6. Remove the Foundry blueprint app registrations

Foundry creates about three `AgentIdentityBlueprint` app registrations for the platform, named after the Foundry account. They are not in the resource group.

```bash
az ad app list --filter "startswith(displayName,'$ACCT-')" \
  --query "[?ends_with(displayName,'-AgentIdentityBlueprint')].{name:displayName,id:id,created:createdDateTime}" -o table
```

**[PAUSE, operator]** *"Delete these blueprint app registrations? (default: No)"*

```bash
az ad app list --filter "startswith(displayName,'$ACCT-')" \
  --query "[?ends_with(displayName,'-AgentIdentityBlueprint')].id" -o tsv \
| while IFS= read -r id; do az ad app delete --id "$id"; done
```

**Who can delete these:** a **Global Administrator**. **Application Administrator is refused**; we measured that refusal. Microsoft's Graph documentation also names an owner of the blueprint and the *Agent ID Administrator* role; we have not tested either. Their owner is a service principal, not you. They can be restored for 30 days with the command in step 5.

## 7. Delete the resource group

**[PAUSE, operator]** *"Delete the entire resource group `$RG` and everything in it? (default: No)"*

```bash
az group delete -n "$RG" --yes
```

## 8. Purge the soft-deleted Foundry account

```bash
az cognitiveservices account purge -n "$ACCT" -g "$RG" -l "$REGION"
```

The reason is in [`bootstrap-teardown.md`](bootstrap-teardown.md) step 5: an unpurged account holds its model quota for about 48 hours.

## 9. Verify

```bash
az group show -n "$RG" 2>/dev/null || echo "group gone"
for P in $PRINCIPALS; do az role assignment list --all --assignee-object-id "$P" --query "[].id" -o tsv; done   # expect empty
az ad app show --id "$APP_ID" 2>/dev/null || echo "sign-in app registration gone"   # unless you kept a shared m8t-webapp
az ad app list --filter "startswith(displayName,'$ACCT-')" --query "[].displayName" -o tsv   # expect empty
az cognitiveservices account list-deleted --query "[?name=='$ACCT'].name" -o tsv            # expect empty
```

## GitHub App and brain repo (your data, left in place)

As in [`bootstrap-teardown.md`](bootstrap-teardown.md): uninstall the App at `https://github.com/settings/installations`, delete it at `https://github.com/settings/apps/<slug>/advanced`, and delete the brain repo only if you want its data gone (`gh repo delete <org>/<repo>`).
