import pytest

from targe import Role


def test_can_instantiate_role() -> None:
    # given
    role = Role("name")

    # then
    assert isinstance(role, Role)


def test_fails_for_invalid_role_name() -> None:
    with pytest.raises(ValueError):
        Role("12.31")
