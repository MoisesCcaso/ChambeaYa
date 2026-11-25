"""I-20 - Tests for the certification application service (autospec doubles).

Code under test: certification/application/certification_application_service.py
"""
import unittest
from types import SimpleNamespace
from unittest.mock import create_autospec

from certification.application.certification_application_service import CertificationApplicationService
from certification.domain.certificate import Certificate
from certification.domain.i_certificate_repository import ICertificateRepository
from recruitment.api import RecruitmentApi
from profiles.api import ProfilesApi
from internships.domain.evaluation import Evaluation
from internships.api import InternshipsApi
from internships.domain.internship import Internship

COMPANY_ID = 10
INTERNSHIP_ID = 7


class TestCertificationService(unittest.TestCase):
    def setUp(self):
        self.certificates = create_autospec(ICertificateRepository, instance=True)
        self.internships = create_autospec(InternshipsApi, instance=True)
        self.recruitment = create_autospec(RecruitmentApi, instance=True)
        self.profiles = create_autospec(ProfilesApi, instance=True)
        self.service = CertificationApplicationService(
            certificate_repository=self.certificates,
            internships=self.internships,
            recruitment=self.recruitment,
            profiles=self.profiles,
        )

        self.internship = Internship(
            id=INTERNSHIP_ID, job_application_id=20, intern_id=30,
            status=Internship.STATUS_FINISHED,
            evaluations=[Evaluation(internship_id=INTERNSHIP_ID, score=90)],
        )
        self.job_application = SimpleNamespace(id=20, job_posting_id=40)
        self.job_posting = SimpleNamespace(id=40, company_id=COMPANY_ID, title="Practicas QA")
        self.intern = SimpleNamespace(id=30, first_names="Ana", last_names="Quispe")

        self.internships.find_internship.return_value = self.internship
        self.recruitment.find_job_application.return_value = self.job_application
        self.recruitment.find_job_posting.return_value = self.job_posting
        self.profiles.find_intern_by_id.return_value = self.intern
        self.certificates.find_by_internship_id.return_value = None
        self.certificates.save.side_effect = lambda certificate: certificate

    # ---- issue_certificate ----
    def test_returns_existing_certificate_with_false(self):
        existing = Certificate(id=1, internship_id=INTERNSHIP_ID)
        self.certificates.find_by_internship_id.return_value = existing

        result = self.service.issue_certificate(COMPANY_ID, INTERNSHIP_ID)

        self.assertEqual((existing, False), result)
        self.certificates.save.assert_not_called()

    def test_saves_new_certificate_and_returns_tuple_with_true(self):
        certificate, created = self.service.issue_certificate(COMPANY_ID, INTERNSHIP_ID)

        self.assertTrue(created)
        self.assertEqual(INTERNSHIP_ID, certificate.internship_id)
        self.assertIn("Ana Quispe", certificate.document.content)
        self.internships.find_internship.assert_called_once_with(INTERNSHIP_ID)
        self.recruitment.find_job_application.assert_called_once_with(20)
        self.recruitment.find_job_posting.assert_called_once_with(40)
        self.profiles.find_intern_by_id.assert_called_once_with(30)
        self.certificates.find_by_internship_id.assert_called_once_with(INTERNSHIP_ID)
        self.certificates.save.assert_called_once_with(certificate)

    def test_issue_certificate_and_notify_the_intern(self):
        mock_notif_service = unittest.mock.Mock()
        self.service.notifications = mock_notif_service
        self.intern.user_id = 99

        certificate, created = self.service.issue_certificate(COMPANY_ID, INTERNSHIP_ID)

        self.assertTrue(created)
        mock_notif_service.notify.assert_called_once_with(
            recipient_user_id=99,
            notification_type="CERTIFICADO_EMITIDO",
            message="Tu certificado digital ha sido emitido",
            metadata={"practica_id": INTERNSHIP_ID},
        )

    def test_issue_certificate_tolerates_notification_failure(self):
        mock_notif_service = unittest.mock.Mock()
        mock_notif_service.notify.side_effect = RuntimeError("SMTP Error")
        self.service.notifications = mock_notif_service
        self.intern.user_id = 99

        certificate, created = self.service.issue_certificate(COMPANY_ID, INTERNSHIP_ID)

        self.assertTrue(created)
        self.assertEqual(INTERNSHIP_ID, certificate.internship_id)

    def test_missing_internship_raises(self):
        self.internships.find_internship.return_value = None
        with self.assertRaisesRegex(ValueError, "Práctica no encontrada"):
            self.service.issue_certificate(COMPANY_ID, INTERNSHIP_ID)
        self.certificates.save.assert_not_called()

    def test_missing_job_application_raises(self):
        self.recruitment.find_job_application.return_value = None
        with self.assertRaisesRegex(ValueError, "Postulación no encontrada"):
            self.service.issue_certificate(COMPANY_ID, INTERNSHIP_ID)

    def test_missing_job_posting_raises(self):
        self.recruitment.find_job_posting.return_value = None
        with self.assertRaisesRegex(ValueError, "Convocatoria no encontrada"):
            self.service.issue_certificate(COMPANY_ID, INTERNSHIP_ID)

    def test_foreign_company_cannot_issue(self):
        with self.assertRaisesRegex(ValueError, "no pertenece"):
            self.service.issue_certificate(999, INTERNSHIP_ID)
        self.certificates.save.assert_not_called()

    def test_missing_intern_raises(self):
        self.profiles.find_intern_by_id.return_value = None
        with self.assertRaisesRegex(ValueError, "Practicante no encontrado"):
            self.service.issue_certificate(COMPANY_ID, INTERNSHIP_ID)

    def test_unfinished_internship_is_neither_certified_nor_saved(self):
        self.internship.status = Internship.STATUS_IN_PROGRESS
        with self.assertRaises(ValueError):
            self.service.issue_certificate(COMPANY_ID, INTERNSHIP_ID)
        self.certificates.save.assert_not_called()

    # ---- verify_certificate ----
    def test_verifies_valid_certificate(self):
        certificate, _ = self.service.issue_certificate(COMPANY_ID, INTERNSHIP_ID)
        self.certificates.find_by_code.return_value = certificate

        valid = self.service.verify_certificate(certificate.qr_code.value)

        self.assertTrue(valid)
        self.certificates.find_by_code.assert_called_once_with(certificate.qr_code.value)

    def test_verification_fails_if_the_pdf_was_tampered(self):
        certificate, _ = self.service.issue_certificate(COMPANY_ID, INTERNSHIP_ID)
        certificate.document.content = "contenido adulterado"
        self.certificates.find_by_code.return_value = certificate

        self.assertFalse(self.service.verify_certificate(certificate.qr_code.value))

    def test_verification_fails_without_document(self):
        certificate, _ = self.service.issue_certificate(COMPANY_ID, INTERNSHIP_ID)
        certificate.document = None
        self.certificates.find_by_code.return_value = certificate

        self.assertFalse(self.service.verify_certificate(certificate.qr_code.value))

    def test_verifying_missing_code_raises(self):
        self.certificates.find_by_code.return_value = None
        with self.assertRaisesRegex(ValueError, "Certificado no encontrado"):
            self.service.verify_certificate("CERT-0-xxxxxxxx")

    # ---- find_by_internship_id ----
    def test_find_by_internship_id_delegates_to_the_repository(self):
        existing = Certificate(id=1, internship_id=INTERNSHIP_ID)
        self.certificates.find_by_internship_id.return_value = existing

        self.assertIs(existing, self.service.find_by_internship_id(INTERNSHIP_ID))
        self.certificates.find_by_internship_id.assert_called_once_with(INTERNSHIP_ID)

    # ---- required repositories ----
    def test_without_repositories_raises_runtime_error(self):
        service = CertificationApplicationService()
        with self.assertRaises(RuntimeError):
            service.issue_certificate(COMPANY_ID, INTERNSHIP_ID)
        with self.assertRaises(RuntimeError):
            service.verify_certificate("X")
        with self.assertRaises(RuntimeError):
            service.find_by_internship_id(INTERNSHIP_ID)

    def test_a_single_missing_repository_raises_runtime_error(self):
        service = CertificationApplicationService(
            certificate_repository=self.certificates,
            internships=self.internships,
            recruitment=self.recruitment,
            profiles=None,
        )
        with self.assertRaises(RuntimeError):
            service.find_by_internship_id(INTERNSHIP_ID)


if __name__ == "__main__":
    unittest.main()
