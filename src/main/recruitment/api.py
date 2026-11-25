"""Public API of the recruitment context: the only thing other contexts may use from it."""

from recruitment.domain.job_application import JobApplication
from recruitment.domain.job_posting import JobPosting

__all__ = ["JobApplication", "JobPosting", "RecruitmentApi"]


class RecruitmentApi:
    def __init__(self, job_posting_repository, job_application_repository):
        self._job_postings = job_posting_repository
        self._job_applications = job_application_repository

    def find_job_posting(self, job_posting_id):
        return self._job_postings.find_by_id(job_posting_id)

    def find_job_application(self, job_application_id):
        return self._job_applications.find_by_id(job_application_id)

    def list_job_postings(self):
        return self._job_postings.find_all()

    def job_application_ids_for_company(self, company_id):
        # shortcut: one query per job posting; add a joined repository query if companies get many postings.
        return [
            job_application.id
            for job_posting in self._job_postings.find_by_company_id(company_id)
            for job_application in self._job_applications.find_by_job_posting_id(job_posting.id)
        ]
