from datetime import datetime
from enum import Enum

from gid import Guid


class AuditStatus(Enum):
    FAILED = "failed"
    SUCCEED = "succeed"


class AuditEntry:
    def __init__(self, actor_id: str, scope: str, index: str):
        self.entry_id = str(Guid())
        self.actor_id = actor_id
        self.scope = scope
        self.index = index
        self.status = AuditStatus.FAILED
        self.created_on = datetime.utcnow()

    def as_succeed(self):
        self.status = AuditStatus.SUCCEED
