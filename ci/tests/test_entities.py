"""The named-entity rule, tested with INVENTED names.

Every fixture here is made up. A real entry in a test file would publish it in plain text —
the exact failure the digest storage exists to prevent — so the rule takes its digest set
as an argument and these tests pass their own.
"""
from __future__ import annotations

import re

from ci.rules.entities import DIGESTS, MAX_NGRAM, digest, find_named_entity

# Invented. Any resemblance to a real company is accidental and harmless: these digests are
# computed here, not shipped.
FAKE = frozenset({
    digest("Quibbleforth"),
    digest("nimbus-widget-console"),
    digest("Fenwick Sprocket Analytics Portal"),
})


def test_a_single_word_entry_is_found():
    assert find_named_entity("we did this for Quibbleforth last year", FAKE) is not None


def test_a_hyphenated_entry_is_found():
    assert find_named_entity("check nimbus-widget-console for the row", FAKE) is not None


def test_a_multi_word_entry_is_found():
    assert find_named_entity("per the Fenwick Sprocket Analytics Portal", FAKE) is not None


def test_matching_is_case_insensitive():
    assert find_named_entity("QUIBBLEFORTH and quibbleforth", FAKE) is not None


def test_surrounding_punctuation_does_not_hide_an_entry():
    assert find_named_entity("(Quibbleforth), and others.", FAKE) is not None


def test_unrelated_prose_is_clean():
    assert find_named_entity("Azure quota increases go through the portal.", FAKE) is None


def test_a_word_that_merely_contains_an_entry_is_not_a_match():
    """Tokenised matching, not substring: `quibbleforthright` is a different word."""
    assert find_named_entity("the quibbleforthright approach", FAKE) is None


def test_the_reported_position_points_at_the_entry():
    text = "some prose here, then Quibbleforth appears"
    assert text[find_named_entity(text, FAKE):].startswith("Quibbleforth")


def test_the_rule_returns_a_position_and_never_the_match():
    """The finding must not echo the entry back — CI repeating it would republish it."""
    assert isinstance(find_named_entity("about Quibbleforth", FAKE), int)


# ── the shipped list ───────────────────────────────────────────────────────────
def test_the_shipped_list_is_populated_and_well_formed():
    """Guards against an empty or malformed DIGESTS silently disabling the rule."""
    assert len(DIGESTS) >= 5
    assert all(re.fullmatch(r"[0-9a-f]{64}", d) for d in DIGESTS)


def test_the_shipped_list_carries_no_readable_text():
    """The point of the storage: nothing in it can be read as a name."""
    assert all(not re.search(r"[g-z]", d) for d in DIGESTS)


def test_digest_normalisation_matches_what_the_scanner_produces():
    """If `digest()` and the scanner's tokenisation disagree, an entry can be stored in a
    shape no document can ever produce — a rule that is green by construction."""
    assert find_named_entity("Nimbus-Widget-Console", frozenset({digest("nimbus widget console")})) is None
    assert find_named_entity("nimbus-widget-console", frozenset({digest("  NIMBUS-widget-console  ")})) is not None


def test_the_ngram_ceiling_covers_the_longest_shipped_entry():
    """MAX_NGRAM below the longest entry means that entry can never match."""
    assert MAX_NGRAM >= 4
