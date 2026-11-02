"""Repeating-key XOR cryptanalysis: key-length detection (normalized Hamming
distance) + per-column single-byte XOR break via English letter statistics.
Own implementation — no external cryptanalysis library.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.core import scoring

MAX_KEY_LENGTH_DEFAULT = 40
PRINTABLE_RATIO_MIN = 0.85


@dataclass
class XorResult:
    key: bytes
    key_length: int
    plaintext: str
    score: float  # lower chi-squared = better fit to English


def hamming_distance(a: bytes, b: bytes) -> int:
    if len(a) != len(b):
        raise ValueError("hamming_distance requires equal-length buffers")
    return sum((x ^ y).bit_count() for x, y in zip(a, b))


def _normalized_distance(data: bytes, key_len: int, max_blocks: int = 20) -> float | None:
    available = len(data) // key_len
    num_blocks = min(max_blocks, available)
    if num_blocks < 2:
        return None
    blocks = [data[i * key_len : (i + 1) * key_len] for i in range(num_blocks)]
    pairs = 0
    total = 0.0
    for i in range(len(blocks)):
        for j in range(i + 1, len(blocks)):
            total += hamming_distance(blocks[i], blocks[j]) / key_len
            pairs += 1
    return total / pairs if pairs else None


def guess_key_lengths(data: bytes, max_len: int = MAX_KEY_LENGTH_DEFAULT, top_n: int = 3) -> list[int]:
    scored: list[tuple[float, int]] = []
    upper_bound = min(max_len, len(data) // 2) or 1
    for key_len in range(1, upper_bound + 1):
        dist = _normalized_distance(data, key_len)
        if dist is not None:
            scored.append((dist, key_len))
    scored.sort(key=lambda t: t[0])
    return [key_len for _dist, key_len in scored[:top_n]]


MIN_LETTER_RATIO = 0.5


def _best_byte_for_column(column: bytes) -> tuple[int, float]:
    """Return (key_byte, chi2_per_letter) minimizing distance to English letter freq.

    chi-squared must be normalized by letter count: without that, a wrong key
    that happens to produce mostly punctuation/symbols (very few actual
    letters) can score a deceptively low *absolute* chi-squared simply
    because there is little data to accumulate deviation from — not because
    it is a better decoding.
    """
    best_key = 0
    best_score = float("inf")
    for key in range(256):
        decoded = bytes(b ^ key for b in column)
        printable = sum(1 for b in decoded if 32 <= b < 127)
        if printable / len(decoded) < PRINTABLE_RATIO_MIN:
            continue
        text = decoded.decode("ascii", errors="ignore")
        letters = scoring.clean_letters(text)
        if len(letters) / len(decoded) < MIN_LETTER_RATIO:
            continue
        score = scoring.chi_squared_distance(text) / len(letters)
        if score < best_score:
            best_score = score
            best_key = key
    return best_key, best_score


def crack_single_key_length(data: bytes, key_length: int) -> XorResult:
    columns = [data[i::key_length] for i in range(key_length)]
    key_bytes = bytearray()
    column_scores = []
    for column in columns:
        key_byte, score = _best_byte_for_column(column)
        key_bytes.append(key_byte)
        column_scores.append(score)
    key = bytes(key_bytes)
    plaintext_bytes = bytes(b ^ key[i % key_length] for i, b in enumerate(data))
    plaintext = plaintext_bytes.decode("utf-8", errors="replace")
    avg_score = sum(column_scores) / len(column_scores) if column_scores else float("inf")
    return XorResult(key=key, key_length=key_length, plaintext=plaintext, score=avg_score)


def crack_repeating_key_xor(
    data: bytes, max_key_len: int = MAX_KEY_LENGTH_DEFAULT, candidates: int = 3
) -> list[XorResult]:
    """Return up to `candidates` XorResult guesses, best (lowest score) first."""
    key_length_guesses = guess_key_lengths(data, max_len=max_key_len, top_n=candidates)
    results = [crack_single_key_length(data, kl) for kl in key_length_guesses]
    results.sort(key=lambda r: r.score)
    return results
