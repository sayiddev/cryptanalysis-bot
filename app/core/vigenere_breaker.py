"""Vigenere cryptanalysis: Kasiski examination + Index of Coincidence for key
length, then per-column chi-squared frequency analysis to recover the key.
Own implementation — no external cryptanalysis library.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass

from app.core import scoring

ALPHABET_SIZE = 26
MAX_KEY_LENGTH_DEFAULT = 20
ENGLISH_IOC = 0.0667


@dataclass
class VigenereResult:
    key: str
    key_length: int
    plaintext: str
    score: float  # lower chi-squared = better fit


def _letters_only(text: str) -> str:
    return "".join(c for c in text.upper() if c.isalpha())


def index_of_coincidence(letters: str) -> float:
    n = len(letters)
    if n < 2:
        return 0.0
    counts = Counter(letters)
    numerator = sum(c * (c - 1) for c in counts.values())
    return numerator / (n * (n - 1))


def kasiski_examination(letters: str, seq_len: int = 3) -> list[int]:
    """Find repeated sequences of `seq_len` letters and return the distances
    between their occurrences (candidate factors for the key length)."""
    positions: dict[str, list[int]] = defaultdict(list)
    for i in range(len(letters) - seq_len + 1):
        positions[letters[i : i + seq_len]].append(i)

    distances = []
    for seq, occurrences in positions.items():
        if len(occurrences) < 2:
            continue
        for i in range(1, len(occurrences)):
            distances.append(occurrences[i] - occurrences[0])
    return distances


def _factor_votes(distances: list[int], max_len: int) -> Counter[int]:
    votes: Counter[int] = Counter()
    for d in distances:
        for candidate in range(2, max_len + 1):
            if d % candidate == 0:
                votes[candidate] += 1
    return votes


def guess_key_lengths(
    text: str, max_len: int = MAX_KEY_LENGTH_DEFAULT, top_n: int = 3
) -> list[int]:
    letters = _letters_only(text)
    distances = kasiski_examination(letters, seq_len=3)
    if not distances:
        distances = kasiski_examination(letters, seq_len=2)

    votes = _factor_votes(distances, max_len) if distances else Counter()

    # Verify/rank candidates by average per-column Index of Coincidence,
    # which should be close to ENGLISH_IOC for the true key length.
    scored: list[tuple[float, int]] = []
    candidate_lengths = sorted(votes, key=lambda k: votes[k], reverse=True)[: max(top_n * 3, 6)]
    if not candidate_lengths:
        candidate_lengths = list(range(1, min(max_len, len(letters) // 10 or 1) + 1))

    for key_len in candidate_lengths:
        columns = [letters[i::key_len] for i in range(key_len)]
        iocs = [index_of_coincidence(col) for col in columns if len(col) > 1]
        if not iocs:
            continue
        avg_ioc = sum(iocs) / len(iocs)
        closeness = abs(avg_ioc - ENGLISH_IOC)
        scored.append((closeness, key_len))

    scored.sort(key=lambda t: t[0])
    return [key_len for _closeness, key_len in scored[:top_n]] or [1]


def _best_shift_for_column(column: str) -> tuple[int, float]:
    best_shift = 0
    best_score = float("inf")
    for shift in range(ALPHABET_SIZE):
        decoded = "".join(
            chr((ord(c) - ord("A") - shift) % ALPHABET_SIZE + ord("A")) for c in column
        )
        score = scoring.chi_squared_distance(decoded)
        if score < best_score:
            best_score = score
            best_shift = shift
    return best_shift, best_score


def _vigenere_decrypt(ciphertext: str, key: str) -> str:
    key = key.upper()
    out = []
    key_index = 0
    for ch in ciphertext:
        if ch.isalpha():
            shift = ord(key[key_index % len(key)]) - ord("A")
            base = ord("A") if ch.isupper() else ord("a")
            decoded_letter = chr((ord(ch.upper()) - ord("A") - shift) % ALPHABET_SIZE + base)
            out.append(decoded_letter if ch.isupper() else decoded_letter.lower())
            key_index += 1
        else:
            out.append(ch)
    return "".join(out)


def crack_single_key_length(original_text: str, key_length: int) -> VigenereResult:
    letters = _letters_only(original_text)
    columns = [letters[i::key_length] for i in range(key_length)]
    key_chars = []
    scores = []
    for column in columns:
        shift, score = _best_shift_for_column(column)
        key_chars.append(chr(shift + ord("A")))
        scores.append(score)
    key = "".join(key_chars)
    plaintext = _vigenere_decrypt(original_text, key)
    avg_score = sum(scores) / len(scores) if scores else float("inf")
    return VigenereResult(key=key, key_length=key_length, plaintext=plaintext, score=avg_score)


def crack_vigenere(
    original_text: str, max_key_len: int = MAX_KEY_LENGTH_DEFAULT, candidates: int = 3
) -> list[VigenereResult]:
    key_length_guesses = guess_key_lengths(original_text, max_len=max_key_len, top_n=candidates)
    results = [crack_single_key_length(original_text, kl) for kl in key_length_guesses]
    results.sort(key=lambda r: r.score)
    return results
