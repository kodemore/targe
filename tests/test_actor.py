from targe import Actor, Policy, Role


def test_can_instantiate_actor() -> None:
    # given
    actor = Actor("1")

    # then
    assert isinstance(actor, Actor)


def test_can_add_policy() -> None:
    # given
    actor = Actor("1")

    # then
    assert not actor.is_allowed("user:update")

    # when
    actor.policies.append(Policy.allow("user:update"))

    # then
    assert actor.is_allowed("user:update")

    # when
    actor.policies.append(Policy.deny("user:update", "id"))

    # then
    assert actor.is_allowed("user:update")
    assert not actor.is_allowed("user:update", "id")


def test_can_add_role() -> None:
    # given
    actor = Actor("1")
    role = Role("example_role")
    role.policies.append(Policy.allow("user:create"))

    # then
    assert not actor.is_allowed("user:create")

    # when
    actor.roles.append(role)

    # then
    assert actor.is_allowed("user:create")


def test_has_role() -> None:
    # given
    actor = Actor("1")
    role_1 = Role("example_role_1")
    role_2 = Role("example_role_2")
    role_3 = Role("example_role_3")

    # then
    assert not actor.has_role("example_role_1")

    # when
    actor.roles.append(role_1)

    # then
    assert actor.has_role("example_role_1")
    assert not actor.has_role("example_role_1", "example_role_2")

    # when
    actor.roles.append(role_2)
    actor.roles.append(role_3)

    # then
    assert actor.has_role("example_role_1")
    assert actor.has_role("example_role_2")
    assert actor.has_role("example_role_3")
    assert actor.has_role("example_role_1", "example_role_3")
    assert actor.has_role("example_role_1", "example_role_2")
    assert actor.has_role("example_role_1", "example_role_2", "example_role_3")
