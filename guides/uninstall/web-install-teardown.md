# `uninstall/web-install-teardown.md`: tear down an install made from the web page

> 🤖 **Agent runbook.** Use this if you installed from the install page in your browser (`m8t.run/ezra/install` or `wazari.ai/ezra/install`). That install put the platform in its **own resource group**, named `rg-m8t-<8 hex>` unless you chose another name. Every step that deletes or changes something is gated on an explicit operator confirmation, default **No**. Steps 1 and 2 only read.
>
> **Shells.** The commands work in bash and zsh. Step 1 saves what it finds to `~/.m8t/teardown-<resource group>/`, and each later step starts by loading it, because an agent's shell may not keep variables between commands.
>
> **The resource group is already gone?** Skip to [If the resource group is already deleted](#if-the-resource-group-is-already-deleted).

## What an install leaves outside its resource group

Deleting the resource group removes everything inside it. These objects live outside it:

| Object | Where it lives | Step |
|---|---|---|
| The gateway identity's two subscription-scope reader roles | Your subscription | 3 |
| The installer identity's subscription-scope Owner role, if the install did not remove it when it finished | Your subscription | 3 |
| The platform's sign-in app registration, with the platform's address as a redirect URI | Your Entra directory | 4 |
| Foundry's `…-AgentIdentityBlueprint` app registrations: one for the Foundry project and one per agent (a new install has three) | Your Entra directory | 5 |
| The soft-deleted Foundry account's quota hold | Your subscription | 7 |

Your GitHub App and brain repo are your data and are left in place (see the end).

## 1. Identify the install and save what you find (read-only)

```bash
RG=<install-rg>                  # shown on the install page's done screen; also in the Azure portal
STATE="$HOME/.m8t/teardown-$RG"; mkdir -p "$STATE"
SUB=$(az account show --query id -o tsv)
ACCT=$(az cognitiveservices account list -g "$RG" --query "[?kind=='AIServices'].name | [0]" -o tsv)
REGION=$(az cognitiveservices account list -g "$RG" --query "[?kind=='AIServices'].location | [0]" -o tsv)
GATEWAYS=$(az containerapp list -g "$RG" --query "length([?tags.m8t=='gateway'])" -o tsv)
GW=$(az containerapp list -g "$RG" --query "[?tags.m8t=='gateway'].name | [0]" -o tsv)
FQDN=$(az containerapp show -g "$RG" -n "$GW" --query properties.configuration.ingress.fqdn -o tsv)
APP_ID=$(az containerapp show -g "$RG" -n "$GW" \
  --query "properties.template.containers[0].env[?name=='AZURE_CLIENT_ID'].value | [0]" -o tsv)
APP_OBJ=$(az ad app show --id "$APP_ID" --query id -o tsv)
SP_OBJ=$(az ad sp show --id "$APP_ID" --query id -o tsv)
printf 'RG=%s\nSUB=%s\nACCT=%s\nREGION=%s\nGW=%s\nFQDN=%s\nAPP_ID=%s\nAPP_OBJ=%s\nSP_OBJ=%s\n' \
  "$RG" "$SUB" "$ACCT" "$REGION" "$GW" "$FQDN" "$APP_ID" "$APP_OBJ" "$SP_OBJ" > "$STATE/env"
{ az resource list -g "$RG" --query "[?identity.principalId!=null].identity.principalId" -o tsv
  az identity list -g "$RG" --query "[].principalId" -o tsv
} | sort -u > "$STATE/principals"
cat "$STATE/env"; echo "gateways: $GATEWAYS"; echo "identities: $(wc -l < "$STATE/principals")"
az resource list -g "$RG" --query "[].{name:name,type:type}" -o table
```

The identities in the group are captured here because after the group is deleted they no longer resolve. The system-assigned ones come from `az resource list`, and the user-assigned ones from `az identity list`.

**[PAUSE — operator]** Continue only if all of these hold:
- the group is the one the install created;
- `gateways` is `1`;
- every value in the env file is non-empty;
- `identities` is at least `1`.

Otherwise stop.

Every later step starts with these two lines:

```bash
RG=<install-rg>; STATE="$HOME/.m8t/teardown-$RG"; . "$STATE/env"
: "${SUB:?}" "${ACCT:?}" "${APP_ID:?}" "${APP_OBJ:?}" "${FQDN:?}"
```

## 2. List what those identities hold at subscription scope (read-only)

```bash
while IFS= read -r P; do
  az role assignment list --all --assignee-object-id "$P" \
    --query "[?scope=='/subscriptions/$SUB'].{role:roleDefinitionName,description:description,id:id}" -o tsv
done < "$STATE/principals"
```

You should see two lines for the gateway, **Cost Management Reader** and **Monitoring Reader**, each with the description `m8t-gateway auto-reap (bootstrap)`. You may also see **Owner** with the description `m8t-installer auto-reap (bootstrap)`. Newer versions of the install page delete that role when the install finishes.

## 3. Remove the subscription-scope roles

**[PAUSE — operator]** *"Delete the subscription-scope role assignments listed in step 2? They belong only to identities inside `$RG`. (default: No)"*

```bash
while IFS= read -r P; do
  az role assignment list --all --assignee-object-id "$P" \
    --query "[?scope=='/subscriptions/$SUB'].id" -o tsv \
  | while IFS= read -r id; do
      az rest --method delete --url "https://management.azure.com${id}?api-version=2022-04-01"
    done
done < "$STATE/principals"
touch "$STATE/roles-decided"
```

Run the `touch` line after a "No" too. Step 6 checks for this file, so the group is not deleted before the roles are decided.

## 4. The platform's sign-in app registration

Decide from what the app registration holds, not from its name:

```bash
TAGGED=$(az ad app show --id "$APP_ID" --query "contains(tags, 'm8t-install-created')" -o tsv)
OTHERS=$(az ad app show --id "$APP_ID" --query spa.redirectUris -o json | jq -c --arg u "https://$FQDN" '. - [$u]')
az ad app show --id "$APP_ID" --query "{name:displayName, tags:tags}" -o json
echo "tagged=$TAGGED  other redirect URIs=$OTHERS"
```

- **`tagged=true` and `other redirect URIs=[]`:** the install page created this app registration, and only this platform uses it. Offer 4a.
- **Anything else:** another platform, a developer, or an older version of the install page may depend on it. Don't delete it; offer 4b.

### 4a. Delete it

**[PAUSE — operator]** *"Delete the app registration `$APP_ID`, which only this platform uses? (default: No)"*

```bash
az ad app delete --id "$APP_ID"
az ad sp list --filter "appId eq '$APP_ID'" --query "length(@)" -o tsv   # expect 0; if not: az ad sp delete --id "$APP_ID"
```

A deleted app registration can be restored within 30 days ([Microsoft Learn](https://learn.microsoft.com/entra/identity-platform/howto-restore-app)). Through Graph, the service principal is restored separately:

```bash
az rest --method POST --url "https://graph.microsoft.com/v1.0/directory/deletedItems/$APP_OBJ/restore"
az rest --method POST --url "https://graph.microsoft.com/v1.0/directory/deletedItems/$SP_OBJ/restore"
```

### 4b. Remove only this platform's address

```bash
OTHERS=$(az ad app show --id "$APP_ID" --query spa.redirectUris -o json | jq -c --arg u "https://$FQDN" '. - [$u]')
echo "$OTHERS"   # what will remain
```

**[PAUSE — operator]** *"Remove `https://$FQDN` from the sign-in redirect URIs of `$APP_ID`, keeping the ones listed? (default: No)"*

```bash
: "${OTHERS:?}"
az rest --method PATCH --url "https://graph.microsoft.com/v1.0/applications/$APP_OBJ" \
  --headers "Content-Type=application/json" --body "{\"spa\":{\"redirectUris\":$OTHERS}}"
az ad app show --id "$APP_ID" --query spa.redirectUris -o json
```

## 5. Foundry's blueprint app registrations

They are named `<Foundry account>-<project>-…-AgentIdentityBlueprint`.

```bash
az ad app list --filter "startswith(displayName,'$ACCT-')" \
  --query "[?ends_with(displayName,'-AgentIdentityBlueprint')].[displayName,id]" -o tsv \
  > "$STATE/blueprints"
cat "$STATE/blueprints"; echo "count: $(wc -l < "$STATE/blueprints")"
```

**[PAUSE — operator]** Check that every name starts with `$ACCT-`. *"Delete these blueprint app registrations? (default: No)"*

```bash
cut -f2 "$STATE/blueprints" | while IFS= read -r id; do az ad app delete --id "$id"; done
```

**Who can delete these:**
- **Global Administrator** can.
- **Application Administrator** is refused; we measured that refusal.
- Microsoft's Graph documentation also names the blueprint's owner and the *Agent ID Administrator* role. We have not tested either.

Each blueprint's owner is a service principal, not you (measured). They can be restored within 30 days like the app registration in 4a, using each id in `$STATE/blueprints`.

## 6. Delete the resource group

```bash
[ -f "$STATE/roles-decided" ] || echo "STOP: run step 3 first"
```

**[PAUSE — operator]** *"Delete the entire resource group `$RG` and everything in it? (default: No)"*

```bash
[ -f "$STATE/roles-decided" ] && az group delete -n "$RG" --yes
```

## 7. Purge the soft-deleted Foundry account

The reason is in [`bootstrap-teardown.md`](bootstrap-teardown.md) step 5: an unpurged account holds its model quota for about 48 hours.

**[PAUSE — operator]** *"Purge the deleted Foundry account `$ACCT`? It cannot be recovered afterwards. (default: No)"*

```bash
az cognitiveservices account purge -n "$ACCT" -g "$RG" -l "$REGION"
```

## 8. Verify

```bash
az group exists -n "$RG"                                                             # expect false
while IFS= read -r P; do
  az role assignment list --all --assignee-object-id "$P" --query "[?scope=='/subscriptions/$SUB'].id" -o tsv
done < "$STATE/principals"                                                           # expect nothing
az ad app list --app-id "$APP_ID" --query "length(@)" -o tsv                         # 0 after 4a
az ad app list --app-id "$APP_ID" --query "[].spa.redirectUris" -o json              # after 4b: no https://$FQDN
az ad app list --filter "startswith(displayName,'$ACCT-')" --query "length(@)" -o tsv   # 0 after step 5
az cognitiveservices account list-deleted --query "length([?name=='$ACCT'])" -o tsv  # 0 after step 7
```

## If the resource group is already deleted

The identities can no longer be looked up, so this finds the leftovers by what they carry.

```bash
RG=<install-rg>; STATE="$HOME/.m8t/teardown-$RG"; mkdir -p "$STATE"
SUB=$(az account show --query id -o tsv)
# The Foundry account, if it is still soft-deleted (its id contains /resourceGroups/<group>/):
az cognitiveservices account list-deleted -o json \
  | jq -r --arg rg "/resourcegroups/$RG/" '.[] | select(.id | ascii_downcase | contains($rg | ascii_downcase)) | "\(.name) \(.location)"'
# The sign-in app registration, if the install page created it:
az ad app list --filter "displayName eq 'm8t-install-$RG'" \
  --query "[].{appId:appId,id:id,tags:tags,redirects:spa.redirectUris}" -o json
# Subscription-scope roles left by install identities whose principal no longer exists:
az role assignment list --all \
  --query "[?scope=='/subscriptions/$SUB' && (description=='m8t-gateway auto-reap (bootstrap)' || description=='m8t-installer auto-reap (bootstrap)') && !principalName].{role:roleDefinitionName,principal:principalId,id:id}" -o table
```

- **Foundry account:** if one is listed, write `ACCT` and `REGION` into `$STATE/env` and run steps 5 and 7. If the account has already been purged but you know its name, step 5 still works.
- **App registration:** if it is listed, write `APP_ID`, `APP_OBJ` and `SUB` into `$STATE/env`. Set `FQDN` to this platform's host from its redirect URIs, then follow step 4.
- **Roles:**
  - Each role listed belongs to an identity that no longer exists; the `!principalName` filter selects those.
  - Before deleting one, confirm its principal is gone: `az ad sp show --id <principal>` must fail. Then delete it by id:

    ```bash
    az rest --method delete --url "https://management.azure.com<id>?api-version=2022-04-01"
    ```

  - Roles left by other deleted installs match too, and they are just as orphaned.
  - Never delete a role whose principal still resolves.

## GitHub App and brain repo (your data, left in place)

As in [`bootstrap-teardown.md`](bootstrap-teardown.md):
- uninstall the App at `https://github.com/settings/installations`;
- delete it at `https://github.com/settings/apps/<slug>/advanced`;
- delete the brain repo only if you want its data gone: `gh repo delete <org>/<repo>`.
