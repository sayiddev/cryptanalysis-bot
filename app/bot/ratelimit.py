"""Per-user token-bucket rate limiting (in-memory — single bot instance).

A production multi-instance deployment would move this to Redis; documented
as a known limitation in docs/DESIGN.md given the 2-day MVP scope.
"""

from __future__ import annotations

import time


class TokenBucket:
    def __init__(self, capacity: int, refill_per_minute: int) -> None:
        self.capacity = capacity
        self.refill_rate = refill_per_minute / 60.0  # tokens per second
        self._buckets: dict[int, tuple[float, float]] = {}  # user_id -> (tokens, last_refill)

    def allow(self, user_id: int) -> bool:
        now = time.monotonic()
        tokens, last_refill = self._buckets.get(user_id, (self.capacity, now))
        elapsed = now - last_refill
        tokens = min(self.capacity, tokens + elapsed * self.refill_rate)

        if tokens < 1:
            self._buckets[user_id] = (tokens, now)
            return False

        tokens -= 1
        self._buckets[user_id] = (tokens, now)
        return True


_default_bucket: TokenBucket | None = None


def get_rate_limiter(capacity: int, refill_per_minute: int) -> TokenBucket:
    global _default_bucket
    if _default_bucket is None:
        _default_bucket = TokenBucket(capacity, refill_per_minute)
    return _default_bucket
