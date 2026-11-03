"""Standalone statistical analysis of a piece of text — the same
measurements (entropy, Index of Coincidence, chi-squared) used internally
by the breakers, exposed directly as a user-facing tool."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from app.core.detector import shannon_entropy
from app.core.scoring import chi_squared_distance, clean_letters
from app.core.vigenere_breaker import index_of_coincidence


@dataclass
class TextAnalysis:
    length: int
    letter_count: int
    shannon_entropy_bits: float
    index_of_coincidence: float
    chi_squared_vs_english: float
    top_letters: list[tuple[str, int]]
    looks_english: bool


def analyze_text(text: str) -> TextAnalysis:
    letters = clean_letters(text)
    counts = Counter(letters)
    top_letters = counts.most_common(5)

    return TextAnalysis(
        length=len(text),
        letter_count=len(letters),
        shannon_entropy_bits=shannon_entropy(text.encode("utf-8", errors="ignore")),
        index_of_coincidence=index_of_coincidence(letters),
        chi_squared_vs_english=chi_squared_distance(text) if letters else 0.0,
        top_letters=top_letters,
        looks_english=bool(letters) and (chi_squared_distance(text) / max(len(letters), 1)) <= 6.0,
    )
