"""Encryption side of the classical ciphers the bot also knows how to break.

Lets a user encrypt a message and immediately feed the ciphertext back into
/xor, /vigenere or /substitution to watch the bot recover it without the key.
"""

from __future__ import annotations

import random
import string

ALPHABET_SIZE = 26


def caesar_encrypt(text: str, shift: int) -> str:
    shift %= ALPHABET_SIZE
    out = []
    for ch in text:
        if ch.isalpha():
            base = ord("A") if ch.isupper() else ord("a")
            out.append(chr((ord(ch) - base + shift) % ALPHABET_SIZE + base))
        else:
            out.append(ch)
    return "".join(out)


def vigenere_encrypt(text: str, key: str) -> str:
    if not key or not key.isalpha():
        raise ValueError("key must be a non-empty alphabetic string")
    key = key.upper()
    out = []
    key_index = 0
    for ch in text:
        if ch.isalpha():
            shift = ord(key[key_index % len(key)]) - ord("A")
            base = ord("A") if ch.isupper() else ord("a")
            out.append(chr((ord(ch) - base + shift) % ALPHABET_SIZE + base))
            key_index += 1
        else:
            out.append(ch)
    return "".join(out)


def xor_encrypt_hex(text: str, key: str) -> str:
    if not key:
        raise ValueError("key must not be empty")
    key_bytes = key.encode("utf-8")
    data = text.encode("utf-8")
    encrypted = bytes(b ^ key_bytes[i % len(key_bytes)] for i, b in enumerate(data))
    return encrypted.hex()


def random_substitution_encrypt(text: str, seed: int | None = None) -> tuple[str, dict[str, str]]:
    """Encrypt with a random monoalphabetic substitution; returns (ciphertext, mapping)."""
    rng = random.Random(seed)
    letters = list(string.ascii_uppercase)
    shuffled = letters[:]
    rng.shuffle(shuffled)
    mapping = dict(zip(letters, shuffled))

    out = []
    for ch in text:
        if ch.isalpha():
            mapped = mapping[ch.upper()]
            out.append(mapped if ch.isupper() else mapped.lower())
        else:
            out.append(ch)
    return "".join(out), mapping
