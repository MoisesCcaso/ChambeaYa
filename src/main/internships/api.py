"""Public API of the internships context: the only thing other contexts may use from it."""

from internships.domain.internship import Internship

__all__ = ["Internship", "InternshipsApi"]


class InternshipsApi:
    def __init__(self, internship_repository, internship_service):
        self._internships = internship_repository
        self._service = internship_service

    def find_internship(self, internship_id):
        return self._internships.find_by_id(internship_id)

    def find_by_job_application_id(self, job_application_id):
        return self._internships.find_by_job_application_id(job_application_id)

    def get_for_user(self, user_id, internship_id):
        """Returns the internship if the user may see it; raises NotFound/Forbidden otherwise."""
        return self._service.get_for_user(user_id, internship_id)
