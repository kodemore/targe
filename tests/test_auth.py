from dataclasses import dataclass
from functools import wraps
from unittest.mock import MagicMock

import pytest

from targe import Actor, Auth, Policy, Role, PolicyEffect
from targe.errors import AccessDeniedError, AuthorizationError, UnauthorizedError


def test_can_instantiate() -> None:
    # given
    store_mock = MagicMock()
    instance = Auth(store_mock)

    # then
    assert isinstance(instance, Auth)


def test_can_guard_resource_from_unauthorized_access() -> None:
    # given
    actor_provider = MagicMock()
    auth = Auth(actor_provider)

    @auth.guard(scope="access : denied")
    def example_action() -> None:
        pass

    # then
    with pytest.raises(UnauthorizedError):
        example_action()


def test_can_guard_resource_from_denied_access() -> None:
    # given
    actor = Actor("id")
    actor_provider = MagicMock()
    actor_provider.get_actor = MagicMock(return_value=actor)

    auth = Auth(actor_provider)

    @auth.guard(scope="articles : update")
    def update_article(article=None) -> None:
        ...

    # then
    with pytest.raises(UnauthorizedError):
        update_article()

    # when
    auth.authorize("actor_id")

    # then
    with pytest.raises(AccessDeniedError):
        update_article()

    # when
    actor.policies.append(Policy.allow("articles : update"))

    # then
    update_article()


def test_can_guard_resource_with_specific_id() -> None:
    # given
    actor = Actor("actor_id")
    actor.policies.append(Policy.allow("articles : allowed_article_id : update"))

    actor_provider = MagicMock()
    actor_provider.get_actor = MagicMock(return_value=actor)

    auth = Auth(actor_provider)

    @auth.guard(scope="articles : { article_id } : update")
    def update_article(article_id=None) -> None:
        pass

    # when
    auth.authorize("actor_id")

    # then
    update_article("allowed_article_id")
    with pytest.raises(AccessDeniedError):
        update_article("other_article_id")


def test_can_guard_rbac_style() -> None:
    # given
    actor = Actor("id")
    role_1 = Role("role_1")
    role_2 = Role("role_2")
    actor.roles.append(role_1)

    actor_provider = MagicMock()
    actor_provider.get_actor = MagicMock(return_value=actor)
    auth = Auth(actor_provider)

    @auth.guard(roles=["role_1", "role_2"])
    def update_article(article: dict) -> None:
        pass

    # when
    auth.authorize("id")

    # then
    with pytest.raises(AccessDeniedError):
        update_article({})

    # when
    actor.roles.append(role_2)

    # then
    update_article({})


def test_can_guard_after() -> None:
    # given
    actor = Actor("actor_id")
    actor_provider = MagicMock()
    actor_provider.get_actor = MagicMock(return_value=actor)
    auth = Auth(actor_provider)
    called_times = 0

    @auth.guard_after(scope="example:action")
    def example_action() -> None:
        nonlocal called_times
        called_times += 1

    # when
    auth.authorize("actor_id")

    # then
    with pytest.raises(AccessDeniedError):
        example_action()

    assert called_times == 1

    # when
    actor.policies.append(Policy.allow("example:action"))

    # then
    example_action()
    assert called_times == 2


def test_can_override_guard_behaviour() -> None:
    # given
    def on_guard(_: Actor, scope: str) -> bool:
        assert scope == "article:update:article_id"

        return True

    actor = Actor("id")
    actor_provider = MagicMock()
    actor_provider.get_actor = MagicMock(return_value=actor)

    auth = Auth(actor_provider, on_guard=on_guard)

    @auth.guard(scope="article : update : { article.id }")
    def update_article(article: dict) -> None:
        ...

    # when
    auth.authorize("actor_id")

    # then
    update_article({"id": "article_id"})


def test_can_use_callable_scope() -> None:
    # given
    actor = Actor("id")
    actor.policies.append(Policy.allow("article : update : article_id"))

    actor_provider = MagicMock()
    actor_provider.get_actor = MagicMock(return_value=actor)
    auth = Auth(actor_provider)

    @dataclass
    class Article:
        id: str
        title: str

    @auth.guard(scope=lambda actor_, kwargs: f"article : update : {kwargs['article'].id}")
    def update_user(article: Article) -> None:
        pass

    # when
    auth.authorize("id")

    # then
    update_user(Article(id="article_id", title="Lorem Ipsum"))
    with pytest.raises(AccessDeniedError):
        update_user(Article(id="denied_id", title="Lorem Lorem"))


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


def test_can_resolve_parameters_for_wrapped_function() -> None:
    # given
    class MyActor(Actor):
        pass

    actor_provider = MagicMock()
    actor_provider.get_actor = MagicMock(return_value=MyActor("user_id"))
    auth = Auth(actor_provider)

    def _decorator(*args):
        def _decorated(func):
            @wraps(func)
            def _wrapped(*args_, **kwargs):
                return func(*args_, **kwargs)

            return _wrapped

        return _decorated

    @auth.guard(scope="test : {value}")
    @_decorator()
    def handler(value):
        ...

    # when
    auth.authorize("id")

    with pytest.raises(AccessDeniedError) as e:
        handler("12")

    assert e.value.kwargs["scope"] == "test:12"


def test_can_guard_method_from_unauthorized_access() -> None:
    # given
    actor_provider = MagicMock()
    auth = Auth(actor_provider)

    class TestResource:
        @auth.guard(scope="access : denied")
        def example_action(self) -> None:
            pass

    resource = TestResource()

    # then
    with pytest.raises(UnauthorizedError):
        resource.example_action()


def test_can_guard_method_access() -> None:
    # given
    actor = Actor("id")
    actor.policies.append(Policy.allow("article : 12"))
    actor_provider = MagicMock()
    auth = Auth(actor_provider)
    actor_provider.get_actor = MagicMock(return_value=actor)

    class ArticleRepository:
        @auth.guard(scope="article : {value}")
        def get_article(self, value):
            return value

    repository = ArticleRepository()

    # when
    auth.authorize()

    # then
    repository.get_article("12")

    with pytest.raises(AccessDeniedError):
        repository.get_article("10")


def test_can_guard_resource_with_structured_id() -> None:
    # given
    actor = Actor("actor_id")
    actor.policies.append(Policy.allow("articles : nature / * : update"))
    actor.policies.append(Policy.allow("articles : article_id : update"))

    actor_provider = MagicMock()
    actor_provider.get_actor = MagicMock(return_value=actor)

    auth = Auth(actor_provider)

    article = {"id": "article_id", "category": "nature/animals/elephant", "title": "Lorem Ipsum"}

    @auth.guard(scope="articles : { article.category } , { article.id } : update")
    def update_article(article=None) -> None:
        pass

    # when
    auth.authorize("actor_id")

    # then
    update_article(article)
