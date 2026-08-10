# Bootstrap — one paste, walk away, a live m8t platform

> 🤖 **Agent runbook.** Paste this into your coding agent. It installs the bare local prereqs, does ONE Azure sign-in, hard-stops if you lack admin rights, then offloads the whole install to an ephemeral cloud installer and watches it to completion. Re-runnable — see "Re-running" below.

## What this does (and what runs where)

- **Local (only `git` + `az` + the `m8t` CLI):** clone the repo, one `az login`, a loud admin-credentials preflight, create + authorize a managed identity, kick the cloud installer, watch its status, tear it down, and point your tools at the live platform.
- **Cloud (in YOUR subscription, ephemeral, self-cleaning):** the installer creates Foundry from zero, deploys the gateway + infra, and self-deletes. The platform persists; the installer leaves no residue.

## The one consent burst (front-loaded — then walk away)

You will be asked to authenticate **once**:

1. **`az login`** — sign in as a subscription **Owner or User Access Administrator** who is **also a directory admin** (or bring a ready app registration via `--client-id`).

> **Your workers need a one-time GitHub App approval** (manifest flow, ~1 click; the App is granted access to **all** your repositories by default, so future brains need no re-approval — power users can narrow it to selected repositories later). See step 3b below.

Everything else — the app registration, the installer's identity and its roles, the installer itself — happens automatically under that one sign-in. No further sign-ins, and nothing else to approve.

Step 4b asks you two short questions — the address to reach you on, and your Microsoft startup advisor if you have one — while the install runs in the background. Neither holds the install up, and both can be answered or corrected later.

## Steps

You're an agent. Walk these in order. Pause only for `az login`, `sudo`, or a genuine choice.

### 0. Tell the user what this costs, then STOP and wait

Before anything else, say this to the user in your own words — but cover every point:

> You are about to install the m8t platform.
>
> - It installs into **your** Azure subscription and **your** GitHub account or organization.
> - The Azure resources it creates **bill to your Azure account — this uses your budget**.
> - With your workers installed, you can ask Ezra what you're spending at any time, and you can turn on a cost report by email every two weeks.
> - You can remove it later — see `guides/uninstall.md`.
>
> **Continue?**

Then **wait for their answer**. Do not take any install or cloud action until the user has
answered — this includes installing prerequisites and running `az login`. **This is a stop, not a
notification.** If they decline, stop here and do nothing else.

> Arrived here from `install.md`? Its Step 0 already asked — do not ask twice.

### 1. Prereqs (git + az + the m8t CLI)

Detect the OS and follow the matching prereqs file for `az`:

- macOS → `install/prereqs-macos.md`
- Windows → `install/prereqs-windows.md`

End state: `az --version` works and `az account show` returns the subscription you want to install into. Ensure the repo checkout is a **full clone** (never shallow — a shallow/grafted clone silently breaks `git pull`): `git rev-parse --is-shallow-repository` must print `false`.

Then install the `m8t` CLI — see [`install/m8t-cli.md`](install/m8t-cli.md) (npm is the default; brew/scoop and a contributor fallback are documented there). Verify with `m8t version`.

> Arrived here from `install.md`? Its prereqs step already did all of this — the checks above will confirm-and-continue in seconds, nothing to redo.

### 2. One `az login`

If `az account show` doesn't already show the right subscription + tenant, sign in:

```bash
az login                                  # add --use-device-code on a headless box
az account set --subscription <sub-id>
```

### 3. Preflight (LOUD hard-stop)

```bash
m8t bootstrap preflight --location <region>   # or add: --client-id <appId>
```

This prints an unmissable notice and **stops** unless you are Owner/UAA at subscription scope **and** can register the app (or passed `--client-id`). **Do not proceed past a hard-stop** — surface the exact message to the user; they need an admin or a `--client-id`.

It then checks the subscription itself, before anything is created: every Azure **resource provider** the
install uses (registering any that are missing), any **soft-deleted Cognitive Services account** — one that
was deleted but not purged keeps its model quota, so quota can read free and the model deployment still
fail — and, when you pass `--location`, **model quota** in that region. Each stops the install only on a
definite, observed blocker, and each refusal names the exact command that fixes it. An unverifiable check
warns and proceeds rather than blocking you on a network blip.

Pass `--location` with the region you intend to install into: without it, quota is not verified and a
quota-less region is only discovered mid-install, after the spend has started.

The same checks are available on their own as `m8t prereqs`. What is and is not covered:
[`prerequisites.md`](prerequisites.md).

### 3b. Create + install the GitHub App for your workers' brains

