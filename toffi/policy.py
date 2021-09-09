from datetime import datetime

from enum import Enum


class PolicyEffect(Enum):
    ALLOW = "allow"
    DENY = "deny"


class Policy:
    def __init__(self, scope: str, index: str = "*", access: PolicyEffect = PolicyEffect.ALLOW):
        self.created_at = datetime.utcnow()
        self.scope = scope
        self.index = index
        self.access = access

    @classmethod
    def allow(cls, scope: str, index: str = "*") -> "Policy":
        return Policy(scope, index, PolicyEffect.ALLOW)

    @classmethod
    def deny(cls, scope: str, index: str = "*") -> "Policy":
        return Policy(scope, index, PolicyEffect.DENY)
