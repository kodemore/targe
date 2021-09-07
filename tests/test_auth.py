from dataclasses import dataclass
from unittest.mock import MagicMock

import pytest

from toffi import Actor, Auth, Policy
from toffi.errors import AccessDeniedError, UnauthorizedError


def test_can_instantiate() -> None:
    # given
    store_mock = MagicMock()
    instance = Auth(store_mock)

    # then
    assert isinstance(instance, Auth)


def test_can_protect_resource_for_unauthorized_access() -> None:
    # given
    store_mock = MagicMock()
    auth = Auth(store_mock)

    @auth.guard(scope="example:action")
    def example_action() -> None:
        pass

    # then
    with pytest.raises(UnauthorizedError):
        example_action()


def test_can_protect_resource_for_denied_access() -> None:
    # given
    actor = Actor("id")
    actor.policies.append(Policy.allow("example:action2"))

    store_mock = MagicMock()
    store_mock.get_actor = MagicMock(return_value=actor)

    auth = Auth(store_mock)

    @auth.guard(scope="example:action")
    def example_action(value=None) -> None:
        return value

    # then
    with pytest.raises(UnauthorizedError):
        example_action()

    # when
    auth.init("id")

    # then
    with pytest.raises(AccessDeniedError):
        example_action()

    # when
    actor.policies.append(Policy.allow("example:action"))

    # then
    assert example_action(10) == 10


def test_can_protect_resource_with_specific_id() -> None:
    # given
    actor = Actor("id")
    actor.policies.append(Policy.allow("user:update", "12"))

    store_mock = MagicMock()
    store_mock.get_actor = MagicMock(return_value=actor)

    auth = Auth(store_mock)

    @auth.guard(scope="user:update", resolver="value")
    def update_user(value=None) -> None:
        pass

    # when
    auth.init("12")

    # then
    update_user("12")
    with pytest.raises(AccessDeniedError):
        update_user("30")


def test_can_protect_resource_with_specific_id_using_ref() -> None:
    # given
    actor = Actor("id")
    actor.policies.append(Policy.allow("user:update", "12"))

    store_mock = MagicMock()
    store_mock.get_actor = MagicMock(return_value=actor)
    auth = Auth(store_mock)

    @dataclass
    class User:
        id: str
        name: str

    @auth.guard(scope="user:update", resolver="user.id")
    def update_user(user: User) -> None:
        pass

    # when
    auth.init("id")

    # then
    update_user(User(id="12", name="Bob"))
    with pytest.raises(AccessDeniedError):
        update_user(User(id="30", name="Frank"))


def test_can_override_guard_behaviour() -> None:
    # given
    def on_guard(function: callable, kwargs: dict, scope: str, ref_id: str) -> bool:
        assert kwargs == {"user": {}}
        assert scope == "user:update"
        assert ref_id == "*"

        return True

    actor = Actor("id")
    store_mock = MagicMock()
    store_mock.get_actor = MagicMock(return_value=actor)

    auth = Auth(store_mock, on_guard=on_guard)

    @auth.guard(scope="user:update")
    def update_user(user: dict) -> None:
        ...

    # when
    auth.init("id")

    # then
    update_user({})
