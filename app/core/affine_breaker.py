"""Affine cipher: E(x) = (a*x + b) mod 26. Own encrypt/decrypt plus a
brute-force breaker (only 12*26=312 valid (a,b) pairs — small enough to
try every one and score with chi-squared letter-frequency fit)."""

from __future__ import annotations

from dataclasses import dataclass
from math import gcd

from app.core import scoring

ALPHABET_SIZE = 26
_VALID_A = [a for a in range(1, ALPHABET_SIZE) if gcd(a, ALPHABET_SIZE) == 1]


@dataclass
class AffineResult:
    a: int
    b: int
    plaintext: str
    score: float  # lower chi-squared = better fit to English


def _mod_inverse(a: int, m: int) -> int:
    for candidate in range(1, m):
        if (a * candidate) % m == 1:
            return candidate
    raise ValueError(f"{a} has no inverse mod {m}")


def affine_encrypt(text: str, a: int, b: int) -> str:
    if gcd(a, ALPHABET_SIZE) != 1:
        raise ValueError(f"a={a} is not coprime with 26 — not a valid Affine key")
    out = []
    for ch in text:
        if ch.isalpha():
            base = ord("A") if ch.isupper() else ord("a")
            x = ord(ch) - base
            out.append(chr((a * x + b) % ALPHABET_SIZE + base))
        else:
            out.append(ch)
    return "".join(out)


def affine_decrypt(text: str, a: int, b: int) -> str:
    a_inv = _mod_inverse(a, ALPHABET_SIZE)
    out = []
    for ch in text:
        if ch.isalpha():
            base = ord("A") if ch.isupper() else ord("a")
            y = ord(ch) - base
            out.append(chr((a_inv * (y - b)) % ALPHABET_SIZE + base))
        else:
            out.append(ch)
    return "".join(out)


def crack_affine(ciphertext: str, candidates: int = 3) -> list[AffineResult]:
    results = []
    for a in _VALID_A:
        for b in range(ALPHABET_SIZE):
            plaintext = affine_decrypt(ciphertext, a, b)
            score = scoring.chi_squared_distance(plaintext)
            results.append(AffineResult(a=a, b=b, plaintext=plaintext, score=score))
    results.sort(key=lambda r: r.score)
    return results[:candidates]
