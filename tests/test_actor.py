from toffi import Actor, Policy, Role


def test_can_instantiate_actor() -> None:
    # given
    actor = Actor("1")

    # then
    assert isinstance(actor, Actor)


def test_can_add_policy() -> None:
    # given
    actor = Actor("1")

    # then
    assert not actor.can("user:update")

    # when
    actor.policies.append(Policy.allow("user:update"))

    # then
    assert actor.can("user:update")

    # when
    actor.policies.append(Policy.deny("user:update", "id"))

    # then
    assert actor.can("user:update")
    assert not actor.can("user:update", "id")


def test_can_add_role() -> None:
    # given
    actor = Actor("1")
    role = Role("example_role")
    role.policies.append(Policy.allow("user:create"))

    # then
    assert not actor.can("user:create")

    # when
    actor.roles.append(role)

    # then
    assert actor.can("user:create")
