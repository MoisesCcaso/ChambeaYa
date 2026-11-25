"""Domain unit tests for JobPosting, JobPostingFactory and JobApplication."""

import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from recruitment.domain.job_posting import JobPosting
from recruitment.domain.job_posting_factory import JobPostingFactory
from recruitment.domain.job_application import JobApplication
from recruitment.domain.job_posting_state import DraftState, ClosedState, PublishedState


class TestJobPostingDomain(unittest.TestCase):
    """Lifecycle and business rule tests for JobPosting."""

    def setUp(self):
        self.job_posting = JobPosting(
            id=1,
            company_id=10,
            title="Practicante Backend Python",
            description="Desarrollo de APIs REST",
            status=JobPosting.STATUS_DRAFT,
            required_skills=["Python", "SQLAlchemy"],
            benefits=["Seguro", "Remoto"],
        )

    def test_only_the_closed_state_has_a_closing_date(self):
        now_value = datetime(2026, 11, 1, tzinfo=timezone.utc)
        self.assertIsNone(DraftState().closing_date)
        self.assertIsNone(PublishedState().closing_date)
        self.assertEqual(ClosedState(now_value).closing_date, now_value)

    def test_closing_date_only_exists_while_the_job_posting_is_closed(self):
        self.assertIsNone(self.job_posting.closing_date)
        self.job_posting.publish()
        self.assertIsNone(self.job_posting.closing_date)
        self.job_posting.close()
        self.assertIsNotNone(self.job_posting.closing_date)
        self.job_posting.reopen()
        self.assertIsNone(self.job_posting.closing_date)

    def test_constructor_with_closed_status_keeps_its_closing_date(self):
        moment = datetime(2026, 11, 1, tzinfo=timezone.utc)
        job_posting = JobPosting(status=JobPosting.STATUS_CLOSED, closing_date=moment)
        self.assertEqual(job_posting.status, JobPosting.STATUS_CLOSED)
        self.assertEqual(job_posting.closing_date, moment)

    def test_publish_from_draft_sets_status_and_utc_date(self):
        fixed_date = datetime(2026, 10, 28, 12, 0, 0, tzinfo=timezone.utc)
        with patch("recruitment.domain.job_posting.datetime") as mock_dt:
            mock_dt.now.return_value = fixed_date
            result = self.job_posting.publish()

        self.assertIs(result, self.job_posting)
        self.assertEqual(self.job_posting.status, JobPosting.STATUS_PUBLISHED)
        self.assertEqual(self.job_posting.published_at, fixed_date)

    def test_publish_outside_draft_raises(self):
        self.job_posting.status = JobPosting.STATUS_PUBLISHED
        with self.assertRaises(ValueError) as ctx:
            self.job_posting.publish()
        self.assertIn("Solo una convocatoria en borrador puede publicarse", str(ctx.exception))

        self.job_posting.status = JobPosting.STATUS_CLOSED
        with self.assertRaises(ValueError):
            self.job_posting.publish()

    def test_close_from_published_sets_status_and_closing_date(self):
        self.job_posting.status = JobPosting.STATUS_PUBLISHED
        closing_date = datetime(2026, 11, 1, 18, 0, 0, tzinfo=timezone.utc)
        with patch("recruitment.domain.job_posting.datetime") as mock_dt:
            mock_dt.now.return_value = closing_date
            result = self.job_posting.close()

        self.assertIs(result, self.job_posting)
        self.assertEqual(self.job_posting.status, JobPosting.STATUS_CLOSED)
        self.assertEqual(self.job_posting.closing_date, closing_date)

    def test_close_from_unpublished_status_raises(self):
        self.job_posting.status = JobPosting.STATUS_DRAFT
        with self.assertRaises(ValueError) as ctx:
            self.job_posting.close()
        self.assertIn("Solo una convocatoria publicada puede cerrarse", str(ctx.exception))

        self.job_posting.status = JobPosting.STATUS_CLOSED
        with self.assertRaises(ValueError):
            self.job_posting.close()

    def test_reopen_from_closed_sets_published_and_clears_closing(self):
        self.job_posting = JobPosting(
            status=JobPosting.STATUS_CLOSED,
            closing_date=datetime(2026, 11, 1, tzinfo=timezone.utc),
        )
        reopened_at = datetime(2026, 11, 5, 10, 0, 0, tzinfo=timezone.utc)

        with patch("recruitment.domain.job_posting.datetime") as mock_dt:
            mock_dt.now.return_value = reopened_at
            result = self.job_posting.reopen()

        self.assertIs(result, self.job_posting)
        self.assertEqual(self.job_posting.status, JobPosting.STATUS_PUBLISHED)
        self.assertEqual(self.job_posting.published_at, reopened_at)
        self.assertIsNone(self.job_posting.closing_date)

    def test_reopen_from_non_closed_status_raises(self):
        self.job_posting.status = JobPosting.STATUS_DRAFT
        with self.assertRaises(ValueError) as ctx:
            self.job_posting.reopen()
        self.assertIn("Solo una convocatoria cerrada puede reabrirse", str(ctx.exception))

        self.job_posting.status = JobPosting.STATUS_PUBLISHED
        with self.assertRaises(ValueError):
            self.job_posting.reopen()

    def test_update_in_draft_changes_fields_and_normalizes_texts(self):
        result = self.job_posting.update(
            title="  Nuevo Título Backend  ",
            description="  Nueva descripción  ",
            required_skills=["  Python  ", "Docker", "Python"],
            benefits=["  Home Office  ", "Bono", None],
        )

        self.assertIs(result, self.job_posting)
        self.assertEqual(self.job_posting.title, "Nuevo Título Backend")
        self.assertEqual(self.job_posting.description, "Nueva descripción")
        self.assertEqual(self.job_posting.required_skills, ["Python", "Docker"])
        self.assertEqual(self.job_posting.benefits, ["Home Office", "Bono"])

    def test_update_outside_draft_raises(self):
        self.job_posting.status = JobPosting.STATUS_PUBLISHED
        with self.assertRaises(ValueError) as ctx:
            self.job_posting.update(title="Intento")
        self.assertIn("Solo una convocatoria en borrador puede editarse", str(ctx.exception))

    def test_update_with_empty_title_raises(self):
        with self.assertRaises(ValueError) as ctx:
            self.job_posting.update(title="   ")
        self.assertIn("El título es obligatorio", str(ctx.exception))

    def test_update_with_invalid_lists_raises(self):
        with self.assertRaises(ValueError) as ctx:
            self.job_posting.update(required_skills="no es lista")
        self.assertIn("Las habilidades requeridas deben ser una lista", str(ctx.exception))

        with self.assertRaises(ValueError) as ctx2:
            self.job_posting.update(benefits="no es lista")
        self.assertIn("Los beneficios deben ser una lista", str(ctx2.exception))

    def test_validate_deletion_in_draft_returns_self(self):
        self.job_posting.status = JobPosting.STATUS_DRAFT
        self.assertIs(self.job_posting.validate_deletion(), self.job_posting)

    def test_validate_deletion_outside_draft_raises(self):
        for status in [JobPosting.STATUS_PUBLISHED, JobPosting.STATUS_CLOSED]:
            self.job_posting.status = status
            with self.assertRaises(ValueError) as ctx:
                self.job_posting.validate_deletion()
            self.assertIn("Solo una convocatoria en borrador puede eliminarse", str(ctx.exception))


