# Prerequisites — m8t

Everything that has to be true for m8t to install, and for a person to actually use it.

There are two lists here because they are answerable at different moments, and by different people:

- **Installing** — one person, once, before anything exists.
- **Using** — everyone who ever signs in, on a platform that already exists.

One command covers both:

```bash
m8t prereqs
```

It works out which phase you are in, tells you which one it ran, and reports what is missing. It changes
nothing unless you pass `--fix`.

```bash
m8t prereqs --fix                        # repair what can be repaired
m8t prereqs --fix --for alice@example.com  # an admin sets a teammate up
```

`--fix` grants Azure roles to a person. It deliberately does **not** touch the sign-in app
registration: that object is shared by every deployment in your tenant, so registering a redirect URI
belongs to the install, not to whoever happens to be diagnosing. `m8t prereqs` reports a missing
redirect URI and prints the exact command; it never writes it.

You do not normally have to run any of this by hand: `m8t bootstrap preflight` runs the install checks
before the installer starts, the install grants you your own platform's data-plane roles as it goes,
and `m8t bootstrap status --watch` completes the rest when it lands.

---

## Installing

The person running the install needs to be an **Owner** (or User Access Administrator) of the Azure
subscription. That is not a preference — the install creates a managed identity and assigns it roles, and
nothing else can do that.

<!-- BEGIN:prereq-install-table -->
| What | Why it matters | Status | Checked by |
|---|---|---|---|
| git, Azure CLI, Node 20+, and the m8t CLI on your machine | Nothing can run at all. | Handled for you | the install runbook |
| Signed in to Azure with an active subscription | Every Azure call fails immediately. | Checked — blocks until fixed | `m8t prereqs` |
| Owner or User Access Administrator at subscription scope | The install cannot create its managed identity or assign it roles. | Checked — blocks until fixed | `m8t prereqs` |
| Directory rights to register one Entra app (or a ready --client-id) | There is no app registration, so nobody can ever sign in to the webapp. | Checked — blocks until fixed | `m8t prereqs` |
| Every Azure resource provider the install uses is registered | The installer dies partway through creating resources, with an error that names a provider rather than anything actionable. | Checked — blocks until fixed | `m8t prereqs` |
| Model quota for the reasoning model in the target region | The install spends money creating resources and then cannot deploy the model the workers need. | Checked — blocks until fixed | `m8t prereqs` |
| A GitHub organization and the rights to install an App on it | The brain-backed workers have nowhere to keep their memory. | Checked — blocks until fixed | the install runbook |
| No Azure Policy or deny assignment blocking resource creation | The installer is refused by governance partway through, with a policy error. | **Not checked** — you may still hit it | — |
| The target region can host every service the platform uses | A resource fails to create in that region partway through the install. | **Not checked** — you may still hit it | — |
| No soft-deleted Cognitive Services account still holding the model quota | Quota looks free but the model deployment fails; the quota is held by an account you already deleted. | Checked — blocks until fixed | `m8t prereqs` |
| The subscription is active and can be billed | Resource creation is refused for billing reasons. | **Not checked** — you may still hit it | — |
<!-- END:prereq-install-table -->

The three rows marked **Not checked** are real risks we do not probe for. They are listed rather than
omitted so that a clean preflight is not mistaken for a guarantee. If your subscription is governed by
Azure Policy, or your organisation restricts which regions or services you may use, check with whoever
administers it before you start.

### Soft-deleted accounts and the quota that looks free

Deleting an Azure Cognitive Services (Foundry) account only **soft-deletes** it, and a soft-deleted
account keeps its model quota until it is **purged**. Quota can therefore read perfectly clear while
the capacity is already spoken for — so the install creates its resources and only then fails to
deploy the model. This is the usual reason a *second* install into the same subscription fails where
the first one worked.

Tell `m8t prereqs` which region you are installing into and it refuses when it finds a soft-deleted
account there, naming it, so you can decide before anything is created:

```bash
m8t prereqs --phase install --region <region>                                  # the check
az cognitiveservices account purge -n <name> -g <resource-group> -l <region>   # permanent
az cognitiveservices account recover -n <name> -g <resource-group> -l <region>  # if you meant to keep it
```

