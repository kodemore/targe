from typing import Any, List


class TargeError(Exception):
    pass


class UnauthorizedError(TargeError, RuntimeError):
    @classmethod
    def for_missing_actor(cls) -> "UnauthorizedError":
        return cls("Unauthorized access - no actor present, did you forget to call Auth.authorize?")


class AccessDeniedError(TargeError, RuntimeError):
    @classmethod
    def for_scope(cls, scope: str) -> "AccessDeniedError":
        return AccessDeniedError(f"Access denied on scope:`{scope}`")

    @classmethod
    def for_missing_roles(cls, roles: List[str]) -> "AccessDeniedError":
        return AccessDeniedError(f"Actor is missing one of the following roles {roles}")


class InvalidReferenceError(TargeError, AttributeError):
    @classmethod
    def for_unresolved_reference(cls, reference: str, function: Any) -> "InvalidReferenceError":
        return cls(f"Could not resolve reference `{reference}` for guarded function `{function}`.")


class AuthorizationError(TargeError, TypeError):
    @classmethod
    def for_invalid_actor(cls, actor: Any):
        return cls(f"Could not initialize session for actor {actor}")


class InvalidIdentifierNameError(ValueError):
    @classmethod
    def for_invalid_role_name(cls, name: str) -> "InvalidIdentifierNameError":
        return cls(f"Provided role name `{name}` is invalid, roles must follow `[a-z][a-z0-9_-]` pattern.")
