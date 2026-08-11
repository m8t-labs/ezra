# `install/companion.md` — the desktop companions

> 🤖 **Agent runbook (component step).** Your coding agent opens this from the install flow and runs it top-to-bottom. Idempotent — safe to re-run.
>
> **Goal:** your mates sit at the edge of the screen, ready to take a message. Most people never open this file: `m8t bootstrap status --watch` installs them as part of getting the platform live. Come here to check on them, update them, repair them, or remove them.

## What they are

Two small always-on-top windows — one per mate — that rest against a screen
edge and peek until you hover them or tab into them. Each has a one-message
composer. Sending hands the message to that mate's conversation and opens it in
your default browser, which stays the only place a conversation is read.

They are not another chat app. They are the shortest path from "I should ask
Ezra about this" to having asked.

## Requirements

- **macOS or Windows**, arm64 or x64. There is no Linux build; onboarding says so
  and skips them rather than installing something that cannot run.
- **The `m8t` CLI** — see [`m8t-cli.md`](m8t-cli.md). It is what installs them
  and what they talk to; they reach nothing on their own.
- **A live platform**, and `az login` — the companions read who is on your
  desktop as you.

## They are their own software

The companions carry their own version and are released on their own. A
platform release names the companion build it carries, the same way it names a
gateway image, and `m8t companion install` takes it from there — the CLI
carries no part of the build. A newer companion arrives when you move to a
platform release that carries one, without touching your CLI, and a newer CLI
does not silently change the companion on your desktop.

What stands behind a build today is the digest, not a signature: the release
names one per target, and `install` checks the archive against it before
unpacking and then checks every file it wrote. The builds are not yet signed or
notarized, which nothing on either platform stops — the CLI fetches the archive
itself, so macOS never marks it quarantined and Windows never marks it from the
web.

## Installing them

`m8t bootstrap status --watch` already does this as part of getting the platform
live, on macOS and Windows alike. Nothing else is needed and there is nothing to
download by hand.

The build is about 120 MB, so allow several minutes on a slow link. An
interrupted download picks up where it stopped rather than starting over.

To put them on a machine on their own — a second workstation, or one where you
skipped them earlier:

```bash
m8t companion install
```

That is the whole thing. It takes the build the release channel names for your
machine, checks it, installs it, registers it to start at login, and launches
it. Your mates are against the edge of the screen when it returns.

## Commands

```bash
m8t companion status      # installed? which version? is a newer one out?
m8t companion install     # take the released build, register for login, launch
m8t companion repair      # reinstall over whatever is there now
m8t companion uninstall   # remove the app, the login item, and the records
```

`install` and `repair` fetch the build the release channel names for your
machine, check the download against the digest the release pinned for it
before unpacking anything, and then check every file of what they wrote
against the build's own manifest. "Installed" means the app on disk is the app
that was published.

`install` is idempotent: against a matching, verified install it does nothing.
`repair` always converges — reach for it when `status` reports anything other
than installed.

Where things land:

| | macOS | Windows |
|---|---|---|
| The app | `~/Applications/m8t Companion.app` | `%LOCALAPPDATA%\m8t\companion\app` |
| Start at login | `~/Library/LaunchAgents/com.m8t.companion.plist` | the `HKCU` `Run` key |
| Records | `~/.m8t/companion/` | `~/.m8t/companion/` |

`uninstall` removes all three, and only those — it refuses to remove a target
it did not install.

## Updating

`m8t companion status` says whether a newer companion has been released. The
companion itself says so too: it asks the CLI on your behalf, and Settings
shows **An update is available** with the version. Taking it is one command:

```bash
m8t companion install
```

Nothing updates itself and nothing downloads in the background. If a release is
marked critical, the companion says **An update is required** instead — same
command either way.

## When they say "Reconnecting…"

Greyed-out heads mean the roster read did not come back. The companions reach
your platform only by running the `m8t` CLI, so there are four things to check,
in order — the same four the Settings window offers under **Repair connection**:

```bash
m8t version               # not found? npm install -g @m8t-stack/cli
az login                  # an expired sign-in stops the roster read
m8t whoami                # names the platform this machine is pointed at
m8t companion repair      # if all three are fine, rebind
```

## Building them from a clone

Contributors working on the companions run what they just compiled rather than
what was released. From the repo root:

```bash
pnpm --filter @m8t-stack/companion pack:mac    # or pack:win
m8t companion install --from apps/companion/dist-artifacts/darwin-arm64
```

The pack builds both architectures of your OS and stages each one as a payload
plus an `artifact-v1.json` describing every file in it. `--from` installs a
staged directory instead of the released build; everything after that point is
identical, verification included. The whole sequence is also one command:

```bash
node scripts/install-companion-from-source.mjs
```

A build from a clone covers one machine — yours. Putting a companion on
somebody else's is a release, which builds each target on its own operating
system and publishes it with a digest per target.

## Verification

```bash
m8t companion status
```

End state: `installed`, a version, and start-at-login on. Your mates are
against a screen edge; hovering one brings it fully into view.