Your workers keep their working memory in private GitHub repositories — their "brains". A GitHub
App creates and writes to those repos. This step creates the App and installs it, and it is part of
the platform: the install needs it.

**Prereq — GitHub CLI, signed in.** The org lookup below shells out to `gh`. Check it's there and signed in first:

```bash
gh --version
```

- Not found → install it: `winget install --exact --id GitHub.cli --accept-package-agreements --accept-source-agreements` (Windows) or `brew install gh` (macOS). Then re-run this check.
- Found → confirm it's authenticated:

```bash
gh auth status
```

- Not signed in → run `gh auth login` and follow its prompts. This is a browser/interactive flow — **pause and tell the user**, same as `az login`.
- Signed in → continue.

**Pick the org the brains live in:**

```bash
m8t brain orgs
```

This is read-only. Act on what it prints:

| It says | You do |
|---|---|
| `Using your GitHub Enterprise org <name>` | Use that org. Tell the user which one, don't ask — a GitHub Enterprise org is the right home for company repos. |
| `You belong to more than one GitHub Enterprise org` | **Ask the user which one**, and use their answer. |
| `No GitHub Enterprise org detected…` | Relay that one sentence, then continue with the org it names. If they have more than one org, **ask which**. |
| `Could not check your GitHub orgs automatically` | Fall back: run `gh api user/memberships/orgs --jq '.[].organization.login'`, and if there's more than one, **ask the user which**. |
| It exits non-zero with a refusal about having no organization | **Stop and relay it.** Brain repos are created through a GitHub App, which needs an org. The user creates a free GitHub organization, then you re-run this step. |

Substitute the chosen org for `<org>` below.

**Now tell the user what's about to happen, then STOP and wait.**

Say this in your own words, and cover both points:

> Next I'll set up the GitHub App that creates your workers' brains — private repositories where
> they keep their working memory, in `<org>`. A browser window will open for you to approve it; it
> takes about a click.
>
> **Ready?**

Then **wait for their answer**. Do not run the command below until they've replied. **This is a stop, not a notification** — the browser window is about to take over their screen, and it should not be a surprise.

