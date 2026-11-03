"""ROT13 and ROT47 — fixed-shift ciphers, no key to break (self-reciprocal:
applying twice returns the original)."""

from __future__ import annotations

from app.core.classical_ciphers import caesar_encrypt


def rot13(text: str) -> str:
    return caesar_encrypt(text, 13)


def rot47(text: str) -> str:
    out = []
    for ch in text:
        code = ord(ch)
        if 33 <= code <= 126:
            out.append(chr(33 + (code - 33 + 47) % 94))
        else:
            out.append(ch)
    return "".join(out)
