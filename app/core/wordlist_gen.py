"""CUPP-style personal wordlist generator (own implementation).

Combines a few user-supplied words/years into likely password candidates
using common human password patterns: casing, leetspeak, concatenation,
reversal, and common suffixes. Purely a string generator — no network
access, no persistence of the input elsewhere in the app.
"""

from __future__ import annotations

_LEET_MAP = str.maketrans({"a": "4", "e": "3", "i": "1", "o": "0", "s": "5"})
_SUFFIXES = ["", "!", "123", "@", "#", "01", "1"]
_MAX_DEFAULT = 1000


def _case_variants(word: str) -> set[str]:
    word = word.strip()
    if not word:
        return set()
    return {word, word.lower(), word.upper(), word.capitalize()}


def generate_personal_wordlist(words: list[str], years: list[str], max_count: int = _MAX_DEFAULT) -> list[str]:
    words = [w.strip() for w in words if w.strip()]
    years = [y.strip() for y in years if y.strip()]

    candidates: set[str] = set()

    base_forms: set[str] = set()
    for word in words:
        for variant in _case_variants(word):
            base_forms.add(variant)
            base_forms.add(variant[::-1])
            base_forms.add(variant.translate(_LEET_MAP))

    for form in base_forms:
        for suffix in _SUFFIXES:
            candidates.add(form + suffix)
        for year in years:
            candidates.add(form + year)
            candidates.add(year + form)
            candidates.add(form + year[-2:])

    if len(words) >= 2:
        for i, word_a in enumerate(words):
            for word_b in words[i + 1 :]:
                for a in _case_variants(word_a):
                    for b in _case_variants(word_b):
                        candidates.add(a + b)
                        candidates.add(b + a)
                        for year in years:
                            candidates.add(a + b + year[-2:])

    candidates.discard("")
    ordered = sorted(candidates, key=len)
    return ordered[:max_count]
