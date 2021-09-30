from targe.actor import CompiledPolicies
from targe.policy import Policy, PolicyEffect


def test_can_instantiate() -> None:
    # given
    instance = CompiledPolicies()

    # then
    assert isinstance(instance, CompiledPolicies)


def test_can_attach_policy() -> None:
    # given
    instance = CompiledPolicies()

    # when
    instance.attach(Policy.allow("resource:create"))
    instance.attach(Policy.deny("resource:delete"))
    instance.attach(Policy.allow("resource:set*"))
    instance.attach(Policy.deny("resource:set*:set*"))

    # then
    assert instance.permissions == {
        "$wildcards": set(),
        "$nodes": {
            "resource": {
                "$wildcards": {"set*"},
                "$nodes": {
                    "create": {
                        "$effect": PolicyEffect.ALLOW,
                    },
                    "delete": {
                        "$effect": PolicyEffect.DENY,
                    },
                    "set*": {
                        "$effect": PolicyEffect.ALLOW,
                        "$wildcards": {"set*"},
                        "$nodes": {
                            "set*": {
                                "$effect": PolicyEffect.DENY,
                            },
                        }
                    },
                },
            },
        },
    }


def test_is_allowed_for_static_scope() -> None:
    # given
    instance = CompiledPolicies()

    # when
    instance.attach(Policy.allow("resource"))

    # then
    assert instance.is_allowed("resource")
    assert not instance.is_allowed("resource:level_1")
    assert not instance.is_allowed("resource:level_1:level_2")

    instance.attach(Policy.deny("resource:create"))
    instance.attach(Policy.allow("resource:level_1"))

    # then
    assert instance.is_allowed("resource")
    assert instance.is_allowed("resource:level_1")
    assert not instance.is_allowed("resource:level_1:level_2")
    assert not instance.is_allowed("resource:create")


def test_is_allowed_for_dynamic_scope() -> None:
    # given
    instance = CompiledPolicies()

    # when
    instance.attach(Policy.allow("resource:set*"))

    # then
    assert instance.is_allowed("resource:set")
    assert instance.is_allowed("resource:setName")
    assert instance.is_allowed("resource:setEmail")
    assert not instance.is_allowed("resource:set:set")

    # when
    instance.attach(Policy.deny("resource:setEmail"))

    # then
    assert instance.is_allowed("resource:set")
    assert instance.is_allowed("resource:setName")
    assert not instance.is_allowed("resource:setEmail")
    assert not instance.is_allowed("resource:set:set")


def test_is_allowed_for_wildcards() -> None:
    # given
    instance = CompiledPolicies()

    # when
    instance.attach(Policy.allow("resource:*"))

    # then
    assert instance.is_allowed("resource")
    assert instance.is_allowed("resource:setName")
    assert instance.is_allowed("resource:level_1:level_2")

    # when
    instance.attach(Policy.deny("resource:level_1:denied"))

    # then
    assert instance.is_allowed("resource")
    assert instance.is_allowed("resource:setName")
    assert instance.is_allowed("resource:level_1:level_2")
    assert not instance.is_allowed("resource:level_1:denied")


def test_is_allowed_for_scoped_wildcards() -> None:
    # given
    instance = CompiledPolicies()

    # when
    instance.attach(Policy.allow("resource:*:allowed"))

    # then
    assert instance.is_allowed("resource:id_1:allowed")
    assert instance.is_allowed("resource:id_n:allowed")
    assert not instance.is_allowed("resource:id")
    assert not instance.is_allowed("resource:id:denied")

    # when
    instance.attach(Policy.deny("resource:id_n:allowed"))

    # when
    assert instance.is_allowed("resource:id_1:allowed")
    assert not instance.is_allowed("resource:id_n:allowed")

    # when
    instance.attach(Policy.allow("resource_2:*"))
    instance.attach(Policy.deny("resource_2:*:denied"))

    # then
    assert instance.is_allowed("resource_2:id_1:allowed")
    assert instance.is_allowed("resource_2:id_n:allowed")
    assert instance.is_allowed("resource_2:id")
    assert not instance.is_allowed("resource_2:id:denied")


def test_is_allowed_for_grouped_policies() -> None:
    # given
    instance = CompiledPolicies()

    # when
    instance.attach(Policy.allow("resource : group-a , group-b : allow"))

    # then
    assert instance.is_allowed("resource : group-a : allow")
    assert instance.is_allowed("resource:group-b:allow")

