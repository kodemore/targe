from toffi.utils import match_rule
import pytest


@pytest.mark.parametrize("value, rule", [
    ["test:123", "test:*"],
    ["test:setName", "test:set*"],
    ["test:set:name", "test:*:name"],
    ["test:set:name:first", "test:*"],
    ["test:getName", "test:*Name"],
    ["test:get:a", "*"],
    ["test:test:test", "test:*st:te*"],
])
def test_successfully_match_rule(value: str, rule: str) -> None:
    assert match_rule(value, rule)


@pytest.mark.parametrize("value, rule", [
    ["test:123", "test:321"],
    ["test:123", "test:123:*"],
    ["test:2", "a:2"],
    ["test:setMet", "test:setA*"],
    ["test:test", "*:a"],
    ["test:test", "test:*k"],
    ["test:test:test", "test:test"],
    ["test:test:test", "test:te*:1"],
    ["test:test:test", "test:*st:1"],
    ["test:test:test", "test:*:1"],

])
def test_fail_match_rule(value: str, rule: str) -> None:
    assert not match_rule(value, rule)
