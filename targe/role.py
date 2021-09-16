import re
from datetime import datetime
from typing import List

from targe import Policy
from targe.errors import InvalidIdentifierNameError

_ROLE_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9_-]+$", re.IGNORECASE)


class Role:
    def __init__(self, name: str):
        self.name = name
        self.policies: List[Policy] = []
        self.created_at = datetime.utcnow()

        self._validate()

    def _validate(self) -> None:
        if not _ROLE_NAME_PATTERN.search(self.name):
            raise InvalidIdentifierNameError.for_invalid_role_name(self.name)
