"""Input validation — length/format checked before any processing.
See THREAT_MODEL.md #3 (DoS via oversized input) and baseline item 3."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ValidationResult:
    ok: bool
    reason: str = ""


def validate_text_input(text: str, max_bytes: int) -> ValidationResult:
    if not text or not text.strip():
        return ValidationResult(False, "input bo'sh bo'lmasligi kerak")
    size = len(text.encode("utf-8"))
    if size > max_bytes:
        return ValidationResult(False, f"input juda katta ({size} bayt > {max_bytes} bayt limit)")
    return ValidationResult(True)


def validate_hex_input(text: str) -> ValidationResult:
    cleaned = text.strip().replace(" ", "").replace("\n", "")
    if not cleaned:
        return ValidationResult(False, "input bo'sh bo'lmasligi kerak")
    if len(cleaned) % 2 != 0:
        return ValidationResult(False, "hex satr uzunligi juft son bo'lishi kerak")
    try:
        bytes.fromhex(cleaned)
    except ValueError:
        return ValidationResult(False, "faqat hex belgilar (0-9, a-f) qabul qilinadi")
    return ValidationResult(True)
