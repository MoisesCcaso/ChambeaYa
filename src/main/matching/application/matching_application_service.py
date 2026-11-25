from matching.domain.matching_domain_service import MatchingDomainService
from shared.errors import ForbiddenError


class MatchingApplicationService:
    def __init__(self, suggestion_repository=None, profile_repository=None,
                 job_posting_repository=None, matching_domain_service=None,
                 intern_repository=None):
        self.suggestion_repository = suggestion_repository
        self.intern_repository = intern_repository or profile_repository
        self.profile_repository = self.intern_repository
        self.job_posting_repository = job_posting_repository
        self.matching_domain_service = matching_domain_service or MatchingDomainService()

    def suggest_job_postings(self, user_id, threshold=50.0):
        self._require_repositories()

        intern = self.profile_repository.find_intern_by_user_id(user_id)
        if intern is None:
            raise ForbiddenError("Practicante no encontrado")

        job_postings = self.job_posting_repository.find_all()
        return self.matching_domain_service.filter_job_postings(intern, job_postings, threshold)

    def calculate_for_intern(self, user_id):
        self._require_repositories()

        intern = self.profile_repository.find_intern_by_user_id(user_id)
        if intern is None:
            raise ForbiddenError("Practicante no encontrado")

        job_postings = self.job_posting_repository.find_all()
        results = self.matching_domain_service.filter_job_postings(intern, job_postings)

        for result in results:
            self.suggestion_repository.save(getattr(result, "suggestion", result))

        return results

    def _require_repositories(self):
        if self.suggestion_repository is None:
            raise RuntimeError("MatchingApplicationService requires a suggestion repository")
        if self.profile_repository is None:
            raise RuntimeError("MatchingApplicationService requires a profile repository")
        if self.job_posting_repository is None:
            raise RuntimeError("MatchingApplicationService requires a job posting repository")