Run without a region, it warns instead and tells you which regions hold one — worth knowing before you
pick where to install. Only account kinds that can carry model deployments (`AIServices`, `OpenAI`,
`CognitiveServices`) are refused on; a soft-deleted Speech or Vision account holds no model quota and
is reported but never blocks you.

---

## Using

This is the list that surprises people, so it is worth stating plainly:

> **Being an Owner of the Azure subscription does not let you use the platform.**

Reading your AI team and talking to it are Azure **data actions**. Subscription-level roles — Owner,
Contributor, Reader — grant *none* of them. Someone who owns the whole subscription can install m8t
perfectly and then find that their workers will not load, which reads like a broken product rather than a
missing role.

<!-- BEGIN:prereq-usage-table -->
| What | Why it matters | Status | Checked by |
|---|---|---|---|
| The m8t CLI can find the platform you are pointed at | Every CLI command that talks to the platform fails to find it. | Checked — blocks until fixed | `m8t prereqs` |
| The webapp's sign-in redirect URI is registered on the app | Sign-in fails with AADSTS50011 on a platform that is otherwise perfectly healthy. | Handled for you | `m8t prereqs` |
| Your account can reach the Foundry data plane | Your AI team will not load, chat does not work, and the CLI and coding-agent plugin cannot reach your workers. Subscription Owner does NOT cover this — it is a data action, and control-plane roles carry none. | Handled for you | `m8t prereqs` |
| Your account can read the platform's Key Vault secrets | Deploying a worker fails — the coding agent and the Azure executor both read the vault as you. | Handled for you | `m8t prereqs` |
| Local state the coding-agent plugin needs (~/.m8t/repo-root, config) | The m8t plugin cannot list or reach your workers from an agent session. | Checked — warns only | `m8t doctor` |
<!-- END:prereq-usage-table -->

### If you installed the platform

The install grants you what you need and says so. It does this **while it is still running**, right
after the Foundry account and Key Vault exist — so even an install that fails at a later step still
leaves you able to sign in and diagnose it. If it could not grant you — you were offline, or someone
else administers your subscription — run `m8t prereqs --fix` when you can, or ask an administrator to
run `m8t prereqs --fix --for you@example.com`.

### If someone else installed it and you are joining

**For the web app, you need nothing at all.** Open the URL you were given and sign in with your work
account. The platform reaches Azure with its own identity, so no Azure roles are needed to use it in the
browser.

**Only if you also want the `m8t` CLI or the coding-agent plugin** do you need Azure access of your own,
because those run on your machine as you. Ask whoever administers the Azure subscription to run:

```bash
m8t prereqs --fix --for you@example.com
```

Then, on your machine:

```bash
az login
m8t prereqs
```

### Who can sign in

Anyone in your organisation's Microsoft Entra directory — including guests you have invited. The sign-in
app is registered as single-tenant, so someone outside your directory cannot sign in even if they have the
URL and an Azure account of their own; Microsoft rejects them before your platform is contacted.

If you want it tighter than "anyone in the directory", that is a native Entra control rather than an m8t
setting: turn on **User assignment required** on the m8t enterprise application, and assign the people who
should have access.

---

## When something is already broken

`m8t doctor` diagnoses a live setup — sign-in, configuration, gateway reachability, Foundry access, Key
Vault access, model quota — and prints a fix for each failure.

Common failures and what they actually mean:

| Symptom | Cause | Fix |
|---|---|---|
| "Couldn't load your AI team" | Your account has no Foundry data-plane role | `m8t prereqs --fix` |
| Sign-in fails with `AADSTS50011` | The webapp's redirect URI was never registered | Run `m8t bootstrap status --finalize`, or have a directory admin add it (`m8t prereqs` prints the exact command) |
| A worker deploy fails on the GitHub App health check | You cannot read the platform Key Vault | `m8t prereqs --fix` |
| The installer dies partway through | Usually a missing resource-provider registration or model quota | `m8t prereqs` before re-running |
| The install fails deploying the model, but quota looked fine | A soft-deleted account in that region still holds the quota | `m8t prereqs --phase install --region <region>` — it names the account and the purge command |
