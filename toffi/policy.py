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
    def allow(cls, scope: str, reference: str = "*") -> "Policy":
        return Policy(scope, reference, PolicyEffect.ALLOW)

    @classmethod
    def deny(cls, scope: str, reference: str = "*") -> "Policy":
        return Policy(scope, reference, PolicyEffect.DENY)
