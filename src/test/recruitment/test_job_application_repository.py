"""Persistence and query tests for SqlAlchemyJobApplicationRepository."""

import unittest

from recruitment.domain.job_application import JobApplication
from bootstrap.app import create_app
from shared.database import db
from recruitment.infrastructure.models.job_posting_model import JobPostingModel
from profiles.infrastructure.models.company_model import CompanyModel
from profiles.infrastructure.models.intern_model import InternModel
from identity.infrastructure.models.user_model import UserModel
from recruitment.infrastructure.sqlalchemy_job_application_repository import SqlAlchemyJobApplicationRepository


class TestJobApplicationRepository(unittest.TestCase):
    """Job application repository tests with in-memory SQLite, no doubles."""

    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.repository = SqlAlchemyJobApplicationRepository()

        # Prepare base entities to satisfy referential integrity (FKs)
        self.company = self._create_company(email="empresa_post@test.com", ruc="20111222333")
        self.job_posting_1 = self._create_job_posting(self.company.id, title="Backend Python")
        self.job_posting_2 = self._create_job_posting(self.company.id, title="Frontend React")

        self.intern_1 = self._create_intern(email="pract1@test.com", dni="71112233")
        self.intern_2 = self._create_intern(email="pract2@test.com", dni="72223344")

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def _create_company(self, email, ruc):
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
            legal_name="Empresa Postulaciones",
            ruc=ruc,
            verified=True,
        )
        db.session.add(company)
        db.session.commit()
        return company

    def _create_job_posting(self, company_id, title):
        job_posting = JobPostingModel(
            company_id=company_id,
            title=title,
            status="publicada",
        )
        db.session.add(job_posting)
        db.session.commit()
        return job_posting

    def _create_intern(self, email, dni):
        user = UserModel(
            email=email,
            password_hash="hash_test",
            role="practicante",
            status="activo",
        )
        db.session.add(user)
        db.session.flush()

        intern = InternModel(
            user_id=user.id,
            first_names="Juan",
            last_names="Pérez",
            dni=dni,
        )
        db.session.add(intern)
        db.session.commit()
        return intern

    def test_save_creates_new_job_application_and_assigns_id(self):
        job_application = JobApplication(
            job_posting_id=self.job_posting_1.id,
            intern_id=self.intern_1.id,
            status=JobApplication.STATUS_PENDING,
        )

        saved = self.repository.save(job_application)

        self.assertIsNotNone(saved.id)
        self.assertEqual(saved.job_posting_id, self.job_posting_1.id)
        self.assertEqual(saved.intern_id, self.intern_1.id)
        self.assertEqual(saved.status, JobApplication.STATUS_PENDING)

    def test_save_updates_existing_job_application_status(self):
        job_application = JobApplication(
            job_posting_id=self.job_posting_1.id,
            intern_id=self.intern_1.id,
            status=JobApplication.STATUS_PENDING,
        )
        saved = self.repository.save(job_application)

        saved.status = JobApplication.STATUS_SELECTED
        updated = self.repository.save(saved)

        self.assertEqual(updated.id, saved.id)
        self.assertEqual(updated.status, JobApplication.STATUS_SELECTED)

        # Confirm persistence in the database
        reloaded = self.repository.find_by_id(saved.id)
        self.assertEqual(reloaded.status, JobApplication.STATUS_SELECTED)

    def test_save_all_persists_several_applications_in_one_transaction(self):
        p1 = self.repository.save(JobApplication(
            job_posting_id=self.job_posting_1.id,
            intern_id=self.intern_1.id,
            status=JobApplication.STATUS_PENDING,
        ))
        p2 = self.repository.save(JobApplication(
            job_posting_id=self.job_posting_1.id,
            intern_id=self.intern_2.id,
            status=JobApplication.STATUS_PENDING,
        ))
        p1.status = JobApplication.STATUS_SELECTED
        p2.status = JobApplication.STATUS_REJECTED

        saved_items = self.repository.save_all([p1, p2])

        self.assertEqual([g.status for g in saved_items], ["seleccionada", "rechazada"])
        self.assertEqual(self.repository.find_by_id(p1.id).status, JobApplication.STATUS_SELECTED)
        self.assertEqual(self.repository.find_by_id(p2.id).status, JobApplication.STATUS_REJECTED)

    def test_save_all_rolls_back_if_commit_fails(self):
        p1 = self.repository.save(JobApplication(
            job_posting_id=self.job_posting_1.id,
            intern_id=self.intern_1.id,
            status=JobApplication.STATUS_PENDING,
        ))
        p1.status = JobApplication.STATUS_SELECTED
        invalid = JobApplication(
            job_posting_id=99999,
            intern_id=self.intern_2.id,
            status=JobApplication.STATUS_PENDING,
        )

        with self.assertRaises(Exception):
            self.repository.save_all([p1, invalid])

        self.assertEqual(self.repository.find_by_id(p1.id).status, JobApplication.STATUS_PENDING)

    def test_find_by_id_existing_and_missing(self):
        job_application = JobApplication(
            job_posting_id=self.job_posting_1.id,
            intern_id=self.intern_1.id,
            status=JobApplication.STATUS_PENDING,
        )
        saved = self.repository.save(job_application)

        reloaded = self.repository.find_by_id(saved.id)
        self.assertIsNotNone(reloaded)
        self.assertEqual(reloaded.id, saved.id)
        self.assertEqual(reloaded.job_posting_id, self.job_posting_1.id)
        self.assertEqual(reloaded.intern_id, self.intern_1.id)

        self.assertIsNone(self.repository.find_by_id(99999))

    def test_find_by_intern_id(self):
        p1 = JobApplication(
            job_posting_id=self.job_posting_1.id,
            intern_id=self.intern_1.id,
        )
        p2 = JobApplication(
            job_posting_id=self.job_posting_2.id,
            intern_id=self.intern_1.id,
        )
        p3 = JobApplication(
            job_posting_id=self.job_posting_1.id,
            intern_id=self.intern_2.id,
        )
        self.repository.save(p1)
        self.repository.save(p2)
        self.repository.save(p3)

        applications_intern1 = self.repository.find_by_intern_id(self.intern_1.id)
        self.assertEqual(len(applications_intern1), 2)
        job_postings_intern1 = {p.job_posting_id for p in applications_intern1}
        self.assertEqual(job_postings_intern1, {self.job_posting_1.id, self.job_posting_2.id})

        empty_applications = self.repository.find_by_intern_id(99999)
        self.assertEqual(empty_applications, [])

    def test_find_by_job_posting_id(self):
        p1 = JobApplication(
            job_posting_id=self.job_posting_1.id,
            intern_id=self.intern_1.id,
        )
        p2 = JobApplication(
            job_posting_id=self.job_posting_1.id,
            intern_id=self.intern_2.id,
        )
        self.repository.save(p1)
        self.repository.save(p2)

        applications_posting1 = self.repository.find_by_job_posting_id(self.job_posting_1.id)
        self.assertEqual(len(applications_posting1), 2)

        empty_applications = self.repository.find_by_job_posting_id(99999)
        self.assertEqual(empty_applications, [])

    def test_find_by_job_posting_and_intern(self):
        job_application = JobApplication(
            job_posting_id=self.job_posting_1.id,
            intern_id=self.intern_1.id,
            status=JobApplication.STATUS_PENDING,
        )
        self.repository.save(job_application)

        found = self.repository.find_by_job_posting_and_intern(
            self.job_posting_1.id, self.intern_1.id
        )
        self.assertIsNotNone(found)
        self.assertEqual(found.job_posting_id, self.job_posting_1.id)
        self.assertEqual(found.intern_id, self.intern_1.id)

        missing = self.repository.find_by_job_posting_and_intern(
            self.job_posting_2.id, self.intern_1.id
        )
        self.assertIsNone(missing)

    def test_to_job_application_domain_with_none(self):
        self.assertIsNone(self.repository._to_job_application_domain(None))
