import pytest
from unittest.mock import MagicMock

from targe import Actor, AuditEntry, Auth, InMemoryAuditStore, Policy, Role
from targe.errors import AccessDeniedError


def test_can_instantiate_in_memory_audit_store() -> None:
    # when
    instance = InMemoryAuditStore()

    # then
    assert isinstance(instance, InMemoryAuditStore)


def test_can_append_new_log_into_memory_store() -> None:
    # given
    store = InMemoryAuditStore()

    # when
    store.append(AuditEntry("actor_id", "scope:id"))

    # then
    assert store.length() == 1


def test_can_iterate_through_in_memory_store() -> None:
    # given
    store = InMemoryAuditStore()

    # when
    store.append(AuditEntry("actor_id", "scope:id_1"))
    store.append(AuditEntry("actor_id", "scope:id_2"))
    store.append(AuditEntry("actor_id", "scope:id_3"))
    store.append(AuditEntry("actor_id", "scope:id_4"))
    key = 0

    # then
    for key, item in enumerate(store):
        assert item.scope == f"scope:id_{key + 1}"

    assert key == 3


def test_default_audit_store_integration() -> None:
    # given
    actor = Actor("id")
    actor.policies.append(Policy.allow("user : *"))

    actor_provider = MagicMock()
    actor_provider.get_actor = MagicMock(return_value=actor)
    auth = Auth(actor_provider)

    @auth.guard(scope="user : update : { u.id }")
    def update_user(u: dict) -> None:
        pass

    @auth.guard(scope="user : read : { user_id }")
    def get_user(user_id: str) -> dict:
        return {"id": user_id}

    # when
    auth.authorize("id")
    user = get_user("12")
    update_user(user)

    # then
    assert isinstance(auth.audit_store, InMemoryAuditStore)
    assert len(auth.audit_store) == 2
    assert auth.audit_store[0].actor_id == "id"
    assert auth.audit_store[0].scope == "user:read:12"
    assert auth.audit_store[1].actor_id == "id"
    assert auth.audit_store[1].scope == "user:update:12"


def test_audit_with_rbac_style() -> None:
    # given
    actor = Actor("id")
    role = Role("user_creator")
    actor.roles.append(role)
    actor_provider = MagicMock()
    actor_provider.get_actor = MagicMock(return_value=actor)
    auth = Auth(actor_provider)

    @auth.guard(scope="user : delete : { user_id }", rbac=["user_remover"])
    def delete_user(user_id: str) -> dict:
        return {"id": user_id}

    @auth.guard(scope="user : create : { u.id }", rbac=["user_creator"])
    def create_user(u: dict) -> None:
        pass

    # when
    auth.authorize("id")
    create_user({"id": "12", "name": "Bob"})

    with pytest.raises(AccessDeniedError):
        delete_user("12")

    # then
    assert len(auth.audit_store) == 2

    assert str(auth.audit_store[0].status) == "succeed"
    assert str(auth.audit_store[1].status) == "failed"

    assert auth.audit_store[0].scope == "user:create:12"
    assert auth.audit_store[1].scope == "user:delete:12"
