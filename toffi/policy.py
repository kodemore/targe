from dataclasses import dataclass

from enum import Enum


class PolicyEffect(Enum):
    ALLOW = "allow"
    DENY = "deny"


@dataclass
class Policy:
    scope: str
    reference: str = "*"
    access: PolicyEffect = PolicyEffect.ALLOW

    @classmethod
    def allow(cls, scope: str, index: str = "*") -> "Policy":
        return Policy(scope, index, PolicyEffect.ALLOW)

    @classmethod
    def deny(cls, scope: str, index: str = "*") -> "Policy":
        return Policy(scope, index, PolicyEffect.DENY)
