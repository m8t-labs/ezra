# Deploy workers — prompt agents & hosted coders

> 🤖 **Agent runbook.** Paste this into your coding agent — it executes the steps top-to-bottom and pauses only for sign-ins, `sudo`, or genuine choices. Idempotent — safe to re-run after a `git pull`.
>
> 💬 **Or just ask.** Deploy workers often? Render the optional `m8t-architect` skill into your coding agent once (open `install/m8t.md` and follow it), then just tell your agent *"spin up a CMO"*. This runbook is the explicit, source-of-truth version — it needs no installed skill.

**Prerequisites.** A deployed platform (see [`deploy.md`](deploy.md)) plus `az` and the `m8t` CLI from [`install.md`](install.md)'s prereqs step (its optional Azure MCP step helps here too). Worker deploys target the Foundry project your platform uses.

Worker deploys read the platform's Key Vault **as you**, so your own account needs access to it — being an Owner of the subscription is not enough. Run `m8t prereqs` to check, `m8t prereqs --fix` to grant it. See [`prerequisites.md`](prerequisites.md).

## How to read this file

You're an agent. Ask the user which worker they want, then run the matching section. Pause only for sign-ins, ambiguous choices (multiple Foundry projects/models), or failures. Every step is idempotent — re-running creates a new version, never a duplicate.

## Deploy a prompt agent (e.g. the CMO)

A prompt agent is a persona under `personas/` rendered into a Microsoft Agent Foundry agent. Two equivalent paths:

- **Just ask** — invoke the `m8t-architect` skill (*"spin up the CMO"*). It runs the field interview one question at a time, asks for a single confirmation, calls Foundry's `agent_update`, and returns a playground URL.
- **Explicit** — follow `<repo-root>/targets/foundry/README.md` steps 1–11 (locate the persona file, run the interview, compose the payload via auto-discovery, pre-flight, confirm, call, write the local metadata). See `targets/foundry/README.md`.

Brain-enabled personas (`targets.foundry.brain: true`) additionally run a brain link (see **Brain-enable a worker** below); a2a-enabled personas (`targets.foundry.a2a: true`) run `m8t a2a enable` **after** any brain link (see **A2A-enable a worker**).

## (Optional) Build + push your own coding-agent image — BYOC

> **You usually don't need this.** `m8t coder deploy` defaults to the **public** image `ghcr.io/m8t-labs/m8t-coding-agent` (pulled anonymously — no build, no registry, nothing to push). Skip to the **Deploy a hosted coder** section below unless you want to customize the image or keep it in your own private registry.

To bring your own image, build it for `linux/amd64` and push to **your own** ACR (or any registry). **ACR Tasks are blocked on some subscriptions** (`TasksOperationsNotAllowed`), so build locally with `--platform linux/amd64 --push`:

```bash
az acr login -n <youracr>
cd agents/coding-agent
TAG=v$(date +%Y%m%d)-$(git rev-parse --short HEAD)

docker buildx build \
  --platform linux/amd64 \
  -t <youracr>.azurecr.io/m8t-coding-agent:$TAG \
  --push .

echo "Pushed: <youracr>.azurecr.io/m8t-coding-agent:$TAG"
cd ../..
```

Prerequisites: `docker buildx` with amd64 cross-compile support; `az acr login -n <youracr>`. Use **unique tags only** — never `:latest`. Image size is ~682 MB. Full build + deploy reference (request/response, `m8t:artifacts` marker schema, mandatory RBAC): `agents/coding-agent/README.md`.

## Deploy a hosted coder

Deploy the coder as a named, discoverable worker. **By default it pulls the public image `ghcr.io/m8t-labs/m8t-coding-agent` — no build, no registry, nothing to push first.** (To use your own image, see the **(Optional) Build + push your own coding-agent image** section above and pass `--image`/`--image-tag`.)

