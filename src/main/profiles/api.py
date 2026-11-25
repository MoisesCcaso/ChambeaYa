"""Public API of the profiles context: the only thing other contexts may use from it."""

__all__ = ["ProfilesApi"]


class ProfilesApi:
    def __init__(self, profile_repository):
        self._profiles = profile_repository

    def find_intern_by_user_id(self, user_id):
        return self._profiles.find_intern_by_user_id(user_id)

    def find_intern_by_id(self, intern_id):
        return self._profiles.find_intern_by_id(intern_id)

    def find_company_by_user_id(self, user_id):
        return self._profiles.find_company_by_user_id(user_id)
