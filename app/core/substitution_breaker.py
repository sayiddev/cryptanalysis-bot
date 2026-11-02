"""Monoalphabetic substitution cryptanalysis via hill-climbing (with a touch of
simulated annealing to escape local optima) scored by quadgram statistics.
Own implementation — no external cryptanalysis library.
"""

from __future__ import annotations

import math
import random
import string
from dataclasses import dataclass

from app.core import scoring

ALPHABET = string.ascii_uppercase


@dataclass
class SubstitutionResult:
    mapping: dict[str, str]  # ciphertext letter -> plaintext letter
    plaintext: str
    score: float  # quadgram log score, higher (less negative) is better


def _frequency_informed_mapping(ciphertext: str) -> dict[str, str]:
    """Warm start: map the most frequent ciphertext letters to the most
    frequent English letters, instead of a fully random permutation."""
    letters = [c for c in ciphertext.upper() if c.isalpha()]
    counts = {c: letters.count(c) for c in set(letters)}
    cipher_by_freq = sorted(ALPHABET, key=lambda c: -counts.get(c, 0))
    english_by_freq = sorted(scoring.MONOGRAM_FREQ, key=lambda c: -scoring.MONOGRAM_FREQ[c])
    mapping = dict(zip(cipher_by_freq, english_by_freq))
    for c in ALPHABET:
        mapping.setdefault(c, c)
    return mapping


def _apply_mapping(ciphertext: str, mapping: dict[str, str]) -> str:
    out = []
    for ch in ciphertext:
        if ch.isalpha():
            upper = ch.upper()
            mapped = mapping.get(upper, upper)
            out.append(mapped if ch.isupper() else mapped.lower())
        else:
            out.append(ch)
    return "".join(out)


def _random_swap(mapping: dict[str, str]) -> dict[str, str]:
    a, b = random.sample(ALPHABET, 2)
    new_mapping = dict(mapping)
    new_mapping[a], new_mapping[b] = new_mapping[b], new_mapping[a]
    return new_mapping


def _hill_climb_once(
    ciphertext: str, iterations: int, start_temperature: float
) -> SubstitutionResult:
    mapping = _frequency_informed_mapping(ciphertext)
    plaintext = _apply_mapping(ciphertext, mapping)
    best_score = scoring.quadgram_log_score(plaintext)
    best_mapping = mapping
    best_plaintext = plaintext

    current_mapping = mapping
    current_score = best_score

    for i in range(iterations):
        temperature = start_temperature * (1 - i / iterations)
        candidate_mapping = _random_swap(current_mapping)
        candidate_plaintext = _apply_mapping(ciphertext, candidate_mapping)
        candidate_score = scoring.quadgram_log_score(candidate_plaintext)

        delta = candidate_score - current_score
        accept = delta > 0
        if not accept and temperature > 1e-6:
            accept = random.random() < math.exp(delta / temperature)

        if accept:
            current_mapping = candidate_mapping
            current_score = candidate_score
            if current_score > best_score:
                best_score = current_score
                best_mapping = current_mapping
                best_plaintext = candidate_plaintext

    return SubstitutionResult(mapping=best_mapping, plaintext=best_plaintext, score=best_score)


def crack_substitution(
    ciphertext: str, restarts: int = 8, iterations: int = 2000
) -> SubstitutionResult:
    """Run several independent hill-climbing restarts, keep the best result."""
    best: SubstitutionResult | None = None
    for _ in range(restarts):
        result = _hill_climb_once(ciphertext, iterations, start_temperature=4.0)
        if best is None or result.score > best.score:
            best = result
    assert best is not None
    return best
