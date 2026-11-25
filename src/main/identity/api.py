"""Public API of the identity context: the only thing other contexts may use from it."""

from identity.domain.user import User

__all__ = ["IdentityApi", "User"]


class IdentityApi:
    def __init__(self, user_repository):
        self._users = user_repository

    def find_user(self, user_id):
        return self._users.find_by_id(user_id)
