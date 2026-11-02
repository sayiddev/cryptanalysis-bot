"""CyberChef-style automatic decode chain: repeatedly detect + decode until
the result looks like readable text, a cycle is found, or max depth is hit.
"""

from __future__ import annotations

import base64
import binascii
from dataclasses import dataclass, field
from urllib.parse import unquote_to_bytes

from app.core import detector, scoring

MAX_DEPTH_DEFAULT = 6
DETECTION_CONFIDENCE_THRESHOLD = 0.5
XOR_SINGLE_BYTE_MAX_CHI2_PER_LETTER = 6.0  # chi-squared/letter needed to accept a guess


@dataclass
class ChainStep:
    encoding: str
    confidence: float
    output_preview: str


@dataclass
class ChainResult:
    steps: list[ChainStep] = field(default_factory=list)
    final_text: str = ""
    final_bytes: bytes = b""
    is_plaintext: bool = False
    stopped_reason: str = ""


def _decode_hex(data: bytes) -> bytes:
    s = data.decode("ascii").replace(" ", "").replace("\n", "").replace("\r", "")
    return bytes.fromhex(s)


def _decode_base64(data: bytes) -> bytes:
    s = data.decode("ascii").strip()
    padding_needed = (-len(s)) % 4
    return base64.b64decode(s + "=" * padding_needed)


def _decode_base64url(data: bytes) -> bytes:
    s = data.decode("ascii").strip()
    padding_needed = (-len(s)) % 4
    return base64.urlsafe_b64decode(s + "=" * padding_needed)


def _decode_base32(data: bytes) -> bytes:
    s = data.decode("ascii").strip().replace(" ", "").upper()
    padding_needed = (-len(s)) % 8
    return base64.b32decode(s + "=" * padding_needed)


def _decode_binary(data: bytes) -> bytes:
    bits = data.decode("ascii").replace(" ", "").replace("\n", "").replace("\r", "")
    return bytes(int(bits[i : i + 8], 2) for i in range(0, len(bits), 8))


def _decode_decimal(data: bytes) -> bytes:
    parts = data.decode("ascii").split()
    return bytes(int(p) for p in parts)


def _decode_url(data: bytes) -> bytes:
    return unquote_to_bytes(data.decode("ascii"))


_DECODERS = {
    "hex": _decode_hex,
    "base64": _decode_base64,
    "base64url": _decode_base64url,
    "base32": _decode_base32,
    "binary": _decode_binary,
    "decimal": _decode_decimal,
    "url": _decode_url,
}


def _best_single_byte_xor(data: bytes) -> tuple[int, bytes, float] | None:
    """Return (key, decoded_bytes, chi2_per_letter) for the best-scoring key, or None."""
    best: tuple[int, bytes, float] | None = None
    for key in range(256):
        candidate = bytes(b ^ key for b in data)
        try:
            text = candidate.decode("ascii")
        except UnicodeDecodeError:
            continue
        letters = scoring.clean_letters(text)
        if len(letters) < 8:
            continue
        score = scoring.chi_squared_distance(text) / len(letters)
        if best is None or score < best[2]:
            best = (key, candidate, score)
    return best


def auto_chain(text: str, max_depth: int = MAX_DEPTH_DEFAULT) -> ChainResult:
    result = ChainResult()
    current = text.encode("utf-8", errors="ignore")
    seen: set[bytes] = {current}

    for _ in range(max_depth):
        text_repr = current.decode("latin-1")

        candidates = [
            d for d in detector.detect(text_repr) if d.confidence >= DETECTION_CONFIDENCE_THRESHOLD
        ]

        decoded_this_round = False
        for candidate in candidates:
            decoder_fn = _DECODERS.get(candidate.encoding)
            if decoder_fn is None:
                continue
            try:
                new_bytes = decoder_fn(current)
            except (ValueError, binascii.Error, UnicodeDecodeError):
                continue
            if not new_bytes or new_bytes == current or new_bytes in seen:
                continue
            seen.add(new_bytes)
            current = new_bytes
            result.steps.append(
                ChainStep(candidate.encoding, candidate.confidence, _preview(current))
            )
            decoded_this_round = True
            break

        if decoded_this_round:
            continue

        if scoring.looks_english_quick(text_repr):
            result.is_plaintext = True
            result.stopped_reason = "looks_like_english"
            break

        # Fallback: try a single-byte XOR brute force before giving up.
        xor_guess = _best_single_byte_xor(current)
        if xor_guess is not None and xor_guess[2] <= XOR_SINGLE_BYTE_MAX_CHI2_PER_LETTER:
            key, new_bytes, _score = xor_guess
            if new_bytes not in seen:
                seen.add(new_bytes)
                current = new_bytes
                result.steps.append(
                    ChainStep(f"xor_single_byte(key=0x{key:02x})", 0.5, _preview(current))
                )
                continue

        result.stopped_reason = "no_further_encoding_detected"
        break
    else:
        result.stopped_reason = "max_depth_reached"

    result.final_bytes = current
    result.final_text = current.decode("utf-8", errors="replace")
    if not result.is_plaintext:
        result.is_plaintext = scoring.looks_english_quick(current.decode("latin-1"))
    return result


def _preview(data: bytes, limit: int = 120) -> str:
    text = data.decode("utf-8", errors="replace")
    return text if len(text) <= limit else text[:limit] + "…"
