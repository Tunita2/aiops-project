"""Blast-radius guard and circuit breaker for the closed-loop orchestrator.

BlastRadiusGuard uses sliding time windows to enforce:
  - Global max actions per minute (across all services)
  - Per-service max restarts per hour

CircuitBreaker counts consecutive failures and halts automation when the
threshold is reached.  Reset is manual (operator restarts the process).
"""

import time
from collections import defaultdict, deque

from engine.logger import JsonLogger

log = JsonLogger("safety")


class BlastRadiusGuard:
    """Enforce per-minute global and per-service-per-hour action limits.

    Uses deque-based sliding windows: timestamps older than the window
    horizon are pruned lazily on each check() call.
    """

    def __init__(self, max_per_minute: int, max_restarts_per_hour: int):
        self._max_per_minute = max_per_minute
        self._max_restarts_per_hour = max_restarts_per_hour
        self._global_window: deque[float] = deque()
        self._service_window: dict[str, deque[float]] = defaultdict(deque)

    def _prune(self, window: deque, horizon: float):
        """Remove timestamps older than the horizon from the front."""
        while window and window[0] < horizon:
            window.popleft()

    def check(self, service: str) -> tuple[bool, str]:
        """Check if an action is allowed. Returns (allowed, reason)."""
        now = time.time()

        # Prune expired timestamps
        self._prune(self._global_window, now - 60)
        self._prune(self._service_window[service], now - 3600)

        # Check global limit
        if len(self._global_window) >= self._max_per_minute:
            return False, f"global actions/min limit ({self._max_per_minute}) reached"

        # Check per-service limit
        if len(self._service_window[service]) >= self._max_restarts_per_hour:
            return False, (
                f"restarts/hour limit ({self._max_restarts_per_hour}) "
                f"for {service}"
            )

        return True, "ok"

    def record(self, service: str):
        """Record that an action was executed for the given service."""
        now = time.time()
        self._global_window.append(now)
        self._service_window[service].append(now)


class CircuitBreaker:
    """Halt automation after N consecutive verify failures.

    State transitions:
      CLOSED → (failure_count reaches threshold) → OPEN
      OPEN   → (manual restart of the process)   → CLOSED

    A single success resets the failure counter back to zero.
    """

    def __init__(self, threshold: int):
        self._threshold = threshold
        self._failures = 0
        self._open = False

    def is_open(self) -> bool:
        return self._open

    def record_failure(self):
        """Increment consecutive failure counter; open breaker if threshold hit."""
        self._failures += 1
        if self._failures >= self._threshold:
            self._open = True
            log.error(
                "CIRCUIT_BREAKER_HALT",
                consecutive_failures=self._failures,
                threshold=self._threshold,
                message="Automation halted. Manual intervention required.",
            )

    def record_success(self):
        """A successful action resets the failure counter."""
        self._failures = 0