```bash
m8t coder deploy <name>                                  # defaults: medium (1 vCPU/2 GiB), gpt-4.1-mini
m8t coder deploy <name> --size large --model-deployment gpt-4.1
m8t coder deploy <name> --env M8T_CODER_EXEC_TIMEOUT_SECONDS=300
```

| Flag | Default | Meaning |
|---|---|---|
| `--persona` | `coding-agent` | worker persona (renders the role/description on the surfaces) |
| `--image` / `--image-tag` | `ghcr.io/m8t-labs/m8t-coding-agent` / *(pinned `vX.Y.Z`)* | image ref — override for BYOC (a bare repo name resolves under `ghcr.io/m8t-labs`; a full `host/repo` ref is used as-is) |
| `--size` | `medium` | `small` 0.5/1Gi · `medium` 1/2Gi · `large` 2/4Gi |
| `--model-deployment` | `gpt-4.1-mini` | the Foundry model deployment the coder calls |
| `--env KEY=VALUE` | — | repeatable; passes `M8T_CODER_*` tuning to the container |
| `--endpoint` / `--subscription` | discovered / active | target project + subscription overrides |
| `--brain-kv <name\|uri>` | inferred from `AZURE_KEYVAULT_URI` | Key Vault used when granting `Key Vault Secrets User` for delivery |
| `--skip-quota-check` | — | bypass the pre-deploy quota check (else fails fast with `MODEL_NO_QUOTA` on 0 TPM) |
| `--allow-non-reasoning` | — | silence the reasoning-model warning when brain-linking off the known-good family |

**What it does:** checks preconditions (region supported, your role-assignment permission; **for a private ACR ref also the image tag + project-MI AcrPull — both skipped for a public ref like the default GHCR image, which needs no registry credentials**) → creates the hosted version with `metadata: { source, kind: "hosted", persona, personaVersion }` → **grants the per-version agent identity `Foundry User` at the Foundry account scope** (the mandatory step that, if skipped, surfaces as a misleading `storage_error`) → polls to `active`. Re-running creates a new version (idempotent).

**RBAC it relies on:** you (the operator) need Owner / User Access Administrator / RBAC Administrator on the Foundry account to grant the agent its role. A **private-ACR** image additionally needs the project managed identity to hold `AcrPull` (auto-granted if missing); the **public GHCR default** needs no such grant.

<details><summary>Manual fallback (raw SDK + az)</summary>

Create the version via the SDK, then `az role assignment create --assignee-object-id <agentOID> --assignee-principal-type ServicePrincipal --role 53ca6127-db72-4b80-b1b0-d745d6d5456d --scope <.../accounts/<account>>`. Documented in `agents/coding-agent/README.md`. Use only if the CLI is unavailable.

</details>

## Brain-enable a worker (GitHub second brain)

A worker can carry a GitHub second brain — a hosted coder bypasses the MCP attachment entirely (the container self-mints a short-lived GitHub-App installation token from Key Vault and reads/writes the brain repo over the GitHub HTTP API in-sandbox). Two equivalent paths:

```bash
# (a) deploy + brain-enable in one shot (defaults the model to a reasoning deployment):
m8t coder deploy <name> --brain <owner>/<repo>

# (b) brain-enable an already-deployed worker:
m8t brain link <name> --repo <owner>/<repo> --model-deployment gpt-5-mini
```

- **Requires a reasoning model.** `--brain` defaults the model to `gpt-5-mini`; `m8t brain link` errors unless the worker already runs a reasoning deployment (or you pass `--model-deployment gpt-5-mini`).
- **Create brains under `--owner m8t-labs`** — the `m8t-brain` GitHub App is installed all-repos only on that org; a personal-account repo polls the install forever.
- **Grants the agent identity `Key Vault Secrets User`** on the brain KV (allow 1–5 min for the grant to propagate before the first invoke).
- Re-running the link with the same repo is a true no-op (the container self-mints, so there is no connection token to rotate).
- `m8t brain link --persona <path>` overrides the persona file recorded in `~/.m8t/foundry/<agent>.yaml` (useful when the persona moved, or for REST/SDK-created agents).

