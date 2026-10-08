"""
Minimal thread-safe rate limiter, a drop-in for the unmaintained ``ratelimiter``
package (its 1.2.0 release uses asyncio.coroutine, which Python 3.11 removed).

    limiter = RateLimiter(max_calls=10, period=1)
    with limiter:
        ...            # at most 10 entries per rolling 1-second window

Entering the context blocks (sleeps) when the window is full. Also usable as
a decorator. Only the parts of the old API this project uses are provided.
"""

import threading
import time
from collections import deque
from functools import wraps


class RateLimiter:
    def __init__(self, max_calls: int, period: float = 1.0, callback=None):
        if max_calls <= 0:
            raise ValueError("max_calls must be positive")
        if period <= 0:
            raise ValueError("period must be positive")
        self.max_calls = max_calls
        self.period = period
        self.callback = callback  # called with the wait time before sleeping
        self._calls = deque()
        self._lock = threading.Lock()

    def _wait_for_slot(self):
        with self._lock:
            while True:
                now = time.monotonic()
                while self._calls and now - self._calls[0] >= self.period:
                    self._calls.popleft()
                if len(self._calls) < self.max_calls:
                    self._calls.append(now)
                    return
                wait = self.period - (now - self._calls[0])
                if self.callback is not None:
                    self.callback(wait)
                time.sleep(max(wait, 0))

    def __enter__(self):
        self._wait_for_slot()
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with self:
                return func(*args, **kwargs)

        return wrapper
