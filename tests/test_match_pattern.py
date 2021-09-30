import pytest

from targe.policy import match_pattern


@pytest.mark.parametrize(
    "value, rule",
    [
        ["test", "tes*"],
        ["setName", "set*"],
        ["test", "*"],
        ["setName", "*Name"],
        ["test", "test"],
    ],
)
def test_successfully_match_pattern(value: str, rule: str) -> None:
    assert match_pattern(value, rule)


@pytest.mark.parametrize(
    "value, rule",
    [
        ["123", "321"],
        ["setMet", "setA*"],
        ["test", "a*"],
        ["test", "*k"],
        ["test", "tests"],
        ["test", "t*t"],
    ],
)
def test_fail_match_pattern(value: str, rule: str) -> None:
    assert not match_pattern(value, rule)
