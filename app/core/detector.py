"""Encoding detection: entropy + character-set heuristics (no external library)."""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass

_HEX_RE = re.compile(r"^[0-9a-fA-F\s]+$")
_BASE64_RE = re.compile(r"^[A-Za-z0-9+/]+={0,2}$")
_BASE64URL_RE = re.compile(r"^[A-Za-z0-9\-_]+={0,2}$")
_BASE32_RE = re.compile(r"^[A-Z2-7\s]+={0,6}$")
_BINARY_RE = re.compile(r"^[01\s]+$")
_DECIMAL_BYTES_RE = re.compile(r"^(\d{1,3})(\s+\d{1,3})*$")
_URL_ESCAPE_RE = re.compile(r"%[0-9A-Fa-f]{2}")


@dataclass(frozen=True)
class Detection:
    encoding: str
    confidence: float  # 0..1


def shannon_entropy(data: bytes) -> float:
    if not data:
        return 0.0
    counts = Counter(data)
    length = len(data)
    return -sum((c / length) * math.log2(c / length) for c in counts.values())


def printable_ratio(data: bytes) -> float:
    if not data:
        return 0.0
    printable = sum(1 for b in data if 32 <= b < 127 or b in (9, 10, 13))
    return printable / len(data)


def _stripped(text: str) -> str:
    return text.strip()


def looks_like_hex(text: str) -> float:
    s = _stripped(text).replace(" ", "").replace("\n", "")
    if len(s) < 2 or len(s) % 2 != 0:
        return 0.0
    if not _HEX_RE.match(s):
        return 0.0
    return 0.9


def looks_like_base64(text: str) -> float:
    # Real base64 never contains an inline space; only newlines are collapsed
    # (line-wrapped payloads). This also keeps multi-word plaintext (whose
    # letters alone are a subset of the base64 alphabet) from being
    # misdetected once spaces are stripped.
    s = _stripped(text).replace("\n", "").replace("\r", "")
    if len(s) < 4 or len(s) % 4 != 0:
        return 0.0
    if not _BASE64_RE.match(s):
        return 0.0
    # Pure hex/decimal strings also satisfy the base64 alphabet; nudge
    # confidence down when the string uses only [0-9a-fA-F] (ambiguous with hex).
    non_hex_chars = sum(1 for c in s if c.lower() not in "0123456789abcdef=")
    confidence = 0.85 if non_hex_chars > 0 else 0.55
    return confidence


def looks_like_base64url(text: str) -> float:
    s = _stripped(text)
    if len(s) < 4 or not _BASE64URL_RE.match(s):
        return 0.0
    if "-" not in s and "_" not in s:
        return 0.0  # indistinguishable from plain base64 otherwise
    return 0.8


def looks_like_base32(text: str) -> float:
    s = _stripped(text).replace("\n", "").replace("\r", "")
    if len(s) < 8 or len(s) % 8 != 0:
        return 0.0
    if not _BASE32_RE.match(s):
        return 0.0
    return 0.7


def looks_like_binary(text: str) -> float:
    s = _stripped(text)
    digits = s.replace(" ", "").replace("\n", "")
    if len(digits) < 8 or len(digits) % 8 != 0:
        return 0.0
    if not _BINARY_RE.match(s):
        return 0.0
    return 0.85


def looks_like_decimal_bytes(text: str) -> float:
    s = _stripped(text)
    if not _DECIMAL_BYTES_RE.match(s):
        return 0.0
    parts = s.split()
    if not parts or any(not (0 <= int(p) <= 255) for p in parts):
        return 0.0
    return 0.6


def looks_like_url_encoded(text: str) -> float:
    matches = _URL_ESCAPE_RE.findall(text)
    if not matches:
        return 0.0
    ratio = len("".join(matches)) * 3 / max(len(text), 1)
    return min(0.95, 0.4 + ratio)


_DETECTORS = {
    "hex": looks_like_hex,
    "base64": looks_like_base64,
    "base64url": looks_like_base64url,
    "base32": looks_like_base32,
    "binary": looks_like_binary,
    "decimal": looks_like_decimal_bytes,
    "url": looks_like_url_encoded,
}


def detect(text: str) -> list[Detection]:
    """Return encoding candidates sorted by confidence, highest first."""
    if not text or not text.strip():
        return []
    results = []
    for name, fn in _DETECTORS.items():
        confidence = fn(text)
        if confidence > 0:
            results.append(Detection(name, confidence))
    results.sort(key=lambda d: d.confidence, reverse=True)
    return results
