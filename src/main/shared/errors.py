"""Business errors shared by every bounded context, each one tied to its HTTP status.

They extend ValueError so callers that already catch ValueError keep working; the
web layer turns them into a JSON response with the right status code.
"""


class DomainError(ValueError):
    """Invalid input or broken business rule (400 Bad Request)."""

    status_code = 400


class AuthenticationError(DomainError):
    """Missing or invalid credentials (401 Unauthorized)."""

    status_code = 401


class ForbiddenError(DomainError):
    """The user is authenticated but may not act on this resource (403 Forbidden)."""

    status_code = 403


class NotFoundError(DomainError):
    """The requested resource does not exist (404 Not Found)."""

    status_code = 404


class ConflictError(DomainError):
    """The resource's current state does not allow the operation (409 Conflict)."""

    status_code = 409
