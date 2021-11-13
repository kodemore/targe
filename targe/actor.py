from abc import abstractmethod
from typing import Protocol, runtime_checkable, Any

from .policy import Policy, PolicyEffect, CompiledPolicies
from .utils import ObservableList


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

    def is_allowed(self, scope: str) -> bool:
        if not self._ready:
            self.compile()

        return self._compiled_policies.is_allowed(scope)

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
    def get_actor(self, context: Any = None) -> Actor:
        ...


__all__ = ["Actor", "ActorProvider", "CompiledPolicies"]
