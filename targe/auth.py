from functools import wraps
from typing import Any, Callable, List, Union, Optional

from .actor import Actor, ActorProvider
from .audit import AuditLog, AuditStatus, AuditStore, InMemoryAuditStore
from .errors import AccessDeniedError, AuthorizationError, InvalidReferenceError, UnauthorizedError
from .utils import resolve_reference

OnGuardFunction = Callable[[Actor, str, str], bool]


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

    def authorize(self, actor_id: str) -> Actor:
        self._actor = self.actor_provider.get_actor(actor_id)
        if not isinstance(self._actor, Actor):
            raise AuthorizationError.for_invalid_actor(actor_id)

        return self._actor

    @property
    def actor(self) -> Actor:
        return self._actor

    def guard(self, scope: str = "*", ref: Union[str, Callable] = "*", rbac: List[str] = None) -> Callable:
        def _decorator(function: Callable) -> Any:
            @wraps(function)
            def _decorated(*args, **kwargs) -> Any:
                if self.actor is None:
                    raise UnauthorizedError.for_missing_actor()

                resolved_reference = self._resolve_reference(ref, function, kwargs, args)
                audit_entry = AuditLog(self.actor.actor_id, scope, resolved_reference)

                # rbac mode
                if rbac is not None:
                    self._guard_with_rbac(rbac, audit_entry if scope != "*" else None)
                    return function(*args, **kwargs)

                # acl mode
                self._guard_with_acl(scope, resolved_reference, audit_entry)

                return function(*args, **kwargs)

            return _decorated

        return _decorator

    def guard_after(self, scope: str, ref: Union[str, Callable] = "*", rbac: List[str] = None) -> Callable:
        def _decorator(function: Callable) -> Any:
            @wraps(function)
            def _decorated(*args, **kwargs) -> Any:
                if self.actor is None:
                    raise UnauthorizedError.for_missing_actor()

                result = function(*args, **kwargs)
                kwargs["return"] = result

                resolved_reference = self._resolve_reference(ref, function, kwargs, args)
                audit_entry = AuditLog(self.actor.actor_id, scope, resolved_reference)

                # rbac mode
                if rbac is not None:
                    self._guard_with_rbac(rbac, audit_entry if scope != "*" else None)
                    return result

                # acl mode
                self._guard_with_acl(scope, resolved_reference, audit_entry)

                return result

            return _decorated

        return _decorator

    def is_allowed(self, scope: str, reference: str) -> bool:
        allowed = self.actor.is_allowed(scope, reference)
        if not allowed and self._on_guard is not None:
            allowed = self._on_guard(self.actor, scope, reference)
        return allowed

    def _guard_with_rbac(self, rbac: List[str], audit_entry: AuditLog = None):
        if not self.actor.has_role(*rbac):
            if audit_entry is not None:
                self.audit_store.append(audit_entry)
            raise AccessDeniedError.for_missing_roles(rbac)
        if audit_entry is not None:
            audit_entry.status = AuditStatus.SUCCEED
            self.audit_store.append(audit_entry)

    def _guard_with_acl(self, scope: str, reference: str, audit_entry: AuditLog = None):
        if not self.is_allowed(scope, reference):
            if audit_entry is not None:
                self.audit_store.append(audit_entry)
            raise AccessDeniedError.on_scope_for_reference(scope, reference)

        if audit_entry is not None:
            audit_entry.status = AuditStatus.SUCCEED
            self.audit_store.append(audit_entry)

    @staticmethod
    def _resolve_reference(ref: Union[str, Callable], function: Any, kwargs, args) -> str:
        if ref == "*":
            return ref  # type: ignore

        all_kwargs = (
            {**kwargs, **dict(zip(function.__code__.co_varnames, args))} if hasattr(function, "__code__") else kwargs
        )

        if callable(ref):
            resolved_reference = ref(all_kwargs)
        else:
            try:
                resolved_reference = resolve_reference(all_kwargs, ref)
            except (AttributeError, KeyError) as error:
                raise InvalidReferenceError.for_unresolved_reference(ref, function) from error

        return resolved_reference
