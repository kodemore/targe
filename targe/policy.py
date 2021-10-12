from datetime import datetime
from enum import Enum
from typing import List


class PolicyEffect(Enum):
    ALLOW = "allow"
    DENY = "deny"


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
        scope = scope.replace(" ", "")
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
            found_wildcard = False
            for wildcard in node["$wildcards"]:
                if match_pattern(part, wildcard):
                    node = node["$nodes"][wildcard]
                    found_wildcard = True
                    break

            if found_wildcard:
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
    if pattern == "*":
        return True

    if pattern.startswith("*"):
        if value[-len(pattern) + 1 :] == pattern[1:]:
            return True
        return False

    if pattern.endswith("*"):
        if value[: len(pattern) - 1] == pattern[:-1]:
            return True
        return False

    if pattern != value:
        return False

    return True


def normalize_scope(scope: str) -> List[str]:
    if "," not in scope:
        return [scope.replace(" ", "")]

    scopes: List[str] = []
    exploded_scope = scope.split(":")

    for section in exploded_scope:
        if "," in section:
            exploded_section = section.split(",")

            if not scopes:
                scopes = [normalised_section.strip() for normalised_section in exploded_section]
                continue

            new_scopes: List[str] = []
            for ready_scope in scopes:
                new_scopes = new_scopes + [
                    f"{ready_scope}:{normalised_section.strip()}" for normalised_section in exploded_section
                ]
            scopes = new_scopes
            continue

        if scopes:
            scopes = [f"{ready_scope}:{section.strip()}" for ready_scope in scopes]
            continue

        scopes = [section.strip()]

    return scopes
