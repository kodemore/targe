from typing import Any


class ToffiError(Exception):
    pass


class UnauthorizedError(ToffiError, RuntimeError):
    @classmethod
    def for_missing_actor(cls) -> "UnauthorizedError":
        return cls("Unauthorized access - no actor present, did you forget to call Auth.authorize?")


class AccessDeniedError(ToffiError, RuntimeError):

    @classmethod
    def on_scope_for_reference(cls, scope: str, reference: str) -> "AccessDeniedError":
        return AccessDeniedError(f"Access denied on scope:`{scope}` for referenced resource:`#{reference}`")


class InvalidReferenceError(ToffiError, AttributeError):

    @classmethod
    def for_unresolved_reference(cls, reference: str, function: Any) -> "InvalidReferenceError":
        return cls(f"Could not resolve reference `{reference}` for guarded function `{function}`.")


class AuthSessionError(ToffiError, RuntimeError):
    @classmethod
    def for_invalid_actor(cls, actor_id: str):
        return cls(f"Could not initialize session for actor {actor_id}")


class InvalidIdentifierNameError(ValueError):
    @classmethod
    def for_invalid_role_name(cls, name: str) -> "InvalidIndentifierNameError":
        return cls(f"Provided role name `{name}` is invalid, roles must follow `[a-z][a-z0-9_-]` pattern.")
