from functools import wraps
from typing import Any, Callable, List, Union

from toffi.actor import Actor
from .audit import AuditEntry
from .errors import AccessDeniedError, InvalidReferenceError, UnauthorizedError, AuthSessionError
from .stores import AuthStore


def _resolve_index(obj: object, path: List[str]) -> str:
    current = obj
    evaluated = ""
    for attr in path:
        evaluated = f"{evaluated}.{attr}"
        if isinstance(obj, dict):
            current = obj[attr]
        else:
            current = getattr(current, attr)

    return str(current)


class Auth:
    def __init__(self, auth_store: AuthStore, on_guard: Callable = None):
        self._actor: Actor = None  # type: ignore
        self._auth_store = auth_store
        self._on_guard = on_guard

    def init(self, actor_id: str) -> None:
        self._actor = self._auth_store.get_actor(actor_id)
        if not isinstance(self._actor, Actor):
            raise AuthSessionError.for_invalid_actor(actor_id)

    @property
    def actor(self) -> Actor:
        return self._actor

    def guard(self, scope: str, resolver: Union[str, Callable] = "*") -> Callable:
        def _decorator(function: Callable) -> Any:
            @wraps(function)
            def _decorated(*args, **kwargs) -> Any:
                if self.actor is None:
                    raise UnauthorizedError.for_missing_actor()
                all_kwargs = (
                    {**kwargs, **dict(zip(function.__code__.co_varnames, args))}
                    if hasattr(function, "__code__")
                    else kwargs
                )
                index = "*"

                if callable(resolver):
                    index = resolver(all_kwargs)
                elif resolver != "*":
                    ref_path = resolver.split(".")
                    if ref_path[0] not in all_kwargs:
                        raise InvalidReferenceError.for_missing_argument(ref_path[0], function, resolver)
                    try:
                        index = _resolve_index(all_kwargs[ref_path[0]], ref_path[1:])
                    except (AttributeError, KeyError) as error:
                        raise InvalidReferenceError.for_unresolved_reference(resolver, function) from error

                audit_entry = AuditEntry(self.actor.actor_id, scope, index)
                if not self.actor.can(scope, index):
                    allow = False
                    if self._on_guard is not None:
                        allow = self._on_guard(function, all_kwargs, scope, index)
                    if not allow:
                        self._auth_store.log(audit_entry)
                        raise AccessDeniedError(f"Access denied to resource:`#{resolver}` on scope:`{scope}`")
                    audit_entry.as_succeed()

                self._auth_store.log(audit_entry)
                return function(*args, **kwargs)

            return _decorated

        return _decorator