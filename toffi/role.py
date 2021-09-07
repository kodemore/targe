from typing import List

from toffi import Policy


class Role:
    def __init__(self, name: str):
        self.role_id = name
        self.name = name
        self.policies: List[Policy] = []
