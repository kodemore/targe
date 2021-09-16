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
    instance.attach(Policy.deny("resource:delete", "{id}"))
    instance.attach(Policy.allow("resource:set*"))
    instance.attach(Policy.deny("resource:set*:set*"))

    # then
    assert instance.permissions == {
        "$wildcards": set(),
        "resource": {
            "$wildcards": {"set*"},
            "create": {
                "$refs": {
                    "*": PolicyEffect.ALLOW,
                },
                "$wildcards": set(),
            },
            "delete": {
                "$refs": {
                    "{id}": PolicyEffect.DENY,
                },
                "$wildcards": set(),
            },
            "set*": {
                "$refs": {
                    "*": PolicyEffect.ALLOW,
                },
                "set*": {
                    "$refs": {
                        "*": PolicyEffect.DENY,
                    },
                    "$wildcards": set(),
                },
                "$wildcards": {"set*"},
            },
        },
    }


def test_is_allowed() -> None:
    # given
    instance = CompiledPolicies()

    # when
    instance.attach(Policy.allow("resource:create"))
    instance.attach(Policy.allow("resource:set*"))
    instance.attach(Policy.deny("resource:setThree"))
    instance.attach(Policy.allow("resource:update", "some_id"))

    # then
    assert not instance.is_allowed("resource2")
    assert not instance.is_allowed("resource:delete")
    assert not instance.is_allowed("resource:update")
    assert not instance.is_allowed("resource:setThree")

    assert instance.is_allowed("resource:update", "some_id")
    assert instance.is_allowed("resource:setOne")
    assert instance.is_allowed("resource:setOne", "other_id")
    assert instance.is_allowed("resource:setTwo")
    assert instance.is_allowed("resource:set")
    assert instance.is_allowed("resource:create")


def test_is_allowed_resource_path() -> None:
    # given
    instance = CompiledPolicies()

    # when
    instance.attach(Policy.allow("resource:set*", "resource:a*:*"))

    # then
    assert instance.is_allowed("resource:setName", "resource:ab:id")
    assert not instance.is_allowed("resource:setName", "resource:b:id")

    # when
    instance.attach(Policy.allow("resource:set*", "resource:*"))

    # then
    assert instance.is_allowed("resource:setName", "resource:b:id2")

    # when
    instance.attach(Policy.deny("resource:set*", "resource:b:id2"))

    # then
    assert not instance.is_allowed("resource:setName", "resource:b:id2")


def test_are_index_patterns_ordered_in_compiled_policy() -> None:
    # given
    instance = CompiledPolicies()

    # when
    instance.attach(Policy.allow("resource", "resource:a*:*"))
    instance.attach(Policy.allow("resource", "resource:a"))
    instance.attach(Policy.allow("resource", "resource:test"))
    instance.attach(Policy.allow("resource", "resource:t:t"))
    instance.attach(Policy.allow("resource", "resource:test:test:*"))

    keys = list(instance.permissions["resource"]["$refs"].keys())

    # then
    assert keys == [
        "resource:test:test:*",
        "resource:a*:*",
        "resource:t:t",
        "resource:test",
        "resource:a",
    ]
