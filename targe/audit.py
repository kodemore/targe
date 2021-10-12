from abc import abstractmethod
from datetime import datetime
from enum import Enum
from gid import Guid
from typing import List, Protocol, runtime_checkable


class AuditStatus(Enum):
    FAILED = "failed"
    SUCCEED = "succeed"

    def __str__(self) -> str:
        return self.value


class AuditEntry:
    def __init__(self, actor_id: str, scope: str):
        self.entry_id = str(Guid())
        self.actor_id = actor_id
        self.scope = scope
        self.status = AuditStatus.FAILED
        self.created_on = datetime.utcnow()

    def __str__(self) -> str:
        return f"[{self.created_on.isoformat()}] {self.actor_id} -> {self.scope} - {self.status}"


@runtime_checkable
class AuditStore(Protocol):
    @abstractmethod
    def append(self, log: AuditEntry) -> None:
        ...


class InMemoryAuditStore(AuditStore):
    def __init__(self):
        self._log: List[AuditEntry] = []

    def append(self, log: AuditEntry) -> None:
        self._log.append(log)

    def __getitem__(self, item):
        return self._log[item]

    def __iter__(self):
        return iter(self._log)

    def __len__(self):
        return len(self._log)

    def length(self) -> int:
        return len(self._log)
