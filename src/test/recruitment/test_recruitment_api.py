import unittest
from types import SimpleNamespace
from unittest.mock import create_autospec

from recruitment.api import RecruitmentApi
from recruitment.domain.i_job_application_repository import IJobApplicationRepository
from recruitment.domain.i_job_posting_repository import IJobPostingRepository


class TestRecruitmentApi(unittest.TestCase):
    def test_job_application_ids_for_company_covers_every_posting_of_the_company(self):
        job_postings = create_autospec(IJobPostingRepository, instance=True)
        job_applications = create_autospec(IJobApplicationRepository, instance=True)
        job_postings.find_by_company_id.return_value = [SimpleNamespace(id=1), SimpleNamespace(id=2)]
        job_applications.find_by_job_posting_id.side_effect = lambda posting_id: {
            1: [SimpleNamespace(id=10), SimpleNamespace(id=11)],
            2: [SimpleNamespace(id=20)],
        }[posting_id]

        ids = RecruitmentApi(job_postings, job_applications).job_application_ids_for_company(7)

        self.assertEqual([10, 11, 20], ids)
        job_postings.find_by_company_id.assert_called_once_with(7)
