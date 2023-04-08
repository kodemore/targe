from datetime import datetime
from enum import Enum
from typing import List


class PolicyEffect(Enum):
    ALLOW = "allow"
    DENY = "deny"


def normalize_scope(scope: str) -> List[str]:
    exploded_scope = scope.replace(" ", "").split(":")
    scopes = []

    for section in exploded_scope:
        exploded_section = [s.strip() for s in section.split(",")]

        if not scopes:
            scopes = exploded_section
        else:
            scopes = [
                f"{ready_scope}:{normalised_section}"
                for ready_scope in scopes for normalised_section in exploded_section
            ]

    return scopes


class Policy:
    def __init__(self, scope: str, access: PolicyEffect = PolicyEffect.ALLOW):
        self.scope = scope
        self.effect = access
        self.created_at = datetime.utcnow()

    @classmethod
    def allow(cls, scope: str) -> "Policy":
        return Policy(scope, PolicyEffect.ALLOW)

    @classmethod
    def deny(cls, scope: str) -> "Policy":
        return Policy(scope, PolicyEffect.DENY)


class CompiledPolicies:
    def __init__(self):
        self.permissions = {}

    def attach(self, policy: Policy) -> None:
        scopes = normalize_scope(policy.scope)
        for scope in scopes:
            self._attach_scope(scope, policy.effect)

    def _attach_scope(self, scope: str, effect: PolicyEffect) -> None:
        current = self.permissions
        for index in scope.split(":"):
            if "$nodes" not in current:
                current["$nodes"] = {}

            index = index.strip()

            if index not in current["$nodes"]:
                current["$nodes"][index] = {}

            if "$wildcards" not in current:
                current["$wildcards"] = set()

            if index.count("*") == 1:
                current["$wildcards"].add(index)
                current["$wildcards"] = set(
                    sorted(
                        list(current["$wildcards"]),
                        key=lambda key: len(key),
                        reverse=True,
                    )
                )

            current = current["$nodes"][index]

        current["$effect"] = effect

    def is_allowed(self, scope: str) -> bool:
        if "," not in scope:
            return self._is_allowed(scope.replace(" ", ""))

        scopes = normalize_scope(scope)
        for scope in scopes:
            if self._is_allowed(scope):
                return True

        return False

    def _is_allowed(self, scope: str) -> bool:
        scope_items = scope.split(":")

        node = self.permissions
        if not node:
            return False

        effect = PolicyEffect.DENY
        interrupted = False

        for part in scope_items:
            if "$nodes" not in node:
                interrupted = True
                break

            if "*" in node["$nodes"] and "$effect" in node["$nodes"]["*"]:
                effect = node["$nodes"]["*"]["$effect"]

            # index exists in scope, so lets use it
            if part in node["$nodes"]:
                node = node["$nodes"][part]
                continue

            # early return if no wildcards are available
            if not node["$wildcards"]:
                interrupted = True
                break

            # search for matching wildcard
            found_wildcard = next((wildcard for wildcard in node["$wildcards"] if match_pattern(part, wildcard)), None)
            if found_wildcard:
                node = node["$nodes"][found_wildcard]
                continue

            # scope has ended prematurely, there is no definition and no wildcards
            interrupted = True
            break

        if not interrupted:
            if "$effect" in node:
                effect = node["$effect"]
            # there is no rule for current scope, lets check for wildcard
            elif effect != PolicyEffect.ALLOW:
                try:
                    effect = node["$nodes"]["*"]["$effect"]
                except KeyError:
                    effect = PolicyEffect.DENY

        return effect == PolicyEffect.ALLOW


def match_pattern(value: str, pattern: str) -> bool:
    segments = pattern.split("*")
    start_pos = 0

    for segment in segments:
        index = value.find(segment, start_pos)

        if index == -1:
            return False

        start_pos = index + len(segment)

    return True
