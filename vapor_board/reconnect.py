"""Bounded, caller-driven TCP reconnect policy; no background loop."""
from dataclasses import dataclass
from .tcp import ConnectionState


@dataclass(frozen=True)
class ReconnectPolicy:
    max_attempts: int = 4
    initial_delay: float = 1.0
    max_delay: float = 8.0

    def __post_init__(self):
        if type(self.max_attempts) is not int or not 1 <= self.max_attempts <= 20:
            raise ValueError("max_attempts must be 1..20")
        if isinstance(self.initial_delay, bool) or not isinstance(self.initial_delay, (int, float)) or not 0 < self.initial_delay <= 60:
            raise ValueError("invalid initial delay")
        if isinstance(self.max_delay, bool) or not isinstance(self.max_delay, (int, float)) or self.max_delay < self.initial_delay or self.max_delay > 300:
            raise ValueError("invalid max delay")

    def delay(self, failed_attempts):
        if type(failed_attempts) is not int or failed_attempts < 1:
            raise ValueError("failed_attempts must be positive")
        return min(self.max_delay, self.initial_delay * (2 ** min(failed_attempts - 1, 16)))


class ReconnectController:
    """One connect attempt per step; caller decides when to schedule next step."""
    def __init__(self, client, policy=None):
        self.client = client
        self.policy = policy or ReconnectPolicy()
        self.failures = 0

    def step(self):
        if self.client.state == ConnectionState.CONNECTED:
            self.failures = 0
            return True, None
        if self.failures >= self.policy.max_attempts:
            return False, None
        ok = self.client.connect()
        if ok:
            self.failures = 0
            return True, None
        self.failures += 1
        if self.failures >= self.policy.max_attempts:
            return False, None
        return False, self.policy.delay(self.failures)

    def reset(self):
        self.failures = 0