class TestJobPostingFactory(unittest.TestCase):
    """Tests for the JobPostingFactory."""

    def setUp(self):
        self.factory = JobPostingFactory()

    def test_create_job_posting_with_valid_data(self):
        job_posting = self.factory.create_job_posting(
            company_id=42,
            title="  Practicante Fullstack  ",
            required_skills=[" React ", " Node "],
            description="  Búsqueda de practicante proactivo  ",
            benefits=["  Almuerzo  "],
        )

        self.assertEqual(job_posting.company_id, 42)
        self.assertEqual(job_posting.title, "Practicante Fullstack")
        self.assertEqual(job_posting.description, "Búsqueda de practicante proactivo")
        self.assertEqual(job_posting.status, JobPosting.STATUS_DRAFT)
        self.assertEqual(job_posting.required_skills, ["React", "Node"])
        self.assertEqual(job_posting.benefits, ["Almuerzo"])

    def test_create_job_posting_without_company_raises(self):
        with self.assertRaises(ValueError) as ctx:
            self.factory.create_job_posting(company_id=None, title="Titulo Valido")
        self.assertIn("La empresa es obligatoria", str(ctx.exception))

    def test_create_job_posting_without_or_with_empty_title_raises(self):
        with self.assertRaises(ValueError) as ctx:
            self.factory.create_job_posting(company_id=1, title="   ")
        self.assertIn("El título es obligatorio", str(ctx.exception))

    def test_create_job_posting_with_invalid_list_types_raises(self):
        with self.assertRaises(ValueError) as ctx:
            self.factory.create_job_posting(
                company_id=1, title="Valido", required_skills="string_no_lista"
            )
        self.assertIn("Las habilidades requeridas deben ser una lista", str(ctx.exception))

        with self.assertRaises(ValueError) as ctx2:
            self.factory.create_job_posting(
                company_id=1, title="Valido", benefits="string_no_lista"
            )
        self.assertIn("Los beneficios deben ser una lista", str(ctx2.exception))


