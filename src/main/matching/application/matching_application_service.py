from matching.domain.matching_domain_service import MatchingDomainService
from shared.errors import ForbiddenError


class MatchingApplicationService:
    def __init__(self, suggestion_repository=None, profiles=None,
                 recruitment=None, matching_domain_service=None):
        self.suggestion_repository = suggestion_repository
        self.profiles = profiles
        self.recruitment = recruitment
        self.matching_domain_service = matching_domain_service or MatchingDomainService()

    def suggest_job_postings(self, user_id, threshold=50.0):
        self._require_repositories()

        intern = self.profiles.find_intern_by_user_id(user_id)
        if intern is None:
            raise ForbiddenError("Practicante no encontrado")

        job_postings = self.recruitment.list_job_postings()
        return self.matching_domain_service.filter_job_postings(intern, job_postings, threshold)

    def calculate_for_intern(self, user_id):
        self._require_repositories()

        intern = self.profiles.find_intern_by_user_id(user_id)
        if intern is None:
            raise ForbiddenError("Practicante no encontrado")

        job_postings = self.recruitment.list_job_postings()
        results = self.matching_domain_service.filter_job_postings(intern, job_postings)

        for result in results:
            self.suggestion_repository.save(getattr(result, "suggestion", result))

        return results

    def _require_repositories(self):
        if self.suggestion_repository is None:
            raise RuntimeError("MatchingApplicationService requires a suggestion repository")
        if self.profiles is None:
            raise RuntimeError("MatchingApplicationService requires the profiles API")
        if self.recruitment is None:
            raise RuntimeError("MatchingApplicationService requires the recruitment API")
