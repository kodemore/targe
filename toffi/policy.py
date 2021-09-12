from datetime import datetime

from enum import Enum


class PolicyEffect(Enum):
    ALLOW = "allow"
    DENY = "deny"


class Policy:
    def __init__(self, scope: str, ref: str = "*", access: PolicyEffect = PolicyEffect.ALLOW):
        self.created_at = datetime.utcnow()
        self.scope = scope
        self.ref = ref
        self.access = access

    @classmethod
    def allow(cls, scope: str, ref: str = "*") -> "Policy":
        return Policy(scope, ref, PolicyEffect.ALLOW)

    @classmethod
    def deny(cls, scope: str, ref: str = "*") -> "Policy":
        return Policy(scope, ref, PolicyEffect.DENY)