class TestJobApplicationDomain(unittest.TestCase):
    """Lifecycle and business rule tests for JobApplication."""

    def setUp(self):
        self.job_application = JobApplication(
            id=10,
            job_posting_id=100,
            intern_id=200,
            status=JobApplication.STATUS_PENDING,
        )

    def test_default_initial_status_is_pending(self):
        job_application = JobApplication(id=1, job_posting_id=2, intern_id=3)
        self.assertEqual(job_application.status, JobApplication.STATUS_PENDING)

    def test_select_from_pending_changes_to_selected(self):
        result = self.job_application.select()
        self.assertIs(result, self.job_application)
        self.assertEqual(self.job_application.status, JobApplication.STATUS_SELECTED)

    def test_reject_from_pending_changes_to_rejected(self):
        result = self.job_application.reject()
        self.assertIs(result, self.job_application)
        self.assertEqual(self.job_application.status, JobApplication.STATUS_REJECTED)

    def test_cancel_from_pending_changes_to_cancelled(self):
        result = self.job_application.cancel()
        self.assertIs(result, self.job_application)
        self.assertEqual(self.job_application.status, JobApplication.STATUS_CANCELLED)

    def test_reactivate_from_cancelled_changes_to_pending(self):
        self.job_application.status = JobApplication.STATUS_CANCELLED
        result = self.job_application.reactivate()
        self.assertIs(result, self.job_application)
        self.assertEqual(self.job_application.status, JobApplication.STATUS_PENDING)

    def test_reactivate_from_non_cancelled_status_raises(self):
        for status in [JobApplication.STATUS_PENDING, JobApplication.STATUS_SELECTED, JobApplication.STATUS_REJECTED]:
            self.job_application.status = status
            with self.assertRaises(ValueError) as ctx:
                self.job_application.reactivate()
            self.assertIn("Solo una postulación retirada puede reactivarse", str(ctx.exception))

    def test_reconsider_from_selected_or_rejected_changes_to_pending(self):
        for status in [JobApplication.STATUS_SELECTED, JobApplication.STATUS_REJECTED]:
            self.job_application.status = status
            result = self.job_application.reconsider()
            self.assertIs(result, self.job_application)
            self.assertEqual(self.job_application.status, JobApplication.STATUS_PENDING)

    def test_reconsider_from_invalid_status_raises(self):
        for status in [JobApplication.STATUS_PENDING, JobApplication.STATUS_CANCELLED]:
            self.job_application.status = status
            with self.assertRaises(ValueError) as ctx:
                self.job_application.reconsider()
            self.assertIn("Solo una postulación seleccionada o rechazada puede reconsiderarse", str(ctx.exception))

    def test_invalid_transitions_from_non_pending_raise(self):
        non_pending_statuses = [
            JobApplication.STATUS_SELECTED,
            JobApplication.STATUS_REJECTED,
            JobApplication.STATUS_CANCELLED,
        ]
        for status in non_pending_statuses:
            self.job_application.status = status
            with self.assertRaises(ValueError):
                self.job_application.select()
            with self.assertRaises(ValueError):
                self.job_application.reject()
            with self.assertRaises(ValueError):
                self.job_application.cancel()
