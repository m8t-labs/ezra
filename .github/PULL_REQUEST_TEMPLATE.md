<!--
Thanks for improving Ezra. Nothing below is mandatory — it is what a reviewer will be
looking for, written down so you don't have to guess.
-->

## What changes, and why

<!-- What will Ezra do differently? If it's a fix, what was wrong? -->

## How you know it's right

<!-- A Microsoft Learn link, a portal behaviour you observed, an outcome you saw. -->

---

Before requesting review, `python -m pytest ci/tests` and `python ci/check.py` both pass
locally. CI runs those two, in that order:

- [ ] A new skill has its frontmatter, its three sections, and a line in both
      `skills/_index.md` and the persona's routing table
- [ ] Internal references resolve — backticked paths count, not just Markdown links
- [ ] No real email addresses, GUIDs, tokens, or anything from a real support case
- [ ] A deliberate change to Ezra's Voice also updates `ci/golden/voice.md`
