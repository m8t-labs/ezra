# Operate & maintain your platform

> 📖 **Human guide.** Read this yourself — it explains and references, it doesn't auto-execute. Where a step is a command, you (or your agent) run it.
>
> 💬 **Or just ask.** With the `m8t` plugin installed, say *"add Ilan to the team"* or *"bind cmo to Telegram"* — the bundled `m8t-cli` skill drives these commands for you.

Once your platform is deployed (see [`deploy.md`](deploy.md)), this is how you run it day-to-day with the `m8t` CLI. Install the CLI per [`install/m8t-cli.md`](install/m8t-cli.md); the full flag-by-flag reference lives in `apps/cli/README.md`.

**Prerequisite:** `az login` to the tenant that holds your deployment — the CLI uses your active Azure session and discovers the gateway via Azure Resource Manager.

> ⚠️ **Two commands referenced below — `m8t deploy` and `m8t coder deploy` — need access
> to the m8t platform repository, which is not public.** They read deployment templates
> and agent definitions out of a checkout, and this repository is not that checkout. They
> refuse by name rather than failing confusingly. Everything else here works: team,
> bindings, status, health and updates need no checkout.

Joining a platform someone else installed, or seeing permission errors? Run `m8t prereqs` — it reports what your account is missing and `--fix` grants it. Full list: [`prerequisites.md`](prerequisites.md).

## Team management

Your team is who can reach the workers (and over which channels). Manage it with `m8t team`:

```bash
m8t team add idabest --display "Ilan Dabest" --telegram 88112233
m8t team list
```

## Channel bindings

A binding routes an external channel (e.g. a Telegram bot) to a worker. Create and manage bindings either in the web app's bindings UI or with `m8t bind` from the CLI. Re-binding does not require a redeploy. For the exact `m8t bind` flags, see `apps/cli/README.md`.

## Platform status & updates

```bash
m8t platform status                 # what's deployed + its versions/health
m8t platform status --verify        # also read the live gateway and compare it to the record
m8t platform update                 # roll the gateway to the newest published vX.Y.Z image
```

### What your gateway is pinned to

A managed install pins the gateway by **image digest**, not by tag. Tags can be moved:
if a published `v0.4.8` were ever re-pushed, a tag-pinned deployment could quietly start
running different code on its next restart, with no version change to show for it. A digest
names the exact image, so what you install is what keeps running.

You still read versions as tags — `v0.4.8` in the status table, the About pane and the update
check. The digest decides what runs; the tag is what it is called.

`m8t platform status --verify` reads the live deployment and compares it to the recorded one:

```text
live verify:
  stamp gateway:      v0.4.8 · sha256:2cd5a75a…
  live gateway:       sha256:2cd5a75a…
  match:              yes  (compared by digest)
```

An install created before this change is pinned by tag, and says so — `match` is still
reported, but by tag, which confirms the label rather than the code behind it. Updating the
platform moves it onto a digest.

`m8t platform update` tracks the public image repo and rolls to the newest semver tag. If you run your **own** image (fork / private registry), update instead by building a fresh tag and re-running the deploy — `m8t deploy --image-ref <youracr>.azurecr.io/m8t-web:<new-tag>` (reusing a tag is a no-op in single-revision mode). See `publish/self-build.md` and the "Re-running / updating" section of [`deploy.md`](deploy.md).

## Health & diagnostics

```bash
m8t doctor                   # baseline health + model-quota check
m8t doctor --agent <name>    # baseline + delivery-grant check for a specific worker
```

`m8t doctor` lists deployed model deployments and warns for any model with 0 quota in the region (the same check `m8t coder deploy` runs). `--agent <name>` additionally verifies that the named worker's managed identity holds `Key Vault Secrets User` on its configured delivery vault.

## Teardown

Tearing the platform down is tag-scoped (`m8t=<role>`) — it never deletes your resource group or your Foundry account. See [`uninstall/azure-infra.md`](uninstall/azure-infra.md). To remove a single worker, use `m8t coder teardown <name>` (see [`workers.md`](workers.md)).
