"""Unit tests for JobPostingApplicationService with doubles."""

import unittest
from unittest.mock import create_autospec

from recruitment.application.job_posting_application_service import JobPostingApplicationService
from recruitment.domain.job_posting import JobPosting
from recruitment.domain.i_job_posting_repository import IJobPostingRepository


class TestJobPostingApplicationService(unittest.TestCase):
    """Isolated tests for the job posting application service with doubles."""

    def setUp(self):
        self.mock_repo = create_autospec(IJobPostingRepository, instance=True)
        self.service = JobPostingApplicationService(job_posting_repository=self.mock_repo)

    def test_requires_repository_in_every_operation(self):
        service_without_repo = JobPostingApplicationService(job_posting_repository=None)

        with self.assertRaises(RuntimeError) as ctx:
            service_without_repo.create_job_posting(1, {"titulo": "Test"})
        self.assertIn("requires a repository", str(ctx.exception))

        with self.assertRaises(RuntimeError):
            service_without_repo.publish(1, 10)

        with self.assertRaises(RuntimeError):
            service_without_repo.update(1, 10, {"titulo": "Nuevo"})

        with self.assertRaises(RuntimeError):
            service_without_repo.close(1, 10)

        with self.assertRaises(RuntimeError):
            service_without_repo.reopen(1, 10)

        with self.assertRaises(RuntimeError):
            service_without_repo.duplicate(1, 10)

        with self.assertRaises(RuntimeError):
            service_without_repo.delete(1, 10)

        with self.assertRaises(RuntimeError):
            service_without_repo.search()

        with self.assertRaises(RuntimeError):
            service_without_repo.find_by_id(10)

        with self.assertRaises(RuntimeError):
            service_without_repo.list_for_company(1)

    def test_create_job_posting_validates_and_saves(self):
        data = {
            "titulo": "Practicante Python",
            "descripcion": "Backend dev",
            "habilidades_requeridas": ["Python"],
            "beneficios": ["Remoto"],
        }
        saved_job_posting = JobPosting(id=1, company_id=5, title="Practicante Python")
        self.mock_repo.save.return_value = saved_job_posting

        result = self.service.create_job_posting(company_id=5, data=data)

        self.assertEqual(result, saved_job_posting)
        self.mock_repo.save.assert_called_once()
        past_job_posting = self.mock_repo.save.call_args[0][0]
        self.assertEqual(past_job_posting.company_id, 5)
        self.assertEqual(past_job_posting.title, "Practicante Python")
        self.assertEqual(past_job_posting.status, JobPosting.STATUS_DRAFT)

    def test_publish_missing_job_posting_raises(self):
        self.mock_repo.find_by_id.return_value = None

        with self.assertRaises(ValueError) as ctx:
            self.service.publish(company_id=1, job_posting_id=99)
        self.assertIn("Convocatoria no encontrada", str(ctx.exception))
        self.mock_repo.save.assert_not_called()

    def test_publish_other_company_job_posting_raises(self):
        job_posting = JobPosting(id=10, company_id=2, status=JobPosting.STATUS_DRAFT)
        self.mock_repo.find_by_id.return_value = job_posting

        with self.assertRaises(ValueError) as ctx:
            self.service.publish(company_id=1, job_posting_id=10)
        self.assertIn("La convocatoria no pertenece a esta empresa", str(ctx.exception))
        self.mock_repo.save.assert_not_called()

    def test_publish_success_changes_to_published_and_saves(self):
        job_posting = JobPosting(id=10, company_id=1, status=JobPosting.STATUS_DRAFT)
        self.mock_repo.find_by_id.return_value = job_posting
        self.mock_repo.save.return_value = job_posting

        result = self.service.publish(company_id=1, job_posting_id=10)

        self.assertEqual(result.status, JobPosting.STATUS_PUBLISHED)
        self.mock_repo.find_by_id.assert_called_once_with(10)
        self.mock_repo.save.assert_called_once_with(job_posting)

    def test_update_changes_fields_and_saves(self):
        job_posting = JobPosting(
            id=10,
            company_id=1,
            title="Original",
            description="Desc",
            status=JobPosting.STATUS_DRAFT,
        )
        self.mock_repo.find_by_id.return_value = job_posting
        self.mock_repo.save.return_value = job_posting

        new_data = {
            "titulo": "Titulo Actualizado",
            "descripcion": "Desc Nueva",
            "habilidades_requeridas": ["FastAPI"],
            "beneficios": ["Seguro EPS"],
        }
        result = self.service.update(company_id=1, job_posting_id=10, data=new_data)

        self.assertEqual(result.title, "Titulo Actualizado")
        self.assertEqual(result.description, "Desc Nueva")
        self.assertEqual(result.required_skills, ["FastAPI"])
        self.assertEqual(result.benefits, ["Seguro EPS"])
        self.mock_repo.save.assert_called_once_with(job_posting)

    def test_find_owned_raises_if_missing_or_not_owned_by_company(self):
        # Case 1: it does not exist
        self.mock_repo.find_by_id.return_value = None
        with self.assertRaises(ValueError) as ctx:
            self.service.update(company_id=1, job_posting_id=99, data={})
        self.assertIn("Convocatoria no encontrada", str(ctx.exception))

        # Case 2: it belongs to another company
        foreign_job_posting = JobPosting(id=50, company_id=999)
        self.mock_repo.find_by_id.return_value = foreign_job_posting
        with self.assertRaises(ValueError) as ctx2:
            self.service.update(company_id=1, job_posting_id=50, data={})
        self.assertIn("La convocatoria no pertenece a esta empresa", str(ctx2.exception))

    def test_close_and_reopen_full_flow(self):
        job_posting = JobPosting(id=10, company_id=1, status=JobPosting.STATUS_PUBLISHED)
        self.mock_repo.find_by_id.return_value = job_posting
        self.mock_repo.save.return_value = job_posting

        # Close
        closed = self.service.close(company_id=1, job_posting_id=10)
        self.assertEqual(closed.status, JobPosting.STATUS_CLOSED)
        self.mock_repo.save.assert_called_with(job_posting)

        # Reopen
        reopened = self.service.reopen(company_id=1, job_posting_id=10)
        self.assertEqual(reopened.status, JobPosting.STATUS_PUBLISHED)
        self.mock_repo.save.assert_called_with(job_posting)

    def test_duplicate_job_posting(self):
        original = JobPosting(
            id=10,
            company_id=1,
            title="Practicante Mobile",
            description="Flutter dev",
            required_skills=["Dart", "Flutter"],
            benefits=["Capacitaciones"],
            status=JobPosting.STATUS_PUBLISHED,
        )
        self.mock_repo.find_by_id.return_value = original
        duplicated = JobPosting(id=11, company_id=1, title="Copia de Practicante Mobile")
        self.mock_repo.save.return_value = duplicated

        result = self.service.duplicate(company_id=1, job_posting_id=10)

        self.assertEqual(result.id, 11)
        self.assertEqual(result.title, "Copia de Practicante Mobile")
        self.mock_repo.save.assert_called_once()
        created_job_posting = self.mock_repo.save.call_args[0][0]
        self.assertEqual(created_job_posting.title, "Copia de Practicante Mobile")
        self.assertEqual(created_job_posting.description, "Flutter dev")
        self.assertEqual(created_job_posting.required_skills, ["Dart", "Flutter"])
        self.assertEqual(created_job_posting.benefits, ["Capacitaciones"])
        self.assertEqual(created_job_posting.status, JobPosting.STATUS_DRAFT)

    def test_delete_in_draft_succeeds(self):
        job_posting = JobPosting(id=10, company_id=1, status=JobPosting.STATUS_DRAFT)
        self.mock_repo.find_by_id.return_value = job_posting
        self.mock_repo.delete.return_value = True

        deleted = self.service.delete(company_id=1, job_posting_id=10)

        self.assertEqual(deleted, job_posting)
        self.mock_repo.delete.assert_called_once_with(10)

    def test_delete_fails_if_repo_returns_false(self):
        job_posting = JobPosting(id=10, company_id=1, status=JobPosting.STATUS_DRAFT)
        self.mock_repo.find_by_id.return_value = job_posting
        self.mock_repo.delete.return_value = False

        with self.assertRaises(ValueError) as ctx:
            self.service.delete(company_id=1, job_posting_id=10)
        self.assertIn("Convocatoria no encontrada", str(ctx.exception))

    def test_search_delegates_query_and_status(self):
        expected_list = [JobPosting(id=1), JobPosting(id=2)]
        self.mock_repo.search.return_value = expected_list

        result = self.service.search(query="Python", status="publicada")

        self.assertEqual(result, expected_list)
        self.mock_repo.search.assert_called_once_with(query="Python", status="publicada")

    def test_find_by_id_existing_and_missing(self):
        job_posting = JobPosting(id=5, company_id=1)
        self.mock_repo.find_by_id.return_value = job_posting

        # Existing
        result = self.service.find_by_id(5)
        self.assertEqual(result, job_posting)
        self.mock_repo.find_by_id.assert_called_once_with(5)

        # Missing
        self.mock_repo.find_by_id.return_value = None
        with self.assertRaises(ValueError) as ctx:
            self.service.find_by_id(99)
        self.assertIn("Convocatoria no encontrada", str(ctx.exception))

    def test_list_for_company_delegates_to_repository(self):
        company_list = [JobPosting(id=1, company_id=3)]
        self.mock_repo.find_by_company_id.return_value = company_list

        result = self.service.list_for_company(company_id=3)

        self.assertEqual(result, company_list)
        self.mock_repo.find_by_company_id.assert_called_once_with(3)
