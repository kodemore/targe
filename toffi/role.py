from typing import List
from datetime import datetime

from gid import Guid

from toffi import Policy


class Role:
    def __init__(self, name: str):
        self.role_id = str(Guid())
        self.name = name
        self.policies: List[Policy] = []
        self.created_at = datetime.utcnow()
