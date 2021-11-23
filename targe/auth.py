from functools import wraps
from inspect import signature
from typing import Any, Callable, List, Union, Optional, Dict

from .actor import Actor, ActorProvider
from .audit import AuditEntry, AuditStatus, AuditStore, InMemoryAuditStore
from .errors import AccessDeniedError, AuthorizationError, InvalidReferenceError, UnauthorizedError
from .utils import resolve_reference

OnGuardFunction = Callable[[Actor, str], bool]
ScopeResolverFunction = Callable[[Actor, Dict[str, Any]], str]


class Auth:
    def __init__(
        self,
        actor_provider: ActorProvider,
        audit_store: AuditStore = None,
        on_guard: OnGuardFunction = None,
    ):
        self.actor_provider = actor_provider
        self.audit_store = audit_store if audit_store is not None else InMemoryAuditStore()
        self._actor: Actor = None  # type: ignore
        self._on_guard: Optional[OnGuardFunction] = on_guard

    def authorize(self, context: Any = None) -> Actor:
        self._actor = self.actor_provider.get_actor(context)
        if not isinstance(self._actor, Actor):
            raise AuthorizationError.for_invalid_actor(self._actor)

        return self._actor

    @property
    def actor(self) -> Actor:
        return self._actor

    def guard(self, scope: Union[str, ScopeResolverFunction] = "*", roles: List[str] = None) -> Callable:
        def _decorator(function: Callable) -> Any:
            @wraps(function)
            def _decorated(*args, **kwargs) -> Any:
                if self.actor is None:
                    raise UnauthorizedError.for_missing_actor()

                resolved_scope = self._resolve_scope(scope, function, kwargs, args)
                audit_entry = AuditEntry(self.actor.actor_id, resolved_scope)

                # rbac mode
                if roles is not None:
                    self._guard_with_rbac(roles, audit_entry if scope != "*" else None)

                # acl mode
                if scope != "*":
                    self._guard_with_acl(resolved_scope, audit_entry)

                audit_entry.status = AuditStatus.SUCCEED
                self.audit_store.append(audit_entry)

                return function(*args, **kwargs)

            return _decorated

        return _decorator

    def guard_after(self, scope: Union[str, ScopeResolverFunction], rbac: List[str] = None) -> Callable:
        def _decorator(function: Callable) -> Any:
            @wraps(function)
            def _decorated(*args, **kwargs) -> Any:
                if self.actor is None:
                    raise UnauthorizedError.for_missing_actor()

                result = function(*args, **kwargs)
                kwargs["return"] = result

                resolved_scope = self._resolve_scope(scope, function, kwargs, args)
                audit_entry = AuditEntry(self.actor.actor_id, resolved_scope)

                # rbac mode
                if rbac is not None:
                    self._guard_with_rbac(rbac, audit_entry if scope != "*" else None)
                    return result

                # acl mode
                self._guard_with_acl(resolved_scope, audit_entry)

                return result

            return _decorated

        return _decorator

    def is_allowed(self, scope: str) -> bool:
        allowed = self.actor.is_allowed(scope)
        if not allowed and self._on_guard is not None:
            allowed = self._on_guard(self.actor, scope)
        return allowed

    def _guard_with_rbac(self, rbac: List[str], audit_entry: AuditEntry = None):
        if not self.actor.has_role(*rbac):
            if audit_entry is not None:
                self.audit_store.append(audit_entry)
            raise AccessDeniedError.for_missing_roles(rbac)

    def _guard_with_acl(self, scope: str, audit_entry: AuditEntry = None):
        if not self.is_allowed(scope):
            if audit_entry is not None:
                self.audit_store.append(audit_entry)
            raise AccessDeniedError.for_scope(scope)

    def _resolve_scope(self, scope: Union[str, ScopeResolverFunction], function: Any, kwargs, args) -> str:
        if scope == "*":
            return scope  # type: ignore

        co_names = tuple(signature(function).parameters.keys())

        all_kwargs = (
            {**kwargs, **dict(zip(co_names, args))}
        )

        if callable(scope):
            resolved_scope = scope(self.actor, all_kwargs)
        else:
            try:
                resolved_scope = resolve_reference(all_kwargs, scope)
            except (AttributeError, KeyError) as error:
                raise InvalidReferenceError.for_unresolved_reference(scope, function) from error

        return resolved_scope.replace(" ", "")
