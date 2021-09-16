from dataclasses import dataclass

import pytest
from unittest.mock import MagicMock

from targe import Actor, Auth, Policy, Role
from targe.errors import AccessDeniedError, AuthorizationError, UnauthorizedError


def test_can_instantiate() -> None:
    # given
    store_mock = MagicMock()
    instance = Auth(store_mock)

    # then
    assert isinstance(instance, Auth)


def test_can_guard_resource_for_unauthorized_access() -> None:
    # given
    actor_provider = MagicMock()
    auth = Auth(actor_provider)

    @auth.guard(scope="example:action")
    def example_action() -> None:
        pass

    # then
    with pytest.raises(UnauthorizedError):
        example_action()


def test_can_guard_resource_for_denied_access() -> None:
    # given
    actor = Actor("id")
    actor.policies.append(Policy.allow("example:action2"))

    actor_provider = MagicMock()
    actor_provider.get_actor = MagicMock(return_value=actor)

    auth = Auth(actor_provider)

    @auth.guard(scope="example:action")
    def example_action(value=None) -> None:
        return value

    # then
    with pytest.raises(UnauthorizedError):
        example_action()

    # when
    auth.authorize("id")

    # then
    with pytest.raises(AccessDeniedError):
        example_action()

    # when
    actor.policies.append(Policy.allow("example:action"))

    # then
    assert example_action(10) == 10


def test_can_guard_resource_with_specific_id() -> None:
    # given
    actor = Actor("id")
    actor.policies.append(Policy.allow("user:update", "user:12"))

    actor_provider = MagicMock()
    actor_provider.get_actor = MagicMock(return_value=actor)

    auth = Auth(actor_provider)

    @auth.guard(scope="user:update", ref="user:{value}")
    def update_user(value=None) -> None:
        pass

    # when
    auth.authorize("12")

    # then
    update_user("12")
    with pytest.raises(AccessDeniedError):
        update_user("30")


def test_can_guard_resource_with_specific_id_using_ref() -> None:
    # given
    actor = Actor("id")
    actor.policies.append(Policy.allow("user:update", "12"))

    actor_provider = MagicMock()
    actor_provider.get_actor = MagicMock(return_value=actor)
    auth = Auth(actor_provider)

    @dataclass
    class User:
        id: str
        name: str

    @auth.guard(scope="user:update", ref="{ user.id }")
    def update_user(user: User) -> None:
        pass

    # when
    auth.authorize("id")

    # then
    update_user(User(id="12", name="Bob"))
    with pytest.raises(AccessDeniedError):
        update_user(User(id="30", name="Frank"))


def test_can_guard_rbac_style() -> None:
    # given
    actor = Actor("id")
    role_1 = Role("role_1")
    role_2 = Role("role_2")
    actor.roles.append(role_1)

    actor_provider = MagicMock()
    actor_provider.get_actor = MagicMock(return_value=actor)
    auth = Auth(actor_provider)

    @auth.guard(rbac=["role_1", "role_2"])
    def update_user(user: dict) -> None:
        pass

    # when
    auth.authorize("id")

    # then
    with pytest.raises(AccessDeniedError):
        update_user({})

    # when
    actor.roles.append(role_2)

    # then
    update_user({})


def test_can_guard_after() -> None:
    # given
    actor = Actor("actor_id")
    actor_provider = MagicMock()
    actor_provider.get_actor = MagicMock(return_value=actor)
    auth = Auth(actor_provider)

    @auth.guard_after(scope="example:action")
    def example_action() -> None:
        pass

    # when
    auth.authorize("actor_id")

    # then
    with pytest.raises(AccessDeniedError):
        example_action()

    # when
    actor.policies.append(Policy.allow("example:action"))

    # then
    example_action()


def test_can_override_guard_behaviour() -> None:
    # given
    def on_guard(_: Actor, scope: str, ref_id: str) -> bool:
        assert scope == "user:update"
        assert ref_id == "*"

        return True

    actor = Actor("id")
    actor_provider = MagicMock()
    actor_provider.get_actor = MagicMock(return_value=actor)

    auth = Auth(actor_provider, on_guard=on_guard)

    @auth.guard(scope="user:update")
    def update_user(user: dict) -> None:
        ...

    # when
    auth.authorize("id")

    # then
    update_user({})


def test_can_use_callable_resolver() -> None:
    # given
    actor = Actor("id")
    actor.policies.append(Policy.allow("user:update", "user:12"))

    actor_provider = MagicMock()
    actor_provider.get_actor = MagicMock(return_value=actor)
    auth = Auth(actor_provider)

    @dataclass
    class User:
        id: str
        name: str

    @auth.guard(scope="user:update", ref=lambda kwargs: f"user:{kwargs['user'].id}")
    def update_user(user: User) -> None:
        pass

    # when
    auth.authorize("id")

    # then
    update_user(User(id="12", name="Bob"))
    with pytest.raises(AccessDeniedError):
        update_user(User(id="denied_id", name="Frank"))


def test_fail_when_actor_provider_returns_invalid_type() -> None:
    # given
    actor_provider = MagicMock()
    actor_provider.get_actor = MagicMock(return_value=False)
    auth = Auth(actor_provider)

    # then
    with pytest.raises(AuthorizationError):
        auth.authorize("user_id")


def test_can_use_custom_actor_definition_for_actor_provider() -> None:
    # given
    class MyActor(Actor):
        pass

    actor_provider = MagicMock()
    actor_provider.get_actor = MagicMock(return_value=MyActor("user_id"))
    auth = Auth(actor_provider)

    # when
    actor = auth.authorize("user_id")

    # then
    assert isinstance(actor, MyActor)
