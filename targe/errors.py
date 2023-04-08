from gaffe import Error


class TargeError(Error):
    pass


class UnauthorizedError(TargeError):
    missing_actor: Exception


class AccessDeniedError(TargeError):
    scope_not_allowed: Exception
    insufficient_roles: Exception


class InvalidReferenceError(TargeError):
    unresolved_reference: Exception


class AuthorizationError(TargeError):
    invalid_actor: ValueError


class InvalidIdentifierNameError(TargeError):
    invalid_role_name: ValueError
