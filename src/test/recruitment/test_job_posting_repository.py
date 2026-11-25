"""Persistence and query tests for SqlAlchemyJobPostingRepository."""

import unittest
from datetime import datetime, timezone

from recruitment.domain.job_posting import JobPosting
from bootstrap.app import create_app
from shared.database import db
from profiles.infrastructure.models.company_model import CompanyModel
from identity.infrastructure.models.user_model import UserModel
from recruitment.infrastructure.sqlalchemy_job_posting_repository import SqlAlchemyJobPostingRepository


class TestJobPostingRepository(unittest.TestCase):
    """Job posting repository tests with in-memory SQLite, no doubles."""

    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.repository = SqlAlchemyJobPostingRepository()

        # Create base companies to satisfy referential integrity (FK)
        self.company_1 = self._create_company_in_db(email="empresa1@test.com", ruc="20123456789")
        self.company_2 = self._create_company_in_db(email="empresa2@test.com", ruc="20987654321")

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def _create_company_in_db(self, email, ruc):
        user = UserModel(
            email=email,
            password_hash="hash_test",
            role="empresa",
            status="activo",
        )
        db.session.add(user)
        db.session.flush()

        company = CompanyModel(
            user_id=user.id,
            legal_name="Empresa Test",
            ruc=ruc,
            verified=True,
        )
        db.session.add(company)
        db.session.commit()
        return company

    def test_save_creates_new_job_posting_and_assigns_id(self):
        job_posting = JobPosting(
            company_id=self.company_1.id,
            title="Practicante Python",
            description="Desarrollo backend con Flask",
            status=JobPosting.STATUS_DRAFT,
            required_skills=["Python", "SQLAlchemy"],
            benefits=["Seguro", "Remoto"],
            published_at=None,
            closing_date=None,
        )

        saved = self.repository.save(job_posting)

        self.assertIsNotNone(saved.id)
        self.assertEqual(saved.company_id, self.company_1.id)
        self.assertEqual(saved.title, "Practicante Python")
        self.assertEqual(saved.description, "Desarrollo backend con Flask")
        self.assertEqual(saved.status, JobPosting.STATUS_DRAFT)
        self.assertEqual(saved.required_skills, ["Python", "SQLAlchemy"])
        self.assertEqual(saved.benefits, ["Seguro", "Remoto"])

    def test_save_updates_existing_job_posting(self):
        job_posting = JobPosting(
            company_id=self.company_1.id,
            title="Practicante QA",
            description="Pruebas de software",
            status=JobPosting.STATUS_DRAFT,
            required_skills=["Pytest"],
            benefits=["Capacitación"],
        )
        saved = self.repository.save(job_posting)

        saved.title = "Practicante QA Automation"
        saved.status = JobPosting.STATUS_PUBLISHED
        saved.published_at = datetime(2026, 10, 28, 12, 0, 0, tzinfo=timezone.utc)
        saved.required_skills = ["Pytest", "Selenium"]

        updated = self.repository.save(saved)

        self.assertEqual(updated.id, saved.id)
        self.assertEqual(updated.title, "Practicante QA Automation")
        self.assertEqual(updated.status, JobPosting.STATUS_PUBLISHED)
        self.assertEqual(updated.required_skills, ["Pytest", "Selenium"])

    def test_find_by_id_existing_and_missing(self):
        job_posting = JobPosting(
            company_id=self.company_1.id,
            title="Practicante Frontend",
            description="React UI",
            status=JobPosting.STATUS_PUBLISHED,
            required_skills=["React"],
            benefits=["Remoto"],
        )
        saved = self.repository.save(job_posting)

        reloaded = self.repository.find_by_id(saved.id)
        self.assertIsNotNone(reloaded)
        self.assertEqual(reloaded.id, saved.id)
        self.assertEqual(reloaded.title, "Practicante Frontend")
        self.assertEqual(reloaded.required_skills, ["React"])

        self.assertIsNone(self.repository.find_by_id(99999))

    def test_find_all_and_find_by_company_id(self):
        c1 = JobPosting(company_id=self.company_1.id, title="Dev Ops", status=JobPosting.STATUS_DRAFT)
        c2 = JobPosting(company_id=self.company_1.id, title="Data Analyst", status=JobPosting.STATUS_PUBLISHED)
        c3 = JobPosting(company_id=self.company_2.id, title="Mobile Dev", status=JobPosting.STATUS_DRAFT)

        self.repository.save(c1)
        self.repository.save(c2)
        self.repository.save(c3)

        all_items = self.repository.find_all()
        self.assertEqual(len(all_items), 3)

        from_company_1 = self.repository.find_by_company_id(self.company_1.id)
        self.assertEqual(len(from_company_1), 2)
        company_1_titles = {c.title for c in from_company_1}
        self.assertEqual(company_1_titles, {"Dev Ops", "Data Analyst"})

        from_empty_company = self.repository.find_by_company_id(99999)
        self.assertEqual(from_empty_company, [])

    def test_delete_existing_returns_true_and_missing_returns_false(self):
        job_posting = JobPosting(
            company_id=self.company_1.id,
            title="Temporal",
            status=JobPosting.STATUS_DRAFT,
        )
        saved = self.repository.save(job_posting)

        deleted_ok = self.repository.delete(saved.id)
        self.assertTrue(deleted_ok)
        self.assertIsNone(self.repository.find_by_id(saved.id))

        missing_deleted = self.repository.delete(99999)
        self.assertFalse(missing_deleted)

    def test_search_by_status_and_text_match(self):
        c1 = JobPosting(
            company_id=self.company_1.id,
            title="Desarrollador Django",
            description="Backend robusto",
            status=JobPosting.STATUS_PUBLISHED,
            required_skills=["Python", "Django"],
        )
        c2 = JobPosting(
            company_id=self.company_1.id,
            title="Desarrollador React",
            description="Frontend con Next.js",
            status=JobPosting.STATUS_PUBLISHED,
            required_skills=["JavaScript", "React"],
        )
        c3 = JobPosting(
            company_id=self.company_2.id,
            title="Ingeniero Django Borrador",
            description="En revisión",
            status=JobPosting.STATUS_DRAFT,
            required_skills=["Django"],
        )
        self.repository.save(c1)
        self.repository.save(c2)
        self.repository.save(c3)

        # Filter by status
        published = self.repository.search(status=JobPosting.STATUS_PUBLISHED)
        self.assertEqual(len(published), 2)

        # Filter by text in the title
        django_results = self.repository.search(query="Django")
        self.assertEqual(len(django_results), 2)

        # Combined filter (query and status)
        published_django = self.repository.search(query="Django", status=JobPosting.STATUS_PUBLISHED)
        self.assertEqual(len(published_django), 1)
        self.assertEqual(published_django[0].title, "Desarrollador Django")

        # Filter by required skill
        react_results = self.repository.search(query="React")
        self.assertEqual(len(react_results), 1)
        self.assertEqual(react_results[0].title, "Desarrollador React")

    def test_load_list_edge_cases(self):
        self.assertEqual(self.repository._load_list(None), [])
        self.assertEqual(self.repository._load_list(""), [])
        self.assertEqual(self.repository._load_list("no-json-valido"), [])
        self.assertEqual(self.repository._load_list('{"objeto": "no lista"}'), [])
