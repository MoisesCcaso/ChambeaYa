"""I-17: isolated tests for the internships application service."""

import unittest
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import create_autospec

from internships.application.internship_application_service import InternshipApplicationService
from recruitment.domain.job_posting import JobPosting
from recruitment.domain.i_job_posting_repository import IJobPostingRepository
from recruitment.domain.i_job_application_repository import IJobApplicationRepository
from recruitment.domain.job_application import JobApplication
from profiles.domain.i_profile_repository import IProfileRepository
from internships.domain.deliverable import Deliverable
from internships.domain.evaluation import Evaluation
from internships.domain.i_internship_repository import IInternshipRepository
from internships.domain.internship import Internship

INTERN_USER_ID = 5
COMPANY_USER_ID = 6
COMPANY_ID = 10
INTERN_ID = 30
JOB_APPLICATION_ID = 20
JOB_POSTING_ID = 40
INTERNSHIP_ID = 7


class TestInternshipApplicationService(unittest.TestCase):
    def setUp(self):
        self.internship_list = create_autospec(IInternshipRepository, instance=True)
        self.profiles_repo = create_autospec(IProfileRepository, instance=True)
        self.job_applications = create_autospec(IJobApplicationRepository, instance=True)
        self.job_postings = create_autospec(IJobPostingRepository, instance=True)
        self.service = InternshipApplicationService(
            internship_repository=self.internship_list,
            profile_repository=self.profiles_repo,
            job_application_repository=self.job_applications,
            job_posting_repository=self.job_postings,
        )

        self.internship = Internship(
            id=INTERNSHIP_ID,
            job_application_id=JOB_APPLICATION_ID,
            intern_id=INTERN_ID,
        )
        self.job_application = JobApplication(
            id=JOB_APPLICATION_ID,
            job_posting_id=JOB_POSTING_ID,
            intern_id=INTERN_ID,
            status=JobApplication.STATUS_SELECTED,
        )
        self.job_posting = JobPosting(
            id=JOB_POSTING_ID,
            company_id=COMPANY_ID,
            status=JobPosting.STATUS_PUBLISHED,
        )
        self.intern = SimpleNamespace(id=INTERN_ID)
        self.company = SimpleNamespace(id=COMPANY_ID)

        self.internship_list.find_by_id.return_value = self.internship
        self.internship_list.find_by_job_application_id.return_value = None
        self.internship_list.save.side_effect = lambda internship: internship
        self.profiles_repo.find_intern_by_user_id.return_value = self.intern
        self.profiles_repo.find_company_by_user_id.return_value = None
        self.job_applications.find_by_id.return_value = self.job_application
        self.job_postings.find_by_id.return_value = self.job_posting

    # Internship start
    def test_starts_internship_and_saves_with_the_right_arguments(self):
        result = self.service.start_internship(COMPANY_ID, JOB_APPLICATION_ID)

        self.job_applications.find_by_id.assert_called_once_with(JOB_APPLICATION_ID)
        self.job_postings.find_by_id.assert_called_once_with(JOB_POSTING_ID)
        self.internship_list.find_by_job_application_id.assert_called_once_with(JOB_APPLICATION_ID)
        saved_internship = self.internship_list.save.call_args.args[0]
        self.assertIs(result, saved_internship)
        self.assertEqual(JOB_APPLICATION_ID, saved_internship.job_application_id)
        self.assertEqual(INTERN_ID, saved_internship.intern_id)
        self.assertEqual(Internship.STATUS_IN_PROGRESS, saved_internship.status)

    def test_does_not_start_if_the_job_application_does_not_exist(self):
        self.job_applications.find_by_id.return_value = None
        with self.assertRaisesRegex(ValueError, "Postulación no encontrada"):
            self.service.start_internship(COMPANY_ID, JOB_APPLICATION_ID)
        self.job_postings.find_by_id.assert_not_called()
        self.internship_list.save.assert_not_called()

    def test_does_not_start_if_the_job_application_is_not_selected(self):
        self.job_application.status = JobApplication.STATUS_PENDING
        with self.assertRaisesRegex(ValueError, "debe estar seleccionada"):
            self.service.start_internship(COMPANY_ID, JOB_APPLICATION_ID)
        self.job_postings.find_by_id.assert_not_called()

    def test_does_not_start_if_the_job_posting_does_not_exist(self):
        self.job_postings.find_by_id.return_value = None
        with self.assertRaisesRegex(ValueError, "Convocatoria no encontrada"):
            self.service.start_internship(COMPANY_ID, JOB_APPLICATION_ID)
        self.internship_list.find_by_job_application_id.assert_not_called()

    def test_does_not_start_for_a_foreign_company(self):
        with self.assertRaisesRegex(ValueError, "no pertenece a esta empresa"):
            self.service.start_internship(999, JOB_APPLICATION_ID)
        self.internship_list.find_by_job_application_id.assert_not_called()

    def test_does_not_start_a_duplicate_internship(self):
        self.internship_list.find_by_job_application_id.return_value = self.internship
        with self.assertRaisesRegex(ValueError, "ya fue iniciada"):
            self.service.start_internship(COMPANY_ID, JOB_APPLICATION_ID)
        self.internship_list.save.assert_not_called()

    # Deliverables
    def test_uploads_deliverable_and_saves_the_aggregate(self):
        result = self.service.upload_deliverable(
            INTERN_USER_ID, INTERNSHIP_ID, "informe.pdf"
        )

        self.profiles_repo.find_intern_by_user_id.assert_called_once_with(
            INTERN_USER_ID
        )
        self.internship_list.find_by_id.assert_called_once_with(INTERNSHIP_ID)
        self.assertEqual("informe.pdf", self.internship.deliverables[0].file_name)
        self.internship_list.save.assert_called_once_with(self.internship)
        self.assertIs(result, self.internship)

    def test_upload_rejects_missing_profile(self):
        self.profiles_repo.find_intern_by_user_id.return_value = None
        with self.assertRaisesRegex(ValueError, "Perfil de practicante no encontrado"):
            self.service.upload_deliverable(999, INTERNSHIP_ID, "informe.pdf")
        self.internship_list.find_by_id.assert_not_called()

    def test_upload_rejects_missing_internship(self):
        self.internship_list.find_by_id.return_value = None
        with self.assertRaisesRegex(ValueError, "Práctica no encontrada"):
            self.service.upload_deliverable(
                INTERN_USER_ID, INTERNSHIP_ID, "informe.pdf"
            )

    def test_upload_rejects_another_interns_internship(self):
        self.internship.intern_id = 999
        with self.assertRaisesRegex(ValueError, "No autorizado"):
            self.service.upload_deliverable(
                INTERN_USER_ID, INTERNSHIP_ID, "informe.pdf"
            )
        self.internship_list.save.assert_not_called()

    def test_upload_propagates_the_finished_internship_rule(self):
        self.internship.status = Internship.STATUS_FINISHED
        with self.assertRaisesRegex(ValueError, "práctica finalizada"):
            self.service.upload_deliverable(
                INTERN_USER_ID, INTERNSHIP_ID, "informe.pdf"
            )
        self.internship_list.save.assert_not_called()

    def test_deliverables_history_is_returned_sorted(self):
        now_value = datetime.now(timezone.utc)
        recent = Deliverable(id=2, uploaded_at=now_value)
        older = Deliverable(id=1, uploaded_at=now_value - timedelta(days=1))
        self.internship.deliverables = [recent, older]

        result = self.service.get_deliverables_history(
            INTERN_USER_ID, INTERNSHIP_ID
        )

        self.assertEqual([older, recent], result)
        self.internship_list.find_by_id.assert_called_once_with(INTERNSHIP_ID)

    def test_removes_deliverable_and_saves_the_aggregate(self):
        deliverable = Deliverable(id=8, file_name="informe.pdf")
        self.internship.deliverables = [deliverable]

        removed = self.service.delete_deliverable(
            INTERN_USER_ID, INTERNSHIP_ID, 8
        )

        self.assertIs(deliverable, removed)
        self.assertEqual([], self.internship.deliverables)
        self.internship_list.save.assert_called_once_with(self.internship)

    def test_remove_missing_deliverable_does_not_save(self):
        with self.assertRaisesRegex(ValueError, "Entregable no encontrado"):
            self.service.delete_deliverable(
                INTERN_USER_ID, INTERNSHIP_ID, 999
            )
        self.internship_list.save.assert_not_called()

    # Evaluations
    def test_evaluate_internship_saves_with_the_right_arguments(self):
        result = self.service.evaluate(COMPANY_ID, INTERNSHIP_ID, 85)

        self.internship_list.find_by_id.assert_called_once_with(INTERNSHIP_ID)
        self.job_applications.find_by_id.assert_called_once_with(JOB_APPLICATION_ID)
        self.job_postings.find_by_id.assert_called_once_with(JOB_POSTING_ID)
        self.assertEqual(85, self.internship.evaluations[0].score)
        self.internship_list.save.assert_called_once_with(self.internship)
        self.assertIs(result, self.internship)

    def test_evaluate_internship_and_notify_the_intern(self):
        mock_notif = unittest.mock.Mock()
        self.service.notification_service = mock_notif
        self.intern.user_id = 99
        self.profiles_repo.find_intern_by_id.return_value = self.intern

        result = self.service.evaluate(COMPANY_ID, INTERNSHIP_ID, 85)

        self.assertIs(result, self.internship)
        mock_notif.create_notification.assert_called_once_with(
            recipient_user_id=99,
            notification_type="EVALUACION_DISPONIBLE",
            message="Tu práctica tiene una nueva evaluación disponible",
            metadata={"practica_id": INTERNSHIP_ID},
        )

    def test_evaluate_internship_tolerates_notification_failure(self):
        mock_notif = unittest.mock.Mock()
        mock_notif.create_notification.side_effect = RuntimeError("Notification Error")
        self.service.notification_service = mock_notif
        self.intern.user_id = 99
        self.profiles_repo.find_intern_by_id.return_value = self.intern

        result = self.service.evaluate(COMPANY_ID, INTERNSHIP_ID, 85)
        self.assertIs(result, self.internship)

    def test_evaluate_rejects_missing_internship(self):
        self.internship_list.find_by_id.return_value = None
        with self.assertRaisesRegex(ValueError, "Práctica no encontrada"):
            self.service.evaluate(COMPANY_ID, INTERNSHIP_ID, 85)
        self.job_applications.find_by_id.assert_not_called()

    def test_evaluate_rejects_missing_job_application(self):
        self.job_applications.find_by_id.return_value = None
        with self.assertRaisesRegex(ValueError, "Postulación no encontrada"):
            self.service.evaluate(COMPANY_ID, INTERNSHIP_ID, 85)
        self.job_postings.find_by_id.assert_not_called()

    def test_evaluate_rejects_missing_job_posting(self):
        self.job_postings.find_by_id.return_value = None
        with self.assertRaisesRegex(ValueError, "Convocatoria no encontrada"):
            self.service.evaluate(COMPANY_ID, INTERNSHIP_ID, 85)

    def test_evaluate_rejects_foreign_company(self):
        with self.assertRaisesRegex(ValueError, "convocatoria de esta empresa"):
            self.service.evaluate(999, INTERNSHIP_ID, 85)
        self.internship_list.save.assert_not_called()

    def test_evaluate_propagates_invalid_score_and_does_not_save(self):
        with self.assertRaisesRegex(ValueError, "entre 0 y 100"):
            self.service.evaluate(COMPANY_ID, INTERNSHIP_ID, 101)
        self.internship_list.save.assert_not_called()

    def test_evaluations_history_is_returned_sorted(self):
        now_value = datetime.now(timezone.utc)
        recent = Evaluation(id=2, evaluated_at=now_value)
        older_one = Evaluation(id=1, evaluated_at=now_value - timedelta(days=1))
        self.internship.evaluations = [recent, older_one]

        result = self.service.get_evaluations_history(
            INTERN_USER_ID, INTERNSHIP_ID
        )

        self.assertEqual([older_one, recent], result)

    def test_removes_evaluation_as_owner_company(self):
        evaluation = Evaluation(id=9, score=90)
        self.internship.evaluations = [evaluation]

        deleted = self.service.delete_evaluation(COMPANY_ID, INTERNSHIP_ID, 9)

        self.assertIs(evaluation, deleted)
        self.assertEqual([], self.internship.evaluations)
        self.job_applications.find_by_id.assert_called_once_with(JOB_APPLICATION_ID)
        self.job_postings.find_by_id.assert_called_once_with(JOB_POSTING_ID)
        self.internship_list.save.assert_called_once_with(self.internship)

    def test_remove_evaluation_rejects_missing_internship(self):
        self.internship_list.find_by_id.return_value = None
        with self.assertRaisesRegex(ValueError, "Práctica no encontrada"):
            self.service.delete_evaluation(COMPANY_ID, INTERNSHIP_ID, 9)

    def test_remove_missing_evaluation_does_not_save(self):
        with self.assertRaisesRegex(ValueError, "Evaluación no encontrada"):
            self.service.delete_evaluation(COMPANY_ID, INTERNSHIP_ID, 999)
        self.internship_list.save.assert_not_called()

    # Finishing and company authorization
    def test_finishes_internship_meeting_the_rules_and_saves_it(self):
        self.internship.deliverables = [Deliverable(id=8)]
        self.internship.evaluations = [Evaluation(id=9, score=60)]

        result = self.service.finish(COMPANY_ID, INTERNSHIP_ID)

        self.assertEqual(Internship.STATUS_FINISHED, self.internship.status)
        self.internship_list.save.assert_called_once_with(self.internship)
        self.assertIs(result, self.internship)

    def test_finish_rejects_missing_internship(self):
        self.internship_list.find_by_id.return_value = None
        with self.assertRaisesRegex(ValueError, "Práctica no encontrada"):
            self.service.finish(COMPANY_ID, INTERNSHIP_ID)

    def test_finish_propagates_domain_rules_and_does_not_save(self):
        with self.assertRaisesRegex(ValueError, "sin entregables"):
            self.service.finish(COMPANY_ID, INTERNSHIP_ID)
        self.internship_list.save.assert_not_called()

    def test_company_operation_rejects_missing_job_application(self):
        self.job_applications.find_by_id.return_value = None
        with self.assertRaisesRegex(ValueError, "Postulación no encontrada"):
            self.service.finish(COMPANY_ID, INTERNSHIP_ID)
        self.job_postings.find_by_id.assert_not_called()

    def test_company_operation_rejects_missing_job_posting(self):
        self.job_postings.find_by_id.return_value = None
        with self.assertRaisesRegex(ValueError, "Convocatoria no encontrada"):
            self.service.finish(COMPANY_ID, INTERNSHIP_ID)

    def test_company_operation_rejects_foreign_company(self):
        with self.assertRaisesRegex(ValueError, "no pertenece a esta empresa"):
            self.service.finish(999, INTERNSHIP_ID)
        self.internship_list.save.assert_not_called()

    # Queries and visibility
    def test_lists_the_interns_internships(self):
        expected_items = [self.internship]
        self.internship_list.find_by_intern_id.return_value = expected_items

        result = self.service.list_for_user(INTERN_USER_ID)

        self.assertIs(expected_items, result)
        self.internship_list.find_by_intern_id.assert_called_once_with(INTERN_ID)
        self.profiles_repo.find_company_by_user_id.assert_not_called()

    def test_lists_company_internships_and_skips_applications_without_internship(self):
        internship_2 = Internship(id=8, job_application_id=22, intern_id=31)
        self.profiles_repo.find_intern_by_user_id.return_value = None
        self.profiles_repo.find_company_by_user_id.return_value = self.company
        self.internship_list.find_by_company_id.return_value = [self.internship, internship_2]

        result = self.service.list_for_user(COMPANY_USER_ID)

        self.assertEqual([self.internship, internship_2], result)
        self.internship_list.find_by_company_id.assert_called_once_with(COMPANY_ID)

    def test_list_rejects_user_without_profile(self):
        self.profiles_repo.find_intern_by_user_id.return_value = None
        self.profiles_repo.find_company_by_user_id.return_value = None
        with self.assertRaisesRegex(ValueError, "Perfil no encontrado"):
            self.service.list_for_user(999)

    def test_owner_company_can_query_internship(self):
        self.profiles_repo.find_intern_by_user_id.return_value = None
        self.profiles_repo.find_company_by_user_id.return_value = self.company

        result = self.service.get_for_user(COMPANY_USER_ID, INTERNSHIP_ID)

        self.assertIs(self.internship, result)
        self.profiles_repo.find_company_by_user_id.assert_called_once_with(COMPANY_USER_ID)
        self.job_applications.find_by_id.assert_called_once_with(JOB_APPLICATION_ID)

    def test_visible_query_rejects_missing_internship(self):
        self.internship_list.find_by_id.return_value = None
        with self.assertRaisesRegex(ValueError, "Práctica no encontrada"):
            self.service.get_for_user(INTERN_USER_ID, INTERNSHIP_ID)
        self.profiles_repo.find_intern_by_user_id.assert_not_called()

    def test_query_rejects_foreign_intern_without_company_profile(self):
        self.profiles_repo.find_intern_by_user_id.return_value = SimpleNamespace(id=999)
        self.profiles_repo.find_company_by_user_id.return_value = None
        with self.assertRaisesRegex(ValueError, "No autorizado"):
            self.service.get_for_user(INTERN_USER_ID, INTERNSHIP_ID)

    # Configuration
    def test_requires_every_repository_before_operating(self):
        incomplete_services = (
            InternshipApplicationService(),
            InternshipApplicationService(
                self.internship_list, self.profiles_repo, self.job_applications, None
            ),
        )
        for service in incomplete_services:
            with self.subTest(service=service):
                with self.assertRaisesRegex(RuntimeError, "requires all of its repositories"):
                    service.get_for_user(INTERN_USER_ID, INTERNSHIP_ID)


if __name__ == "__main__":
    unittest.main()
