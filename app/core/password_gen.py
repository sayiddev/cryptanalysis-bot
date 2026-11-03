"""Cryptographically secure random password generator (uses `secrets`,
not `random` — this is the defensive counterpart to the wordlist tools)."""

from __future__ import annotations

import secrets
import string

MIN_LENGTH = 8
MAX_LENGTH = 128
DEFAULT_LENGTH = 16

_LOWER = string.ascii_lowercase
_UPPER = string.ascii_uppercase
_DIGITS = string.digits
_SYMBOLS = "!@#$%^&*()-_=+[]{}"


def generate_strong_password(length: int = DEFAULT_LENGTH) -> str:
    length = max(MIN_LENGTH, min(MAX_LENGTH, length))

    # Guarantee at least one character from each class, then fill the rest
    # from the combined pool so every password is unpredictable.
    pool = _LOWER + _UPPER + _DIGITS + _SYMBOLS
    required = [
        secrets.choice(_LOWER),
        secrets.choice(_UPPER),
        secrets.choice(_DIGITS),
        secrets.choice(_SYMBOLS),
    ]
    remaining = [secrets.choice(pool) for _ in range(length - len(required))]

    chars = required + remaining
    for i in range(len(chars) - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        chars[i], chars[j] = chars[j], chars[i]
    return "".join(chars)


def generate_random_alpha_key(length: int = 8) -> str:
    """Random uppercase-letter key, e.g. for a Vigenere cipher."""
    length = max(1, min(64, length))
    return "".join(secrets.choice(_UPPER) for _ in range(length))


def generate_random_hex_key(length_bytes: int = 8) -> str:
    """Random hex key, e.g. for a repeating-key XOR cipher."""
    length_bytes = max(1, min(64, length_bytes))
    return secrets.token_hex(length_bytes)
