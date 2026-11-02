"""English-likelihood scoring used by the chain decoder and the cipher breakers.

Quadgram statistics are loaded from a local corpus (see scripts/build_quadgrams.py) —
no external library or dataset is used, per the assignment's "own implementation" rule.
"""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

_DATA_DIR = Path(__file__).resolve().parent / "data"
_QUADGRAMS_PATH = _DATA_DIR / "quadgrams.json"

# Standard English monogram frequencies (percent), used for a cheap quick check.
MONOGRAM_FREQ = {
    "E": 12.70, "T": 9.06, "A": 8.17, "O": 7.51, "I": 6.97, "N": 6.75,
    "S": 6.33, "H": 6.09, "R": 5.99, "D": 4.25, "L": 4.03, "C": 2.78,
    "U": 2.76, "M": 2.41, "W": 2.36, "F": 2.23, "G": 2.02, "Y": 1.97,
    "P": 1.93, "B": 1.29, "V": 0.98, "K": 0.77, "J": 0.15, "X": 0.15,
    "Q": 0.10, "Z": 0.07,
}

_LETTERS_ONLY_RE = re.compile(r"[^A-Za-z]")


@lru_cache(maxsize=1)
def _load_quadgrams() -> tuple[dict[str, float], float]:
    payload = json.loads(_QUADGRAMS_PATH.read_text(encoding="utf-8"))
    return payload["log_probs"], payload["floor_log_prob"]


def clean_letters(text: str) -> str:
    """Upper-case letters only, everything else stripped."""
    return _LETTERS_ONLY_RE.sub("", text).upper()


def quadgram_log_score(text: str) -> float:
    """Total log10-probability of the text under the quadgram model.

    Higher (closer to 0, less negative) means more English-like.
    Returns a very negative number for empty/too-short input.
    """
    letters = clean_letters(text)
    if len(letters) < 4:
        return -1e6
    log_probs, floor = _load_quadgrams()
    return sum(log_probs.get(letters[i : i + 4], floor) for i in range(len(letters) - 3))


def average_quadgram_score(text: str) -> float:
    """Per-quadgram average log score — comparable across different text lengths."""
    letters = clean_letters(text)
    n = len(letters) - 3
    if n <= 0:
        return -12.0
    return quadgram_log_score(text) / n


def looks_english(text: str, threshold: float = -3.6) -> bool:
    """Quick heuristic: does this text look like real English (vs. random bytes)?"""
    letters = clean_letters(text)
    if len(letters) < 8:
        return False
    return average_quadgram_score(text) >= threshold


def looks_english_quick(
    text: str, max_chi2_per_letter: float = 6.0, min_letters: int = 12, min_letter_ratio: float = 0.55
) -> bool:
    """Monogram chi-squared heuristic — robust even with a small quadgram corpus.

    English letter-frequency chi-squared distance per letter is typically well
    under ~3 for real prose and well over ~8 for uniformly random letters, so
    this works as a cheap "is this readable text?" gate for the decode chain.
    """
    letters = clean_letters(text)
    if len(letters) < min_letters:
        return False
    if len(letters) / max(len(text), 1) < min_letter_ratio:
        return False
    return chi_squared_distance(text) / len(letters) <= max_chi2_per_letter


def chi_squared_distance(text: str) -> float:
    """Chi-squared distance of the text's letter frequency vs. standard English.

    Lower = closer to English. Used as a fast fitness check for XOR/Vigenere
    key-length candidates before running the more expensive quadgram scorer.
    """
    letters = clean_letters(text)
    if not letters:
        return 1e9
    n = len(letters)
    counts = {c: 0 for c in MONOGRAM_FREQ}
    for c in letters:
        if c in counts:
            counts[c] += 1
    chi2 = 0.0
    for letter, expected_pct in MONOGRAM_FREQ.items():
        expected = expected_pct / 100.0 * n
        observed = counts[letter]
        if expected > 0:
            chi2 += (observed - expected) ** 2 / expected
    return chi2
