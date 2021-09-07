from toffi import Actor
from toffi.audit import AuditEntry
from abc import abstractmethod
from typing import Protocol, runtime_checkable


@runtime_checkable
class AuthStore(Protocol):
    @abstractmethod
    def get_actor(self, actor_id: str) -> Actor:
        ...

    def log(self, log: AuditEntry) -> None:
        ...
