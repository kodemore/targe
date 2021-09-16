import re
from collections import UserList
from copy import copy
from typing import Any, Callable, Dict


class ObservableList(UserList):
    def __init__(self, data: list, on_change: Callable):
        super(ObservableList, self).__init__()
        self.data = data
        self.on_change = on_change

    def append(self, item: Any) -> None:
        super().append(item)
        self.on_change(copy(self.data))

    def insert(self, i: int, item: Any) -> None:
        super().insert(i, item)
        self.on_change(copy(self.data))

    def pop(self, i: int = ...) -> Any:  # type: ignore
        result = super().pop(i)
        self.on_change(copy(self.data))
        return result

    def remove(self, item: Any) -> None:
        super().remove(item)
        self.on_change(copy(self.data))

    def clear(self) -> None:
        super().clear()
        self.on_change(copy(self.data))


def match_rule(value: str, rule: str) -> bool:
    if rule == "*":
        return True

    values = value.split(":")
    rules = rule.split(":")
    rules_length = len(rules)

    if rules_length > len(values):
        return False

    for i in range(0, len(values)):
        value_part = values[i]
        if i >= rules_length:
            if rules[-1] == "*":
                continue
            return False

        rule_part = rules[i]

        if rule_part == "*":
            continue

        if rule_part.startswith("*"):
            if value_part[-len(rule_part) + 1 :] == rule_part[1:]:
                continue
            return False

        if rule_part.endswith("*"):
            if value_part[: len(rule_part) - 1] == rule_part[:-1]:
                continue
            return False

        if rule_part != value_part:
            return False

    return True


_ID_PATTERN = r"[_a-z][_a-z0-9\.]*"
_VAR_PATTERN = r"\{\s*" f"(?:(?P<var>{_ID_PATTERN}))" r"(?P<ignore>.*?)" r"\s*\}"
_VAR_MATCHER = re.compile(_VAR_PATTERN)


def _resolve_variable(obj: Any, match) -> str:
    current = obj
    reference = match.group("var")
    var = reference.split(".")
    for attr in var:
        if hasattr(current, "__getitem__"):
            current = current[attr]
        elif hasattr(current, attr):
            current = getattr(current, attr)
        else:
            raise KeyError(f"Could not resolve referenced value `{reference}`")

    return str(current)


def resolve_reference(obj: Dict[str, Any], reference: str) -> str:
    result = _VAR_MATCHER.sub(lambda match: _resolve_variable(obj, match), reference)
    return result
