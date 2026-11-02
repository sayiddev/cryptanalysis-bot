"""Build a quadgram log-probability table from a local English text corpus.

Run once (or whenever the corpus changes):
    python scripts/build_quadgrams.py
Writes app/core/data/quadgrams.json used by the substitution hill-climbing solver.
"""

from __future__ import annotations

import json
import math
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORPUS_PATH = ROOT / "app" / "core" / "data" / "corpus_en.txt"
OUTPUT_PATH = ROOT / "app" / "core" / "data" / "quadgrams.json"


def build() -> None:
    text = CORPUS_PATH.read_text(encoding="utf-8")
    letters_only = re.sub(r"[^A-Za-z]", "", text).upper()

    counts: Counter[str] = Counter()
    for i in range(len(letters_only) - 3):
        counts[letters_only[i : i + 4]] += 1

    total = sum(counts.values())
    floor_log_prob = math.log10(0.01 / total)  # assigned to unseen quadgrams

    log_probs = {gram: math.log10(count / total) for gram, count in counts.items()}

    payload = {
        "floor_log_prob": floor_log_prob,
        "total_quadgrams": total,
        "unique_quadgrams": len(log_probs),
        "log_probs": log_probs,
    }
    OUTPUT_PATH.write_text(json.dumps(payload), encoding="utf-8")
    print(f"Wrote {len(log_probs)} quadgrams ({total} total) -> {OUTPUT_PATH}")


if __name__ == "__main__":
    build()
