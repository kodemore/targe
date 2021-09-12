from dataclasses import dataclass
from unittest.mock import MagicMock

import pytest

from toffi import Actor, Auth, Policy, InMemoryAuditStore
from toffi.errors import AccessDeniedError, UnauthorizedError


def test_can_instantiate() -> None:
    # given
    store_mock = MagicMock()
    instance = Auth(store_mock)

    # then
    assert isinstance(instance, Auth)


def test_can_protect_resource_for_unauthorized_access() -> None:
    # given
    actor_provider = MagicMock()
    auth = Auth(actor_provider)

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
    actor.policies.append(Policy.allow("user:update", "user:12"))

    actor_provider = MagicMock()
    actor_provider.get_actor = MagicMock(return_value=actor)

    auth = Auth(actor_provider)

    @auth.guard(scope="user:update", ref="user:{value}")
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
    auth.init("id")

    # then
    update_user(User(id="12", name="Bob"))
    with pytest.raises(AccessDeniedError):
        update_user(User(id="30", name="Frank"))


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
    auth.init("id")

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
    auth.init("id")

    # then
    update_user(User(id="12", name="Bob"))
    with pytest.raises(AccessDeniedError):
        update_user(User(id="denied_id", name="Frank"))


def test_auth_audit_store() -> None:
    # given
    actor = Actor("id")
    actor.policies.append(Policy.allow("user:*", "*"))

    actor_provider = MagicMock()
    actor_provider.get_actor = MagicMock(return_value=actor)
    auth = Auth(actor_provider)

    @auth.guard(scope="user:update", ref="{ u.id }")
    def update_user(u: dict) -> None:
        pass

    @auth.guard(scope="user:read", ref="{ user_id }")
    def get_user(user_id: str) -> dict:
        return {"id": user_id}

    # when
    auth.init("id")
    user = get_user("12")
    update_user(user)

    # then
    assert isinstance(auth.audit_store, InMemoryAuditStore)
    assert len(auth.audit_store._log) == 2
    assert auth.audit_store._log[0].actor_id == "id"
    assert auth.audit_store._log[0].scope == "user:read"
    assert auth.audit_store._log[0].reference == "12"
    assert auth.audit_store._log[1].actor_id == "id"
    assert auth.audit_store._log[1].scope == "user:update"
    assert auth.audit_store._log[1].reference == "12"
