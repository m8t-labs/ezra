# `uninstall/web-install-teardown.md`: tear down an install made from the web page

> 🤖 **Agent runbook.** Use this if you installed from the install page in your browser (`m8t.run/ezra/install` or `wazari.ai/ezra/install`). That install put the platform in its **own resource group**; the done screen names it. Every step that deletes or changes something is gated on an explicit operator confirmation, default **No**. Steps 1 and 2 change nothing in Azure; step 1 writes local state.
>
> **Needs:** `az`, signed in to the subscription, and `jq`. The commands work in bash and zsh.
>
> **State between commands.** Step 1 saves what it finds to `~/.m8t/teardown-<resource group>/`. An agent's shell may not keep variables between commands, so **every code block below starts by loading that file**, and checks the values it uses.
>
> **The resource group is already gone?** Skip to [If the resource group is already deleted](#if-the-resource-group-is-already-deleted).

## What an install leaves outside its resource group

Deleting the resource group removes everything inside it. These objects live outside it:

| Object | Where it lives | Step |
|---|---|---|
| The gateway identity's two subscription-scope reader roles | Your subscription | 3 |
| The installer identity's subscription-scope Owner role, if the install did not remove it | Your subscription | 3 |
| The platform's sign-in app registration, with the platform's address as a redirect URI | Your Entra directory | 4 |
| Foundry's `…-AgentIdentityBlueprint` app registrations: one for the Foundry project and one per agent, so about three on a new install | Your Entra directory | 5 |
| The soft-deleted Foundry account's quota hold | Your subscription | 7 |

Your GitHub App and brain repo are your data and are left in place (see the end).

## 1. Identify the install and save what you find (changes nothing in Azure)

```bash
RG='<install-rg>'                  # the name on the install page's done screen
STATE="$HOME/.m8t/teardown-$RG"; mkdir -p "$STATE"; rm -f "$STATE/roles-decided"
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
printf "RG='%s'\nSUB='%s'\nACCT='%s'\nREGION='%s'\nGW='%s'\nFQDN='%s'\nAPP_ID='%s'\nAPP_OBJ='%s'\nSP_OBJ='%s'\n" \
  "$RG" "$SUB" "$ACCT" "$REGION" "$GW" "$FQDN" "$APP_ID" "$APP_OBJ" "$SP_OBJ" > "$STATE/env"
{ az resource list -g "$RG" --query "[?identity.principalId!=null].identity.principalId" -o tsv
  az identity list -g "$RG" --query "[].principalId" -o tsv
} | sort -u > "$STATE/principals"
cat "$STATE/env"; echo "gateways: $GATEWAYS"; echo "identities: $(wc -l < "$STATE/principals")"
az resource list -g "$RG" --query "[].{name:name,type:type}" -o table
```

The group's identities are captured now because once the group is deleted they no longer resolve. System-assigned ones come from `az resource list`, user-assigned ones from `az identity list`.

**[PAUSE — operator]** Continue only if all of these hold:
- the group is the one the install created;
- `gateways` is `1`;
- every value in the env file is non-empty;
- `identities` is at least `1`.

Otherwise stop.

## 2. List what those identities hold at subscription scope (read-only)

```bash
RG='<install-rg>'; STATE="$HOME/.m8t/teardown-$RG"; . "$STATE/env"; : "${SUB:?}"
while IFS= read -r P; do
  az role assignment list --all --assignee-object-id "$P" \
    --query "[?scope=='/subscriptions/$SUB'].{role:roleDefinitionName,description:description,id:id}" -o tsv
done < "$STATE/principals"
```

You should see two lines for the gateway, **Cost Management Reader** and **Monitoring Reader**, each with the description `m8t-gateway auto-reap (bootstrap)`. You may also see **Owner** with the description `m8t-installer auto-reap (bootstrap)`.

## 3. Remove the subscription-scope roles

**[PAUSE — operator]** *"Delete the subscription-scope role assignments listed in step 2? They belong only to identities inside `$RG`. (default: No)"*

On yes:

```bash
RG='<install-rg>'; STATE="$HOME/.m8t/teardown-$RG"; . "$STATE/env"; : "${SUB:?}"
while IFS= read -r P; do
  az role assignment list --all --assignee-object-id "$P" \
    --query "[?scope=='/subscriptions/$SUB'].id" -o tsv \
  | while IFS= read -r id; do
      az rest --method delete --url "https://management.azure.com${id}?api-version=2022-04-01"
    done
done < "$STATE/principals"
```

Then, whatever the answer, record that the roles were decided. Step 6 refuses to delete the group without this file.

```bash
RG='<install-rg>'; touch "$HOME/.m8t/teardown-$RG/roles-decided"
```

## 4. The platform's sign-in app registration

The app registration is deleted only if the install page created it (`m8t-install-created` tag) **and** it holds no redirect URI but this platform's. Otherwise another platform, a developer, or an older version of the install page may depend on it, so only this platform's address is removed (4b).

```bash
RG='<install-rg>'; STATE="$HOME/.m8t/teardown-$RG"; . "$STATE/env"; : "${APP_ID:?}" "${FQDN:?}"
az ad app show --id "$APP_ID" --query "{name:displayName, tags:tags, redirects:spa.redirectUris}" -o json
TAGGED=$(az ad app show --id "$APP_ID" --query "contains(tags || \`[]\`, 'm8t-install-created')" -o tsv)
OTHERS=$(az ad app show --id "$APP_ID" --query spa.redirectUris -o json \
  | jq -c --arg u "https://$FQDN" '. - [$u, $u + "/"]')
echo "tagged=$TAGGED  other redirect URIs=$OTHERS"
[ "$TAGGED" = true ] && [ "$OTHERS" = "[]" ] && echo "=> 4a: delete it" || echo "=> 4b: remove only this platform's address"
```

### 4a. Delete it

**[PAUSE — operator]** *"Delete the app registration `$APP_ID`, which only this platform uses? (default: No)"*

```bash
RG='<install-rg>'; STATE="$HOME/.m8t/teardown-$RG"; . "$STATE/env"; : "${APP_ID:?}" "${FQDN:?}"
TAGGED=$(az ad app show --id "$APP_ID" --query "contains(tags || \`[]\`, 'm8t-install-created')" -o tsv)
OTHERS=$(az ad app show --id "$APP_ID" --query spa.redirectUris -o json \
  | jq -c --arg u "https://$FQDN" '. - [$u, $u + "/"]')
if [ "$TAGGED" = true ] && [ "$OTHERS" = "[]" ]; then
  az ad app delete --id "$APP_ID"
  az ad sp list --filter "appId eq '$APP_ID'" --query "length(@)" -o tsv   # expect 0; if not: az ad sp delete --id "$APP_ID"
else
  echo "REFUSED: not install-created, or other redirect URIs remain; use 4b"
fi
```

The app registration can be restored within 30 days ([Microsoft Learn](https://learn.microsoft.com/entra/identity-platform/howto-restore-app)). Restoring an application does not restore its service principal ([Microsoft Learn](https://learn.microsoft.com/powershell/module/microsoft.entra.directorymanagement/restore-entradeleteddirectoryobject)), so restore both:

```bash
RG='<install-rg>'; . "$HOME/.m8t/teardown-$RG/env"; : "${APP_OBJ:?}" "${SP_OBJ:?}"
az rest --method POST --url "https://graph.microsoft.com/v1.0/directory/deletedItems/$APP_OBJ/restore"
az rest --method POST --url "https://graph.microsoft.com/v1.0/directory/deletedItems/$SP_OBJ/restore"
```

### 4b. Remove only this platform's address

**[PAUSE — operator]** Show the `other redirect URIs` list from step 4. *"Remove `https://$FQDN` from the sign-in redirect URIs of `$APP_ID`, keeping the ones listed? (default: No)"*

```bash
RG='<install-rg>'; STATE="$HOME/.m8t/teardown-$RG"; . "$STATE/env"; : "${APP_ID:?}" "${APP_OBJ:?}" "${FQDN:?}"
OTHERS=$(az ad app show --id "$APP_ID" --query spa.redirectUris -o json \
  | jq -c --arg u "https://$FQDN" '. - [$u, $u + "/"]')
: "${OTHERS:?}"
az rest --method PATCH --url "https://graph.microsoft.com/v1.0/applications/$APP_OBJ" \
  --headers "Content-Type=application/json" --body "{\"spa\":{\"redirectUris\":$OTHERS}}"
az ad app show --id "$APP_ID" --query spa.redirectUris -o json
```

## 5. Foundry's blueprint app registrations

They are named `<Foundry account>-<project>-…-AgentIdentityBlueprint`.

```bash
RG='<install-rg>'; STATE="$HOME/.m8t/teardown-$RG"; . "$STATE/env"; : "${ACCT:?}"
az ad app list --filter "startswith(displayName,'$ACCT-')" \
  --query "[?ends_with(displayName,'-AgentIdentityBlueprint')].[displayName,id,appId]" -o tsv \
  > "$STATE/blueprints"
cat "$STATE/blueprints"; echo "count: $(wc -l < "$STATE/blueprints")"
```

**[PAUSE — operator]** Check that every name starts with `$ACCT-`. *"Delete these blueprint app registrations? (default: No)"*

```bash
RG='<install-rg>'; STATE="$HOME/.m8t/teardown-$RG"; [ -s "$STATE/blueprints" ] || { echo "run the listing first"; false; } &&
cut -f2 "$STATE/blueprints" | while IFS= read -r id; do az ad app delete --id "$id"; done
```

**Who can delete these:**
- **Global Administrator** can.
- **Application Administrator** was refused when we tried it.
- [Microsoft Learn](https://learn.microsoft.com/entra/agent-id/howto-delete-agent-identity) names *Agent ID Administrator* and *Cloud Application Administrator* for managing and deleting agent identity objects. We have not tried either.
- Each blueprint's owner is a service principal, not you (measured).

Deleting a blueprint also soft-deletes its agent identities, in the background ([Microsoft Learn](https://learn.microsoft.com/entra/agent-id/concept-agent-identity-deletion)). A blueprint can be restored within 30 days through Microsoft Graph; the admin center does not restore agent identity objects ([Microsoft Learn](https://learn.microsoft.com/entra/agent-id/howto-delete-agent-identity)). Restore the application ([Microsoft Learn](https://learn.microsoft.com/entra/identity-platform/howto-restore-app)), then its service principal; we have not run this restore. Use the object id (column 2) and the app id (column 3) from `$STATE/blueprints`:

```bash
OBJ='<object-id>'; APPID='<app-id>'
az rest --method POST --url "https://graph.microsoft.com/v1.0/directory/deletedItems/$OBJ/restore"
SP=$(az rest --method GET \
  --url "https://graph.microsoft.com/v1.0/directory/deletedItems/microsoft.graph.servicePrincipal?\$filter=appId eq '$APPID'" \
  --query "value[0].id" -o tsv)
[ -n "$SP" ] && az rest --method POST --url "https://graph.microsoft.com/v1.0/directory/deletedItems/$SP/restore" \
  || echo "no deleted service principal for $APPID"
```

Agent identities that the background cleanup already removed must each be restored separately.

## 6. Delete the resource group

**[PAUSE — operator]** *"Delete the entire resource group `$RG` and everything in it? (default: No)"*

```bash
RG='<install-rg>'; STATE="$HOME/.m8t/teardown-$RG"
if [ -f "$STATE/roles-decided" ] && [ "$STATE/roles-decided" -nt "$STATE/env" ]; then
  az group delete -n "$RG" --yes
else
  echo "REFUSED: decide the roles in step 3 first"
fi
```

## 7. Purge the soft-deleted Foundry account

The reason is in [`bootstrap-teardown.md`](bootstrap-teardown.md) step 5: an unpurged account holds its model quota for about 48 hours.

**[PAUSE — operator]** *"Purge the deleted Foundry account `$ACCT`? It cannot be recovered afterwards. (default: No)"*

```bash
RG='<install-rg>'; . "$HOME/.m8t/teardown-$RG/env"; : "${ACCT:?}" "${REGION:?}"
az cognitiveservices account purge -n "$ACCT" -g "$RG" -l "$REGION"
```

## 8. Verify

For the main path. After the recovery path, run its listing again, step 5's listing (expect `count: 0`), and step 4's first block.

```bash
RG='<install-rg>'; STATE="$HOME/.m8t/teardown-$RG"; . "$STATE/env"; : "${SUB:?}" "${ACCT:?}" "${APP_ID:?}"
az group exists -n "$RG"                                                             # expect false
while IFS= read -r P; do
  az role assignment list --all --assignee-object-id "$P" --query "[?scope=='/subscriptions/$SUB'].id" -o tsv
done < "$STATE/principals"                                                           # expect nothing
az ad app list --app-id "$APP_ID" --query "length(@)" -o tsv                         # 0 after 4a
az ad app list --app-id "$APP_ID" --query "[].spa.redirectUris" -o json              # after 4b: no https://$FQDN
az ad app list --filter "startswith(displayName,'$ACCT-')" --query "length([?ends_with(displayName,'-AgentIdentityBlueprint')])" -o tsv   # 0 after step 5
az cognitiveservices account list-deleted --query "length([?name=='$ACCT'])" -o tsv  # 0 after step 7
```

## If the resource group is already deleted

The group's identities can no longer be looked up, so this finds what is left by what it carries. It only lists; the deletes are the gated steps above, or the gated block at the end.

```bash
RG='<install-rg>'; STATE="$HOME/.m8t/teardown-$RG"; mkdir -p "$STATE"
SUB=$(az account show --query id -o tsv)
echo "## the Foundry account, if still soft-deleted (its id contains /resourceGroups/<group>/)"
az cognitiveservices account list-deleted -o json \
  | jq -r --arg rg "/resourcegroups/$RG/" '.[] | select(.id | ascii_downcase | contains($rg | ascii_downcase)) | "\(.name) \(.location)"'
echo "## the sign-in app registration, if the install page created it"
az ad app list --filter "displayName eq 'm8t-install-$RG'" --query "[].{appId:appId,id:id,tags:tags,redirects:spa.redirectUris}" -o json
echo "## subscription-scope install roles, with the name az found for each principal"
az role assignment list --all \
  --query "[?scope=='/subscriptions/$SUB' && (description=='m8t-gateway auto-reap (bootstrap)' || description=='m8t-installer auto-reap (bootstrap)')].{role:roleDefinitionName,principal:principalId,name:principalName,id:id}" -o table
```

**Foundry account and app registration.** Add what the listing found to the state file, then run the matching steps above:
- step 5 for the blueprints, which needs `ACCT`;
- step 7 for the purge, which needs `ACCT` and `REGION`;
- step 4 for the app registration, which needs `APP_ID`, `APP_OBJ`, `SP_OBJ` (`az ad sp show --id <appId> --query id -o tsv`), and `FQDN`, your platform's address from the done screen without `https://`. If no `m8t-install-<group>` app was listed, your platform used an older, shared `m8t-webapp`. `az ad app list --display-name m8t-webapp` matches by prefix and can list several; take the ids of the one whose redirect URIs include your platform's address, and run 4b.

Step 4 deletes only when the app registration carries the install tag and holds no other address. Append only the lines for values you found; a later line overrides an earlier one when the file is loaded:

```bash
RG='<install-rg>'; E="$HOME/.m8t/teardown-$RG/env"
echo "RG='$RG'" >> "$E"
echo "ACCT='<account-name>'" >> "$E"; echo "REGION='<location>'" >> "$E"
echo "APP_ID='<appId>'" >> "$E"; echo "APP_OBJ='<id>'" >> "$E"; echo "SP_OBJ='<sp-id>'" >> "$E"; echo "FQDN='<platform-host>'" >> "$E"
```

**Roles.** A role whose `name` column is empty is orphaned: az looked its principal up and found nothing. If every row shows an empty name, including roles of platforms you still run, az could not read the directory; stop and fix access first.

**[PAUSE — operator]** *"Delete the role `<id>` held by the deleted principal `<principal>`? (default: No)"* For each role, on yes:

```bash
P='<principal>'; ID='<id>'
if [ "$(az role assignment list --all --query "[?id=='$ID' && principalName=='' && (description=='m8t-gateway auto-reap (bootstrap)' || description=='m8t-installer auto-reap (bootstrap)')].principalId | [0]" -o tsv)" = "$P" ] \
   && az ad sp show --id "$P" 2>&1 | grep -q "does not exist"; then
  az rest --method delete --url "https://management.azure.com${ID}?api-version=2022-04-01"
else
  echo "REFUSED: not an install role with an empty principal name held by that principal, or that principal is a service principal that exists"
fi
```

Roles left by other deleted installs match too, and they are just as orphaned.

## GitHub App and brain repo (your data, left in place)

As in [`bootstrap-teardown.md`](bootstrap-teardown.md):
- uninstall the App at `https://github.com/settings/installations`;
- delete it at `https://github.com/settings/apps/<slug>/advanced`;
- delete the brain repo only if you want its data gone: `gh repo delete <org>/<repo>`.
