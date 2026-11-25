"""Unit tests for the recruitment Parameter Objects (DTOs / Command Objects) (Issue #180)."""

import unittest
from unittest.mock import create_autospec

from recruitment.application.job_posting_application_service import JobPostingApplicationService
from recruitment.application.dtos import (
    JobPostingCommand,
)
from recruitment.domain.job_posting import JobPosting
from recruitment.domain.i_job_posting_repository import IJobPostingRepository


class TestJobPostingCommandDTO(unittest.TestCase):
    """Unit tests for the JobPostingCommand Parameter Object."""

    def setUp(self):
        self.mock_repo = create_autospec(IJobPostingRepository, instance=True)
        self.service = JobPostingApplicationService(job_posting_repository=self.mock_repo)

    def test_from_dict_builds_typed_command(self):
        cmd = JobPostingCommand.from_dict({
            "titulo": "Backend Python",
            "descripcion": "Prácticas Flask",
            "habilidades_requeridas": ["Python", "SQL"],
            "beneficios": ["Remoto"],
        })
        self.assertIsInstance(cmd, JobPostingCommand)
        self.assertEqual(cmd.title, "Backend Python")
        self.assertEqual(cmd.description, "Prácticas Flask")
        self.assertEqual(cmd.required_skills, ["Python", "SQL"])
        self.assertEqual(cmd.benefits, ["Remoto"])

    def test_from_dict_returns_same_instance_if_already_a_command(self):
        cmd = JobPostingCommand(title="QA")
        self.assertIs(JobPostingCommand.from_dict(cmd), cmd)

    def test_create_job_posting_accepts_job_posting_command(self):
        cmd = JobPostingCommand(
            title="Data Engineer",
            description="ETL pipelines",
            required_skills=["Python"],
            benefits=["Certificado"],
        )
        self.mock_repo.save.side_effect = lambda c: c

        result = self.service.create_job_posting(company_id=3, data=cmd)

        self.assertEqual(result.title, "Data Engineer")
        self.assertEqual(result.description, "ETL pipelines")
        self.assertEqual(result.required_skills, ["Python"])
        self.assertEqual(result.benefits, ["Certificado"])

    def test_update_job_posting_accepts_job_posting_command(self):
        existing = JobPosting(
            id=10,
            company_id=3,
            title="Original",
            description="Desc",
            status=JobPosting.STATUS_DRAFT,
        )
        self.mock_repo.find_by_id.return_value = existing
        self.mock_repo.save.side_effect = lambda c: c

        cmd = JobPostingCommand(
            title="Actualizado con DTO",
            description="Nueva Desc",
            required_skills=["Flask"],
            benefits=["Mentoría"],
        )
        result = self.service.update(company_id=3, job_posting_id=10, data=cmd)

        self.assertEqual(result.title, "Actualizado con DTO")
        self.assertEqual(result.required_skills, ["Flask"])


if __name__ == "__main__":
    unittest.main()
