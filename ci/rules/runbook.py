"""The install runbook's dangerous step.

`guides/bootstrap.md` is walked by a coding agent with the founder's cloud credentials, and
one step in it opens a browser to create a GitHub App. Three claims about that step are
load-bearing, and each has been broken at least once by an edit that read as an
improvement:

* **the org is chosen deliberately** — by asking the CLI, not by an agent guessing from a
  raw membership listing;
* **the founder is stopped BEFORE the browser opens** — after it, a pause is not a pause,
  it is a caption on a window that already took the screen;
* **no skip path is offered that does not work** — the from-zero install requires a GitHub
  App, so a founder who took either "skip" used to reach a cloud abort that published
  nothing readable.

This rule came from the platform repository, where the runbook used to live. It moved here
with its subject: a guard that cannot see the file it guards is not a guard. It has a known
expiry — it dies with the paste-runbook when the one-click install lands.

Not fork-gated. These claims are about whether the install works, which is as true in a
copy as it is here.
"""
from __future__ import annotations

import re
from pathlib import Path

from .contracts import Finding

RUNBOOK = "guides/bootstrap.md"

STEP_START = "### 3b."
STEP_END = "### 4."

ORG_COMMAND = "m8t brain orgs"
RAW_LISTING = "gh api user/memberships/orgs --jq"
FALLBACK_VERDICT = "Could not check your GitHub orgs automatically"
BROWSER_COMMAND = "m8t brain app-create --org"
STOP_PHRASE = "This is a stop, not a notification"
LAUNCH_COMMAND = "m8t bootstrap launch --location <region> --org <org>"

NON_WORKING_SKIPS = (
    re.compile(r"skip (that|this) step if you do not want brain-backed workers", re.I),
    re.compile(r"basic platform without brain-backed workers", re.I),
    re.compile(r"personal GitHub account[\s\S]{0,120}?skip this step", re.I),
)


def check_runbook(root: Path) -> list[Finding]:
    guides = root / "guides"
    if not guides.is_dir():
        # A copy that carries no runbook has nothing to guard. Absence of the FOLDER is a
        # deliberate shape; absence of the FILE inside it is not — see below.
        return []

    path = root / RUNBOOK
    if not path.is_file():
        return [Finding(
            "runbook.missing",
            f"{RUNBOOK} is required — the install runbook's GitHub App step is guarded here, "
            "and a guard whose subject vanished reports health it never checked",
            RUNBOOK)]

    text = path.read_text(encoding="utf-8", errors="replace")
    f: list[Finding] = []

    start = text.find(STEP_START)
    end = text.find(STEP_END)
    if start == -1 or end == -1 or end < start:
        return [Finding("runbook.step_missing",
                        f"could not locate the GitHub App step ({STEP_START} .. {STEP_END})",
                        RUNBOOK)]
    step = text[start:end]

    def line_of(offset_in_step: int) -> int:
        return text.count("\n", 0, start + offset_in_step) + 1

    # ── the org is chosen deliberately ─────────────────────────────────────────
    if ORG_COMMAND not in step:
        f.append(Finding("runbook.org.undeliberate",
                         f"the GitHub App step must select the org with `{ORG_COMMAND}`",
                         RUNBOOK, line_of(0)))

    raw_at = step.find(RAW_LISTING)
    if raw_at != -1:
        # Checking merely that the raw listing comes AFTER the CLI command is too weak:
        # the command could stay put while its row is softened from "Fall back: run ..."
        # into a co-equal "Prefer to check manually? Run ...", reintroducing the ambiguity
        # this exists to prevent. So it is pinned to the fallback row AND the row must
        # still mark it as subordinate.
        verdict_at = step.find(FALLBACK_VERDICT)
        if verdict_at == -1:
            row = ""
        else:
            row_start = step.rfind("\n", 0, verdict_at) + 1
            row_end = step.find("\n", verdict_at)
            row = step[row_start:row_end if row_end != -1 else len(step)]
        if not (RAW_LISTING in row and re.search(r"\bfall back\b", row, re.I)):
            f.append(Finding(
                "runbook.org.raw_listing_promoted",
                f"the raw membership listing must stay the labeled fallback in the "
                f"`{FALLBACK_VERDICT}` row, not moved elsewhere or reworded into a co-equal option",
                RUNBOOK, line_of(raw_at)))

    if LAUNCH_COMMAND not in text:
        f.append(Finding("runbook.org.not_passed_to_launch",
                         "the launch step must pass the org chosen in the GitHub App step",
                         RUNBOOK))

    # ── the founder is stopped before the browser opens ────────────────────────
    browser_at = step.find(BROWSER_COMMAND)
    stop_at = step.find(STOP_PHRASE)
    if stop_at == -1:
        f.append(Finding("runbook.stop.missing",
                         "the GitHub App step must stop and wait for the founder",
                         RUNBOOK, line_of(0)))
    elif browser_at == -1:
        f.append(Finding("runbook.stop.no_browser_command",
                         f"the GitHub App step must run `{BROWSER_COMMAND}`",
                         RUNBOOK, line_of(0)))
    elif stop_at > browser_at:
        f.append(Finding("runbook.stop.after_browser",
                         "the stop must come BEFORE the command that opens the browser",
                         RUNBOOK, line_of(stop_at)))

    # The message promises the explanation precedes the browser, so the order is what is
    # enforced — not merely that the phrase appears somewhere the command could precede.
    memory_at = step.lower().find("working memory")
    if memory_at == -1 or (browser_at != -1 and memory_at > browser_at):
        f.append(Finding("runbook.stop.unexplained",
                         "the step must say what the brains are before opening a browser",
                         RUNBOOK, line_of(max(memory_at, 0))))

    # ── no skip path that does not work ────────────────────────────────────────
    for pattern in NON_WORKING_SKIPS:
        m = pattern.search(text)
        if m:
            f.append(Finding("runbook.skip.not_a_working_path",
                             "this skip is not a working path and must not be offered — the "
                             "from-zero install requires a GitHub App",
                             RUNBOOK, text.count("\n", 0, m.start()) + 1))

    return f
