"""One-way hash functions and simple encodings offered in the "Qurish"
(build/encrypt) menu alongside the classical ciphers. These use Python's
standard hashlib/base64 — crypto primitives, not a cryptanalysis library,
which the assignment brief explicitly allows ("Use libraries for plumbing:
... crypto primitives where the brief allows")."""

from __future__ import annotations

import base64
import hashlib


def sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha1_hex(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8"), usedforsecurity=False).hexdigest()


def md5_hex(text: str) -> str:
    return hashlib.md5(text.encode("utf-8"), usedforsecurity=False).hexdigest()


def base64_encode(text: str) -> str:
    return base64.b64encode(text.encode("utf-8")).decode("ascii")