Run the manifest flow (this opens your browser to GitHub's pre-filled Create GitHub App page):

```bash
m8t brain app-create --org <org>
```

Your browser opens to a single page that walks you through it, all in one tab:

1. **Create GitHub App** — click the green button on GitHub's pre-filled form (no typing).
2. **Install** — click **Install on `<org>`**, leave the default "All repositories", and confirm.

After you confirm on GitHub, GitHub redirects you back to an "Installed — return to your terminal" page, so you always know when it's done.

> GitHub may ask you to confirm your identity once or twice — a sign-in plus a security re-check for creating an org app. That's expected, not an error.

`m8t brain app-create` waits for the installation to complete (polls for up to 5 minutes), then writes:

- `~/.m8t/github-app-<org>-<appId>.pem` — that App's private key (mode 0600)
- `~/.m8t/github-app-<org>-<appId>.json` — that App's own credentials (appId, slug, org, installationId, pemPath)
- `~/.m8t/github-app.json` — the **active** App: the one `m8t bootstrap launch` will use

`m8t bootstrap launch` reads the active App automatically in the next step — no extra flags needed.

`~/.m8t/github-app.json` is a pointer, and `m8t brain app-create` overwrites it by design — the App it
just created becomes the active one. The per-App files beside it are never overwritten, so creating an
App for a second org leaves the first org's key exactly where it was.

**To make an App you already created the active one again:**

1. See what you have: `ls ~/.m8t/github-app-*.json`
2. Copy that App's file over the pointer: `cp ~/.m8t/github-app-<org>-<appId>.json ~/.m8t/github-app.json`

No re-create needed. `m8t bootstrap launch --org <org>` checks the org against the credentials on disk
and stops if they disagree, so a wrong pointer is caught before anything is installed.

### 4. Launch the cloud installer

```bash
m8t bootstrap launch --location <region> --org <org>  # add --client-id <appId> if you used it in preflight
```

This creates + authorizes the installer managed identity, picks up the GitHub App creds from `~/.m8t/github-app.json` (if present), and kicks the installer. (No prompts.)

`--org` is the org you chose in step 3b. It is checked against the credentials on disk and stops the
install if they disagree, so a leftover App from an earlier run can't quietly send the brains
somewhere else.

#### Re-running

The install is safe to re-run against an **empty** target — the steps converge and nothing is
duplicated. If the target resource group already holds resources — a partial install from an earlier
attempt, or an existing deployment — `m8t bootstrap launch` **stops** instead of writing over them,
and prints what it found. **This is a stop, not a notification** — surface exactly what it found to
the user and wait for their explicit go-ahead before you re-run with the consent flag below; never
pass it on your own judgment.

If the occupant is your own earlier attempt — the most likely case — the cleanest fix is usually to
clean it up first: `m8t bootstrap reap --force` tears down the orphaned installer identity (and its
Owner-at-subscription-scope grant) that a partial launch leaves behind. Picking an empty resource
group instead, without reaping first, leaves that privileged identity behind.

To deliberately continue into the occupied group anyway, re-run with the `--resource-group` and
`--reinstall-into` flags the message prints, naming the same group in both — only after the user has
said to:

```bash
m8t bootstrap launch --location <region> --resource-group <rg-name> --reinstall-into <rg-name>
```

`--reinstall-into` **authorizes** the target; it does not choose it — `--resource-group` does that,
and the two names must match. Requiring it here is deliberate: blind re-entry into a partial install
is its own class of bug.

### 4b. Your details

Two questions, while the install runs in the background. Ask the user both — in your own
words, but ask for exactly these two things — and pass their answers:

1. **The email address to reach them on.** Ezra sends them their copies of its outbound
   mail there — when it emails their startup advisor on their behalf, that address is
   copied in and is where replies go. Their Azure sign-in is offered as the default; have
   them confirm it rather than assuming, because a guest account's sign-in address is
   often not the address they actually use.
2. **Their Microsoft startup advisor's name and email, if they have one.** This is who
   Ezra can email for quota and credit requests, and only when asked to. It is genuinely
   optional — "I don't know" is a normal answer, and they can tell Ezra later.

```bash
m8t bootstrap profile --founder-email you@example.com --advisor-name "Their Advisor" --advisor-email advisor@example.com
```

If they don't have an advisor to hand, drop both advisor flags and pass `--no-advisor`
instead. Running it in a terminal yourself, with no flags, asks you both questions directly;
run this way, from an agent, it needs the flags and will say so rather than hanging.

**It is safe to re-run at any time**, including after the install finishes if a detail was
wrong. An answer you don't re-supply is left as it was; `--no-advisor` is the way to remove
an advisor you recorded earlier.

The command may also offer a hosted Ezra to talk to while the wait runs. When it is
available it prints a link and opens it; when it isn't, it says so in one line and carries
on. Relay whichever happened — don't promise a browser tab before you've seen the line. That
Ezra is ours, not theirs: it cannot see their subscription or this install, so it is not a
way to check progress. Theirs arrives with the install and `m8t open` reaches it. Add
`--print` on a machine with no browser, or `--no-chat` to skip the offer entirely.

**Nothing in this step blocks or fails the install.**

#### Which model the intake advisor ran on

<!-- CLI-rewrite: this whole subsection documents the retired intake advisor. It is kept
     only because the table is generated from the CLI and held in lockstep by a check
     there. Remove the section and its check together. -->

The intake advisor this describes has been **retired** — nothing runs this cascade today,
and step 4b above replaced it. The table is kept, generated from the CLI, until the CLI
rewrite removes it.

It ran on the best model the subscription could actually deploy. At startup
the CLI walked an ordered preference list, top to bottom, and stopped at the first model
it could deploy in the region.

<!-- BEGIN:model-cascade-table -->
| # | Model | Family | Capacity |
|---|---|---|---|
| 1 | `gpt-5.6-luna` | OpenAI | 100 |
| 2 | `gpt-5.6-sol` | OpenAI | 100 |
| 3 | `gpt-5.6-terra` | OpenAI | 100 |
| 4 | `gpt-5.4` | OpenAI | 100 |
| 5 | `grok-4.3` | xAI | 100 |
| 6 | `gpt-4.1-mini` | OpenAI | 50 |
<!-- END:model-cascade-table -->

A model was eligible only if all of the following held in the region:

- it appeared in the region's Foundry model catalog;
- it was agent-eligible there (Microsoft's `agentsV2` capability);
- it offered the Global Standard deployment type;
- the subscription did not have an explicit zero quota for it.

Models 1-3 are the same generation and Microsoft publishes no ranking between them,
so their order here is arbitrary - landing on any of the three was the same outcome.

If none of the list could be deployed - or if the check could not run, for example when
the account lacked permission to create deployments - the advisor fell back to the
model named in its own configuration, and said it could not check rather than
guess why.

A table row was never a promise: what a subscription can deploy depends on its
quota, which varies by subscription and region.

### 5. Watch it to done — this also finishes your local setup

Watch the cloud install progress:

```bash
m8t bootstrap status --watch --repo-root "$(pwd)"
```

Show the user the live phase trace. The full install is unattended (~minutes). It ends at `done` (or `failed` with a clear error).

When it reaches `done`, this same command completes the half of the install that can only happen on your machine — it is not a separate step you run afterwards:

1. **authorizes sign-in to your webapp** (registers the gateway's redirect URI). Nothing else in the install can do this: the cloud installer runs as a managed identity with no directory rights, and when it started, the gateway's address did not exist yet. Without it the platform serves fine and then refuses every sign-in with `AADSTS50011`.
2. writes the repo-root marker and points your local tools at the gateway;
3. **tells your advisors how to reach you** — the details you confirmed in step 4b go into your brain-backed advisor's memory, so it knows the address to copy you on and who it may escalate to. Two cases: you ran step 4b → it lands here; you skipped it → it says so and names the command, and you can run `m8t bootstrap profile` any time afterwards.
4. **puts your mates on your desktop** — a small always-on-top window per mate at the edge of the screen, each with a one-message composer. They are their own software with their own version; this fetches the build your platform release names and verifies it before installing. It runs last and announces itself first, because it is the one step that downloads ~120 MB — on a slow link, minutes with nothing else to show. Four ways it can end, and it **says which of these happened**, every time it runs: installed; the release you are on carries no companions; this host has no build (there is no Linux one); or it needs `m8t companion repair`. The platform is live and unaffected in all four. (It does not run at all if step 2 could not point your tools at the gateway — the companions need one to talk to, and that failure is reported above it.) See [`install/companion.md`](install/companion.md).
5. prints the optional local-tooling pointers + fresh-session guidance.

Each is best-effort — none blocks the others, and the platform is already live. You can (re-)run the seed manually any time with `m8t bootstrap seed-profile` (idempotent — an unchanged profile is a no-op), and redo the whole local setup with `m8t bootstrap status --finalize`.

> **Your own access to the platform is granted by the installer**, early in the install, so a partial install still leaves you able to sign in and diagnose it. If it could not grant you (you are not the subscription's administrator, say), run `m8t prereqs --fix` — the install tells you so rather than failing silently.
>
> **More than one m8t deployment in your subscription?** (Reinstall, shared sub, prod+test.) `status` auto-targets the install it just did. Other gateway commands (`m8t whoami`, etc.) take `--resource-group <rg>` to pick one; the error from an ambiguous run lists each gateway's resource group.

### 6. Reap the installer scaffolding

```bash
m8t bootstrap reap   # tears down the installer's identity + container (the platform stays)
```

Optionally, add local tooling to your host: [`install/m8t-plugin.md`](install/m8t-plugin.md) to talk to deployed workers from your agent sessions, and — only if you want the opt-in persona skills (see [`workers.md`](workers.md)) — [`install/m8t.md`](install/m8t.md). Neither gates your platform; skip both freely.

When step 5 prints its summary, **relay it to the user and expand it conversationally**: their live platform URL (or `m8t open`), the agents that were installed and their brains, and how to reach them — `@ezra` (or `/ezra`) in the coding agent, the webapp, or by connecting Telegram in the webapp's Channels. Then remind them to open a brand-new chat/session so the new skills + MCP load.

## Done

Relay the summary from step 5 as described above, then tell the user:

> **✅ Your m8t platform is live.** Open a brand new chat/session (new skills + MCP load only on fresh start), then talk to your platform. Deploy more workers with `m8t coder deploy <name>` or the worker runbook ([`workers.md`](workers.md)).

Then relay **the companion line the install printed** — do not assert it yourself, because only the install knows how that step ended (step 5.4 lists the four ways):

- *"Desktop companions installed"* → tell them their mates are on their desktop, and to hover one to bring it into view and send it a message.
- *"carries no desktop companions"* / *"not built for"* → tell them there are no desktop companions on this release or this host, and that everything else is unaffected.
- *"need repair"* → relay it with the `m8t companion repair` command.

If there is no companion line at all — the install was interrupted mid-step, or it never reached the step because the gateway could not be resolved — say so and offer `m8t companion install`. Do not report an outcome nobody observed.

## Re-running

`m8t bootstrap status` and `reap` are idempotent — safe to re-run any time; `status` just resumes
watching whatever install is already in progress, and re-does the local setup harmlessly when it is
already done. `launch` is the exception: see "Re-running" under Step 4 above — it converges cleanly
against an empty target, but refuses to write into a resource group that already holds resources
unless you pass `--reinstall-into`.

> `m8t bootstrap finish` is **deprecated**. It still works — it prints a notice and does exactly what
> `m8t bootstrap status --finalize` does — but there is no longer a separate finishing step to run.
