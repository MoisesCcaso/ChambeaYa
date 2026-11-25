"""Unit tests for JobApplicationService with doubles."""

import unittest
from unittest.mock import MagicMock, create_autospec

from recruitment.application.job_application_service import (
    INTERN_PROFILE_NOT_FOUND,
    JobApplicationService,
)
from recruitment.domain.job_posting import JobPosting
from recruitment.domain.i_job_posting_repository import IJobPostingRepository
from recruitment.domain.i_job_application_repository import IJobApplicationRepository
from recruitment.domain.job_application import JobApplication
from profiles.domain.i_intern_repository import IInternRepository
from internships.domain.i_internship_repository import IInternshipRepository
from shared.error_messages import JOB_POSTING_NOT_FOUND, JOB_APPLICATION_NOT_FOUND


class TestJobApplicationService(unittest.TestCase):
    """Isolated tests for the job application service using autospec on its segregated repositories (ISP)."""

    def setUp(self):
        self.mock_job_application_repo = create_autospec(IJobApplicationRepository, instance=True)
        self.mock_job_posting_repo = create_autospec(IJobPostingRepository, instance=True)
        self.mock_profile_repo = create_autospec(IInternRepository, instance=True)
        self.mock_internship_repo = create_autospec(IInternshipRepository, instance=True)

        self.service = JobApplicationService(
            job_application_repository=self.mock_job_application_repo,
            job_posting_repository=self.mock_job_posting_repo,
            intern_repository=self.mock_profile_repo,
            internship_repository=self.mock_internship_repo,
        )

    def test_require_repositories_raises_if_any_is_missing(self):
        incomplete_services = [
            JobApplicationService(None, self.mock_job_posting_repo, self.mock_profile_repo, self.mock_internship_repo),
            JobApplicationService(self.mock_job_application_repo, None, self.mock_profile_repo, self.mock_internship_repo),
            JobApplicationService(self.mock_job_application_repo, self.mock_job_posting_repo, None, self.mock_internship_repo),
            JobApplicationService(self.mock_job_application_repo, self.mock_job_posting_repo, self.mock_profile_repo, None),
        ]

        for s in incomplete_services:
            with self.assertRaises(RuntimeError) as ctx:
                s.apply(user_id=1, job_posting_id=10)
            self.assertIn("requires all of its repositories", str(ctx.exception))

            with self.assertRaises(RuntimeError):
                s.list_for_intern(1)

            with self.assertRaises(RuntimeError):
                s.list_for_job_posting(1, 10)

            with self.assertRaises(RuntimeError):
                s.select_candidate(1, 100)

            with self.assertRaises(RuntimeError):
                s.reject_candidate(1, 100)

            with self.assertRaises(RuntimeError):
                s.cancel(1, 100)

            with self.assertRaises(RuntimeError):
                s.reconsider_candidate(1, 100)

    # ------------------- apply tests -------------------

    def test_intern_profile_not_found_constant(self):
        self.assertEqual(INTERN_PROFILE_NOT_FOUND, "Perfil de practicante no encontrado")

    def test_apply_intern_profile_not_found(self):
        self.mock_profile_repo.find_intern_by_user_id.return_value = None

        with self.assertRaises(ValueError) as ctx:
            self.service.apply(user_id=1, job_posting_id=10)
        self.assertEqual(str(ctx.exception), INTERN_PROFILE_NOT_FOUND)

    def test_apply_with_incomplete_profile_without_names(self):
        intern_without_first_names = MagicMock(first_names="", last_names="Perez")
        self.mock_profile_repo.find_intern_by_user_id.return_value = intern_without_first_names

        with self.assertRaises(ValueError) as ctx:
            self.service.apply(user_id=1, job_posting_id=10)
        self.assertIn("Completa tus nombres y apellidos antes de postular", str(ctx.exception))

        intern_without_last_names = MagicMock(first_names="Juan", last_names="")
        self.mock_profile_repo.find_intern_by_user_id.return_value = intern_without_last_names

        with self.assertRaises(ValueError) as ctx2:
            self.service.apply(user_id=1, job_posting_id=10)
        self.assertIn("Completa tus nombres y apellidos antes de postular", str(ctx2.exception))

    def test_apply_job_posting_not_found(self):
        intern = MagicMock(id=5, first_names="Juan", last_names="Perez")
        self.mock_profile_repo.find_intern_by_user_id.return_value = intern
        self.mock_job_posting_repo.find_by_id.return_value = None

        with self.assertRaises(ValueError) as ctx:
            self.service.apply(user_id=1, job_posting_id=99)
        self.assertIn("Convocatoria no encontrada", str(ctx.exception))

    def test_apply_to_unpublished_job_posting_raises(self):
        intern = MagicMock(id=5, first_names="Juan", last_names="Perez")
        self.mock_profile_repo.find_intern_by_user_id.return_value = intern
        draft_job_posting = JobPosting(id=10, status=JobPosting.STATUS_DRAFT)
        self.mock_job_posting_repo.find_by_id.return_value = draft_job_posting

        with self.assertRaises(ValueError) as ctx:
            self.service.apply(user_id=1, job_posting_id=10)
        self.assertIn("Solo se puede postular a convocatorias publicadas", str(ctx.exception))

    def test_apply_existing_active_application_raises(self):
        intern = MagicMock(id=5, first_names="Juan", last_names="Perez")
        self.mock_profile_repo.find_intern_by_user_id.return_value = intern
        job_posting = JobPosting(id=10, status=JobPosting.STATUS_PUBLISHED)
        self.mock_job_posting_repo.find_by_id.return_value = job_posting

        existing = JobApplication(id=1, job_posting_id=10, intern_id=5, status=JobApplication.STATUS_PENDING)
        self.mock_job_application_repo.find_by_job_posting_and_intern.return_value = existing

        with self.assertRaises(ValueError) as ctx:
            self.service.apply(user_id=1, job_posting_id=10)
        self.assertIn("Ya existe una postulación para esta convocatoria", str(ctx.exception))

    def test_apply_existing_cancelled_application_is_reactivated_and_saved(self):
        intern = MagicMock(id=5, first_names="Juan", last_names="Perez")
        self.mock_profile_repo.find_intern_by_user_id.return_value = intern
        job_posting = JobPosting(id=10, status=JobPosting.STATUS_PUBLISHED)
        self.mock_job_posting_repo.find_by_id.return_value = job_posting

        cancelled_existing = JobApplication(id=1, job_posting_id=10, intern_id=5, status=JobApplication.STATUS_CANCELLED)
        self.mock_job_application_repo.find_by_job_posting_and_intern.return_value = cancelled_existing
        self.mock_job_application_repo.save.return_value = cancelled_existing

        result = self.service.apply(user_id=1, job_posting_id=10)

        self.assertEqual(result.status, JobApplication.STATUS_PENDING)
        self.mock_job_application_repo.save.assert_called_once_with(cancelled_existing)

    def test_apply_new_job_application_succeeds(self):
        intern = MagicMock(id=5, first_names="Juan", last_names="Perez")
        self.mock_profile_repo.find_intern_by_user_id.return_value = intern
        job_posting = JobPosting(id=10, status=JobPosting.STATUS_PUBLISHED)
        self.mock_job_posting_repo.find_by_id.return_value = job_posting
        self.mock_job_application_repo.find_by_job_posting_and_intern.return_value = None

        saved = JobApplication(id=20, job_posting_id=10, intern_id=5, status=JobApplication.STATUS_PENDING)
        self.mock_job_application_repo.save.return_value = saved

        result = self.service.apply(user_id=1, job_posting_id=10)

        self.assertEqual(result, saved)
        self.mock_job_application_repo.save.assert_called_once()
        created_application = self.mock_job_application_repo.save.call_args[0][0]
        self.assertEqual(created_application.job_posting_id, 10)
        self.assertEqual(created_application.intern_id, 5)

    # ------------------- listing tests -------------------

    def test_list_for_intern(self):
        intern = MagicMock(id=5)
        self.mock_profile_repo.find_intern_by_user_id.return_value = intern

        p1 = JobApplication(id=1, job_posting_id=100, intern_id=5)
        p2 = JobApplication(id=2, job_posting_id=101, intern_id=5)
        self.mock_job_application_repo.find_by_intern_id.return_value = [p1, p2]

        c1 = JobPosting(id=100, title="Convo 100")
        c2 = JobPosting(id=101, title="Convo 101")
        self.mock_job_posting_repo.find_by_id.side_effect = lambda cid: c1 if cid == 100 else c2

        result = self.service.list_for_intern(user_id=2)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], (p1, c1))
        self.assertEqual(result[1], (p2, c2))

    def test_list_for_intern_without_profile_raises(self):
        self.mock_profile_repo.find_intern_by_user_id.return_value = None
        with self.assertRaises(ValueError) as ctx:
            self.service.list_for_intern(user_id=2)
        self.assertIn("Perfil de practicante no encontrado", str(ctx.exception))

    def test_list_for_job_posting(self):
        job_posting = JobPosting(id=10, company_id=3)
        self.mock_job_posting_repo.find_by_id.return_value = job_posting

        p1 = JobApplication(id=1, job_posting_id=10, intern_id=50)
        self.mock_job_application_repo.find_by_job_posting_id.return_value = [p1]

        intern = MagicMock(id=50, first_names="Carlos")
        self.mock_profile_repo.find_intern_by_id.return_value = intern

        internship = MagicMock(id=1000)
        self.mock_internship_repo.find_by_job_application_id.return_value = internship

        result = self.service.list_for_job_posting(company_id=3, job_posting_id=10)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], (p1, intern, internship))
        
    def test_list_for_intern_returns_named_attributes(self):
        self.mock_profile_repo.find_intern_by_user_id.return_value = MagicMock(id=5)
        p1 = JobApplication(id=1, job_posting_id=100, intern_id=5)
        self.mock_job_application_repo.find_by_intern_id.return_value = [p1]
        c1 = JobPosting(id=100, title="Convo 100")
        self.mock_job_posting_repo.find_by_id.return_value = c1

        result = self.service.list_for_intern(user_id=2)

        self.assertIs(result[0].job_application, p1)
        self.assertIs(result[0].job_posting, c1)

    def test_list_for_job_posting_returns_named_attributes(self):
        self.mock_job_posting_repo.find_by_id.return_value = JobPosting(id=10, company_id=3)
        p1 = JobApplication(id=1, job_posting_id=10, intern_id=50)
        self.mock_job_application_repo.find_by_job_posting_id.return_value = [p1]
        intern = MagicMock(id=50)
        internship = MagicMock(id=1000)
        self.mock_profile_repo.find_intern_by_id.return_value = intern
        self.mock_internship_repo.find_by_job_application_id.return_value = internship

        result = self.service.list_for_job_posting(company_id=3, job_posting_id=10)

        self.assertIs(result[0].job_application, p1)
        self.assertIs(result[0].intern, intern)
        self.assertIs(result[0].internship, internship)    

    def test_require_owned_job_posting_in_list_for_job_posting(self):
        # Missing job posting
        self.mock_job_posting_repo.find_by_id.return_value = None
        with self.assertRaises(ValueError) as ctx:
            self.service.list_for_job_posting(company_id=1, job_posting_id=99)
        self.assertIn("Convocatoria no encontrada", str(ctx.exception))

        # Job posting owned by another company
        foreign_job_posting = JobPosting(id=10, company_id=2)
        self.mock_job_posting_repo.find_by_id.return_value = foreign_job_posting
        with self.assertRaises(ValueError) as ctx2:
            self.service.list_for_job_posting(company_id=1, job_posting_id=10)
        self.assertIn("La convocatoria no pertenece a esta empresa", str(ctx2.exception))

    # ------------------- select_candidate tests -------------------

    def test_select_candidate_job_application_or_posting_not_found(self):
        self.mock_job_application_repo.find_by_id.return_value = None
        with self.assertRaises(ValueError) as ctx:
            self.service.select_candidate(company_id=1, job_application_id=99)
        self.assertIn("Postulación no encontrada", str(ctx.exception))

        job_application = JobApplication(id=1, job_posting_id=10)
        self.mock_job_application_repo.find_by_id.return_value = job_application
        self.mock_job_posting_repo.find_by_id.return_value = None
        with self.assertRaises(ValueError) as ctx2:
            self.service.select_candidate(company_id=1, job_application_id=1)
        self.assertIn("Convocatoria no encontrada", str(ctx2.exception))

    def test_select_candidate_from_foreign_job_posting_raises(self):
        job_application = JobApplication(id=1, job_posting_id=10)
        self.mock_job_application_repo.find_by_id.return_value = job_application
        other_company_job_posting = JobPosting(id=10, company_id=2)
        self.mock_job_posting_repo.find_by_id.return_value = other_company_job_posting

        with self.assertRaises(ValueError) as ctx:
            self.service.select_candidate(company_id=1, job_application_id=1)
        self.assertIn("La convocatoria no pertenece a esta empresa", str(ctx.exception))

    def test_select_candidate_fails_if_another_internship_already_started(self):
        application_to_select = JobApplication(id=1, job_posting_id=10, status=JobApplication.STATUS_PENDING)
        another_application = JobApplication(id=2, job_posting_id=10, status=JobApplication.STATUS_SELECTED)

        self.mock_job_application_repo.find_by_id.return_value = application_to_select
        self.mock_job_posting_repo.find_by_id.return_value = JobPosting(id=10, company_id=1)
        self.mock_job_application_repo.find_by_job_posting_id.return_value = [application_to_select, another_application]

        # Simulate that another one already has a started internship
        self.mock_internship_repo.find_by_job_application_id.return_value = MagicMock(id=555)

        with self.assertRaises(ValueError) as ctx:
            self.service.select_candidate(company_id=1, job_application_id=1)
        self.assertIn("No se puede cambiar al candidato porque la práctica seleccionada ya inició", str(ctx.exception))

    def test_select_candidate_succeeds_and_rejects_other_pending_or_selected(self):
        job_application_1 = JobApplication(id=1, job_posting_id=10, status=JobApplication.STATUS_PENDING)
        job_application_2 = JobApplication(id=2, job_posting_id=10, status=JobApplication.STATUS_PENDING)
        job_application_3 = JobApplication(id=3, job_posting_id=10, status=JobApplication.STATUS_SELECTED)

        self.mock_job_application_repo.find_by_id.return_value = job_application_1
        self.mock_job_posting_repo.find_by_id.return_value = JobPosting(id=10, company_id=1)
        self.mock_job_application_repo.find_by_job_posting_id.return_value = [job_application_1, job_application_2, job_application_3]
        self.mock_internship_repo.find_by_job_application_id.return_value = None
        self.mock_job_application_repo.save_all.side_effect = lambda items: list(items)

        result = self.service.select_candidate(company_id=1, job_application_id=1)

        self.assertEqual(result.id, 1)
        self.assertEqual(result.status, JobApplication.STATUS_SELECTED)
        self.assertEqual(job_application_2.status, JobApplication.STATUS_REJECTED)
        self.assertEqual(job_application_3.status, JobApplication.STATUS_REJECTED)

        self.mock_job_application_repo.save_all.assert_called_once_with(
            [job_application_1, job_application_2, job_application_3]
        )
        self.mock_job_application_repo.save.assert_not_called()

    def test_select_candidate_sends_notifications_to_candidates(self):
        mock_notif = unittest.mock.Mock()
        self.service.notification_service = mock_notif
        job_application_1 = JobApplication(id=1, job_posting_id=10, intern_id=101, status=JobApplication.STATUS_PENDING)
        job_application_2 = JobApplication(id=2, job_posting_id=10, intern_id=102, status=JobApplication.STATUS_PENDING)

        self.mock_job_application_repo.find_by_id.return_value = job_application_1
        self.mock_job_posting_repo.find_by_id.return_value = JobPosting(id=10, company_id=1)
        self.mock_job_application_repo.find_by_job_posting_id.return_value = [job_application_1, job_application_2]
        self.mock_internship_repo.find_by_job_application_id.return_value = None
        self.mock_job_application_repo.save_all.side_effect = lambda items: list(items)

        intern_1 = unittest.mock.Mock(user_id=201)
        intern_2 = unittest.mock.Mock(user_id=202)
        self.mock_profile_repo.find_intern_by_id.side_effect = lambda pid: (
            intern_1 if pid == 101 else intern_2
        )

        result = self.service.select_candidate(company_id=1, job_application_id=1)

        self.assertEqual(result.id, 1)
        self.assertEqual(mock_notif.create_notification.call_count, 2)
        mock_notif.create_notification.assert_any_call(
            recipient_user_id=201,
            notification_type="POSTULACION_SELECCIONADA",
            message="Has sido seleccionado para una convocatoria",
            metadata={"postulacion_id": 1},
        )
        mock_notif.create_notification.assert_any_call(
            recipient_user_id=202,
            notification_type="POSTULACION_RECHAZADA",
            message="Tu postulación no fue seleccionada",
            metadata={"postulacion_id": 2},
        )

    def test_select_candidate_tolerates_notification_error(self):
        mock_notif = unittest.mock.Mock()
        mock_notif.create_notification.side_effect = RuntimeError("Notification Error")
        self.service.notification_service = mock_notif
        job_application = JobApplication(id=1, job_posting_id=10, intern_id=101, status=JobApplication.STATUS_PENDING)

        self.mock_job_application_repo.find_by_id.return_value = job_application
        self.mock_job_posting_repo.find_by_id.return_value = JobPosting(id=10, company_id=1)
        self.mock_job_application_repo.find_by_job_posting_id.return_value = [job_application]
        self.mock_internship_repo.find_by_job_application_id.return_value = None
        self.mock_job_application_repo.save_all.side_effect = lambda items: list(items)
        self.mock_profile_repo.find_intern_by_id.return_value = unittest.mock.Mock(user_id=201)

        result = self.service.select_candidate(company_id=1, job_application_id=1)
        self.assertEqual(result.id, 1)

    # ------------------- reject_candidate, cancel and reconsider_candidate tests -------------------

    def test_reject_candidate_succeeds(self):
        job_application = JobApplication(id=1, job_posting_id=10, status=JobApplication.STATUS_PENDING)
        self.mock_job_application_repo.find_by_id.return_value = job_application
        self.mock_job_posting_repo.find_by_id.return_value = JobPosting(id=10, company_id=1)
        self.mock_job_application_repo.save.return_value = job_application

        result = self.service.reject_candidate(company_id=1, job_application_id=1)

        self.assertEqual(result.status, JobApplication.STATUS_REJECTED)
        self.mock_job_application_repo.save.assert_called_once_with(job_application)

    def test_reject_candidate_job_application_not_found(self):
        self.mock_job_application_repo.find_by_id.return_value = None
        with self.assertRaises(ValueError) as ctx:
            self.service.reject_candidate(company_id=1, job_application_id=99)
        self.assertIn("Postulación no encontrada", str(ctx.exception))

    def test_cancel_success_and_errors(self):
        # Intern not found
        self.mock_profile_repo.find_intern_by_user_id.return_value = None
        with self.assertRaises(ValueError) as ctx:
            self.service.cancel(user_id=1, job_application_id=10)
        self.assertIn("Perfil de practicante no encontrado", str(ctx.exception))

        # Job application not found
        intern = MagicMock(id=5)
        self.mock_profile_repo.find_intern_by_user_id.return_value = intern
        self.mock_job_application_repo.find_by_id.return_value = None
        with self.assertRaises(ValueError) as ctx2:
            self.service.cancel(user_id=1, job_application_id=10)
        self.assertIn("Postulación no encontrada", str(ctx2.exception))

        # Job application of another intern
        other_application = JobApplication(id=10, intern_id=99, status=JobApplication.STATUS_PENDING)
        self.mock_job_application_repo.find_by_id.return_value = other_application
        with self.assertRaises(ValueError) as ctx3:
            self.service.cancel(user_id=1, job_application_id=10)
        self.assertIn("La postulación no pertenece a este practicante", str(ctx3.exception))

        # Successful cancellation
        own_application = JobApplication(id=10, intern_id=5, status=JobApplication.STATUS_PENDING)
        self.mock_job_application_repo.find_by_id.return_value = own_application
        self.mock_job_application_repo.save.return_value = own_application

        result = self.service.cancel(user_id=1, job_application_id=10)
        self.assertEqual(result.status, JobApplication.STATUS_CANCELLED)
        self.mock_job_application_repo.save.assert_called_once_with(own_application)

    def test_reconsider_candidate_success_and_errors(self):
        # Job application not found
        self.mock_job_application_repo.find_by_id.return_value = None
        with self.assertRaises(ValueError) as ctx:
            self.service.reconsider_candidate(company_id=1, job_application_id=99)
        self.assertIn("Postulación no encontrada", str(ctx.exception))

        job_application = JobApplication(id=1, job_posting_id=10, status=JobApplication.STATUS_REJECTED)
        self.mock_job_application_repo.find_by_id.return_value = job_application
        self.mock_job_posting_repo.find_by_id.return_value = JobPosting(id=10, company_id=1)

        # With an internship already started
        self.mock_internship_repo.find_by_job_application_id.return_value = MagicMock(id=123)
        with self.assertRaises(ValueError) as ctx2:
            self.service.reconsider_candidate(company_id=1, job_application_id=1)
        self.assertIn("No se puede cambiar la decisión porque la práctica ya fue iniciada", str(ctx2.exception))

        # Successful reconsideration
        self.mock_internship_repo.find_by_job_application_id.return_value = None
        self.mock_job_application_repo.save.return_value = job_application

        result = self.service.reconsider_candidate(company_id=1, job_application_id=1)
        self.assertEqual(result.status, JobApplication.STATUS_PENDING)
        self.mock_job_application_repo.save.assert_called_once_with(job_application)
        
    def test_apply_to_missing_job_posting_uses_standard_message(self):
        self.mock_profile_repo.find_intern_by_user_id.return_value = MagicMock(
            id=5, first_names="Ana", last_names="Perez"
        )
        self.mock_job_posting_repo.find_by_id.return_value = None
        with self.assertRaises(ValueError) as ctx:
            self.service.apply(user_id=2, job_posting_id=99)
        self.assertEqual(str(ctx.exception), JOB_POSTING_NOT_FOUND)        
