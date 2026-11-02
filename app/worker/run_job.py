"""Entry point for one isolated cryptanalysis job.

Run as a subprocess (`python -m app.worker.run_job`): reads a single JSON job
spec from stdin, applies CPU/memory limits (POSIX only — a Linux container in
production), and writes a single JSON result line to stdout. Never imports or
executes anything from the job input itself (no eval/exec/pickle) — only the
fixed set of core-engine functions below is reachable.
"""

from __future__ import annotations

import json
import os
import sys

from app.core import chain, substitution_breaker, vigenere_breaker, xor_breaker

try:
    import resource

    HAS_RESOURCE = True
except ImportError:  # Windows dev machines — limits enforced by the caller's timeout only
    HAS_RESOURCE = False


def _apply_resource_limits() -> None:
    if not HAS_RESOURCE:
        print("warning: resource module unavailable, skipping CPU/memory limits", file=sys.stderr)
        return
    cpu_seconds = int(os.environ.get("JOB_TIMEOUT_SECONDS", "20"))
    memory_mb = int(os.environ.get("JOB_MEMORY_LIMIT_MB", "256"))
    resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds))
    memory_bytes = memory_mb * 1024 * 1024
    try:
        resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))
    except (ValueError, OSError):
        pass  # some platforms (e.g. macOS) don't support RLIMIT_AS fully


def _run_chain(text: str) -> dict:
    result = chain.auto_chain(text)
    return {
        "steps": [
            {"encoding": s.encoding, "confidence": s.confidence, "preview": s.output_preview}
            for s in result.steps
        ],
        "final_text": result.final_text,
        "is_plaintext": result.is_plaintext,
        "stopped_reason": result.stopped_reason,
    }


def _run_xor(hex_ciphertext: str, max_key_len: int = 40, candidates: int = 3) -> dict:
    data = bytes.fromhex(hex_ciphertext.strip())
    results = xor_breaker.crack_repeating_key_xor(data, max_key_len=max_key_len, candidates=candidates)
    return {
        "candidates": [
            {
                "key_hex": r.key.hex(),
                "key_ascii": r.key.decode("ascii", errors="replace"),
                "key_length": r.key_length,
                "plaintext": r.plaintext,
                "score": r.score,
            }
            for r in results
        ]
    }


def _run_vigenere(ciphertext: str, max_key_len: int = 20, candidates: int = 3) -> dict:
    results = vigenere_breaker.crack_vigenere(ciphertext, max_key_len=max_key_len, candidates=candidates)
    return {
        "candidates": [
            {
                "key": r.key,
                "key_length": r.key_length,
                "plaintext": r.plaintext,
                "score": r.score,
            }
            for r in results
        ]
    }


def _run_substitution(ciphertext: str, restarts: int = 8, iterations: int = 2000) -> dict:
    result = substitution_breaker.crack_substitution(ciphertext, restarts=restarts, iterations=iterations)
    return {
        "mapping": result.mapping,
        "plaintext": result.plaintext,
        "score": result.score,
    }


_DISPATCH = {
    "chain": lambda job: _run_chain(job["input"]),
    "xor": lambda job: _run_xor(job["input"], **job.get("params", {})),
    "vigenere": lambda job: _run_vigenere(job["input"], **job.get("params", {})),
    "substitution": lambda job: _run_substitution(job["input"], **job.get("params", {})),
}


def main() -> None:
    _apply_resource_limits()
    raw = sys.stdin.read()
    try:
        job = json.loads(raw)
        job_type = job["job_type"]
        handler = _DISPATCH.get(job_type)
        if handler is None:
            raise ValueError(f"unknown job_type: {job_type}")
        result = handler(job)
        print(json.dumps({"ok": True, "result": result}))
    except Exception as exc:  # noqa: BLE001 — isolated process, must always report back as JSON
        print(json.dumps({"ok": False, "error": str(exc), "error_type": type(exc).__name__}))


if __name__ == "__main__":
    main()
