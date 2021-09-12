from typing import Any


class ToffiError(Exception):
    pass


class UnauthorizedError(ToffiError, RuntimeError):
    @classmethod
    def for_missing_actor(cls) -> "UnauthorizedError":
        return cls("Unauthorized access - no actor present, did you forget to start session?")


class AccessDeniedError(ToffiError, RuntimeError):
    pass


class InvalidReferenceError(ToffiError, AttributeError):

    @classmethod
    def for_unresolved_reference(cls, reference: str, function: Any) -> "InvalidReferenceError":
        return cls(f"Could not resolve reference `{reference}` for guarded function `{function}`.")


class AuthSessionError(ToffiError, RuntimeError):
    @classmethod
    def for_invalid_actor(cls, actor_id: str):
        return cls(f"Could not initialize session for actor {actor_id}")
