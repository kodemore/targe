from abc import abstractmethod
from typing import Protocol, runtime_checkable

from .policy import Policy, PolicyEffect
from .utils import ObservableList, match_rule


class CompiledPolicies:
    def __init__(self):
        self.permissions = {}

    def attach(self, policy: Policy) -> None:
        current = self.permissions
        for index in policy.scope.split(":"):
            if index not in current:
                current[index] = {}

            if "$wildcards" not in current:
                current["$wildcards"] = set()

            if index.endswith("*") and len(index) > 1:
                current["$wildcards"].add(index)

            current = current[index]

        if "$refs" not in current:
            current["$refs"] = {}

        # unify structure
        if "$wildcards" not in current:
            current["$wildcards"] = set()

        current["$refs"][policy.ref] = policy.effect

        # reorder keys, longer should be positioned first
        refs = current["$refs"]
        ordered_keys = sorted(
            list(refs.keys()),
            key=lambda key: len(key) + key.count(":") * 1000,
            reverse=True,
        )
        ordered_refs = {key: refs[key] for key in ordered_keys}
        current["$refs"] = ordered_refs

    def is_allowed(self, scope: str, index: str = "*") -> bool:
        scope_items = scope.split(":")

        node = self.permissions
        if not node:
            return False

        for part in scope_items:
            # index exists in scope, so lets use it
            if part in node:
                node = node[part]
                continue

            # look into wildcards
            if node["$wildcards"]:
                found_wildcard = False
                for wildcard in node["$wildcards"]:
                    if part.startswith(wildcard[0:-1]):
                        found_wildcard = True
                        node = node[wildcard]
                        break
                if found_wildcard:
                    continue

            # catch all in scope lets use it
            if "*" in node:
                node = node["*"]
                continue

            # scope has ended prematurely, there is no definition and no wildcards
            return False

        # get access record for resource
        if index in node["$refs"]:
            return node["$refs"][index] == PolicyEffect.ALLOW

        # find match
        for rule in node["$refs"]:
            if match_rule(index, rule):
                return node["$refs"][rule] == PolicyEffect.ALLOW

        # no definition
        return False


class Actor:
    def __init__(self, actor_id: str):
        self.roles = ObservableList([], self._on_change)
        self.policies = ObservableList([], self._on_change)

        self._actor_id = actor_id
        self._compiled_policies: CompiledPolicies = CompiledPolicies()
        self._ready = False

    @property
    def actor_id(self) -> str:
        return self._actor_id

    def is_allowed(self, scope: str, index: str = "*") -> bool:
        if not self._ready:
            self.compile()

        return self._compiled_policies.is_allowed(scope, index)

    def on_change(self) -> None:
        pass

    def _on_change(self, _) -> None:
        self.compile()
        self.on_change()

    def compile(self) -> None:
        self._compiled_policies = CompiledPolicies()

        for role in self.roles:
            for policy in role.policies:
                self._compiled_policies.attach(policy)

        for policy in self.policies:
            self._compiled_policies.attach(policy)

        self._ready = True

    def has_role(self, *role_id: str) -> bool:
        role_list = {role.name for role in self.roles}

        for role in role_id:
            if role not in role_list:
                return False

        return True


@runtime_checkable
class ActorProvider(Protocol):
    @abstractmethod
    def get_actor(self, actor_id: str) -> Actor:
        ...


__all__ = ["Actor", "ActorProvider", "CompiledPolicies"]