## A2A-enable a worker (agent-to-agent delegation)

The A2A bridge route (`/api/a2a/mcp`) ships inside the gateway web image — no separate resource. Enable a worker as a caller/callee:

```bash
m8t a2a enable <agent> --persona <persona-name> --gateway-url https://<gateway-fqdn>
```

- Pass the gateway **base URL** (`https://<gateway-fqdn>`) — the bridge path `/api/a2a/mcp` is appended automatically. It also resolves from `M8T_GATEWAY_URL` or the `gatewayUrl` key in `~/.m8t/config.yaml`.
- Idempotent — re-running rotates the bearer. Reverse with `m8t a2a disable <agent>`.
- **For a brain + a2a worker, run `m8t a2a enable` AFTER `m8t brain link`** — a brain link re-renders instructions and would drop the a2a tool snippet if run after.

The gateway-side bridge configuration (env vars, per-caller project connection, cache TTL) is platform-side — see the "A2A bridge" section of `deploy/README.md`.

**Flagship demo (Stacey → Coder).** Neither is part of the default install — a from-zero install deploys Ezra alone; both are deployed by hand below, which is how canary runs them. A brain-enabled advisor that delegates execution to the coder is the full A2A story. Deploy order: (1) deploy the advisor on a reasoning model + `reasoning.effort: low`; (2) `m8t brain create <advisor> --owner m8t-labs --seed <seed> --kv-uri <kv>`; (3) `m8t a2a enable <advisor>` LAST; (4) deploy the coder with delivery creds (`--env GITHUB_APP_INSTALLATION_ID=… --env AZURE_KEYVAULT_URI=…`) and grant its MI `Key Vault Secrets User` on the brain KV; (5) `m8t a2a enable <coder>`. Then on the web app: ask the advisor for a data task → she `invoke_worker`s the coder → the coder writes an artifact into her brain and returns a pointer → she reads it back and answers. Every hop shows in the Agent Ledger, grouped by `delegationId`.

## Verify a deployed worker

```bash
m8t doctor --agent <name>
```

`--agent <name>` adds a targeted delivery-grant check (reads the agent's deployed env vars and verifies its managed identity holds `Key Vault Secrets User` on the configured vault). The baseline `m8t doctor` also runs a model-quota check across deployed model deployments.

## Teardown a worker

```bash
m8t coder teardown <name>      # deletes the agent + its container + identity + role assignment
```

For the full per-worker teardown and the surrounding cloud cleanup, see [`uninstall/azure-infra.md`](uninstall/azure-infra.md) step 3d.

## Hosted-agent images and updates

Hosted agents (`coder`, `ezra-executor`) run on Foundry's managed compute, which
pulls the container image by authenticating with the project's managed identity.
Projects created after 2026-06-25 do not allow anonymous pulls, so m8t images
cannot be pulled directly from public GHCR.

The CLI handles this for you:

- **`m8t foundry create`** provisions a small Basic Azure Container Registry in your
  resource group and grants the project managed identity `AcrPull`.
- **`m8t coder deploy` / `m8t azure-exec deploy`** copy the requested public image
  (default `ghcr.io/m8t-labs/<agent>:<tag>`) into that ACR with a server-side
  `az acr import` (no local build), then deploy the agent from the ACR ref. If the
  ACR is missing (e.g. a project created before this feature), it is created on the
  fly.

**Updating an image:** re-run the deploy command with a newer `--image-tag`. The new
tag is imported and a new immutable agent version is rolled out. There is no separate
update command. Pin explicit version tags (never `latest`) for reproducible rollouts.

**Bring your own registry:** pass `--image <name>.azurecr.io/<repo>` to deploy from an
existing private ACR; the CLI skips staging and only ensures the `AcrPull` grant.

## Re-running / updating

Every step is idempotent: re-deploying a worker creates a new version; `m8t brain link` with the same repo is a no-op; `m8t a2a enable` rotates the bearer. Safe to re-run after a `git pull`.
