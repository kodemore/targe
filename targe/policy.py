from datetime import datetime
from enum import Enum


class PolicyEffect(Enum):
    ALLOW = "allow"
    DENY = "deny"


class Policy:
    def __init__(self, scope: str, ref: str = "*", access: PolicyEffect = PolicyEffect.ALLOW):
        self.ref = ref
        self.scope = scope
        self.effect = access
        self.created_at = datetime.utcnow()

    @classmethod
    def allow(cls, scope: str, ref: str = "*") -> "Policy":
        return Policy(scope, ref, PolicyEffect.ALLOW)

    @classmethod
    def deny(cls, scope: str, ref: str = "*") -> "Policy":
        return Policy(scope, ref, PolicyEffect.DENY)
