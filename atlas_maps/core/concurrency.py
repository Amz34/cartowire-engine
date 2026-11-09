"""Token bucket rate limiter and concurrency controller for bot-proof scaling."""
from __future__ import annotations

import asyncio
import time


class TokenBucketRateLimiter:
    """
    Thread-safe asynchronous token bucket rate limiter.
    Ensures outgoing requests remain strictly beneath endpoint throttle thresholds.
    """

    def __init__(self, rate: float = 2.0, capacity: float = 5.0):
        self.rate = rate  # tokens added per second
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        """Acquire a token, asynchronously waiting if the bucket is exhausted."""
        async with self._lock:
            while True:
                now = time.monotonic()
                elapsed = now - self.last_update
                self.last_update = now
                self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)

                if self.tokens >= 1.0:
                    self.tokens -= 1.0
                    return

                # Calculate sleep required for next token
                needed = 1.0 - self.tokens
                wait_time = needed / self.rate
                await asyncio.sleep(wait_time)
