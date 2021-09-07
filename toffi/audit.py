from abc import abstractmethod
from datetime import datetime
from enum import Enum
from typing import Protocol, runtime_checkable, List

from gid import Guid


class AuditStatus(Enum):
    FAILED = "failed"
    SUCCEED = "succeed"


class AuditLog:
    def __init__(self, actor_id: str, scope: str, index: str):
        self.log_id = str(Guid())
        self.actor_id = actor_id
        self.scope = scope
        self.index = index
        self.status = AuditStatus.FAILED
        self.created_on = datetime.utcnow()

    def as_succeed(self):
        self.status = AuditStatus.SUCCEED


@runtime_checkable
class AuditStore(Protocol):
    @abstractmethod
    def log(self, log: AuditLog) -> None:
        ...


class InMemoryAuditStore(AuditStore):
    def __init__(self):
        self._log: List[AuditLog] = []

    def log(self, log: AuditLog) -> None:
        self._log.append(log)
