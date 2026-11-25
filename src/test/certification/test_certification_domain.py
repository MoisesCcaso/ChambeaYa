"""I-18 - Unit tests for the certification domain.

Code under test:
    certification/domain/certificate.py, pdf_file.py, qr_code.py,
    certification_domain_service.py
"""
import hashlib
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from certification.domain.pdf_file import PdfFile
from certification.domain.certification_domain_service import CertificationDomainService
from certification.domain.certificate import Certificate
from certification.domain.qr_code import QrCode
from internships.domain.evaluation import Evaluation
from internships.domain.internship import Internship

UUID4_PATH = "certification.domain.qr_code.uuid4"


def _internship(status=Internship.STATUS_FINISHED, scores=(80,), internship_id=7):
    evaluations = [Evaluation(internship_id=internship_id, score=p) for p in scores]
    return Internship(id=internship_id, job_application_id=1, intern_id=2,
                    status=status, evaluations=evaluations)


def _certificate_data():
    intern = SimpleNamespace(first_names="Ana", last_names="Quispe")
    job_posting = SimpleNamespace(title="Practicas de Backend")
    return intern, job_posting


class TestCertificationDomainService(unittest.TestCase):
    def setUp(self):
        self.service = CertificationDomainService()
        self.intern, self.job_posting = _certificate_data()

    def test_generates_certificate_for_finished_and_passed_internship(self):
        internship = _internship()
        certificate = self.service.generate_certificate(
            internship, self.intern, self.job_posting
        )
        self.assertEqual(7, certificate.internship_id)
        self.assertIsNotNone(certificate.qr_code)
        self.assertIsNotNone(certificate.document)
        self.assertIn("Ana Quispe", certificate.document.content)
        self.assertIn("Practicas de Backend", certificate.document.content)

    def test_rejects_internship_in_progress(self):
        internship = _internship(status=Internship.STATUS_IN_PROGRESS)
        with self.assertRaises(ValueError):
            self.service.generate_certificate(internship, self.intern, self.job_posting)

    def test_rejects_finished_internship_without_passed_evaluation(self):
        internship = _internship(scores=(59.99,))
        with self.assertRaises(ValueError):
            self.service.generate_certificate(internship, self.intern, self.job_posting)

    def test_rejects_finished_internship_without_evaluations(self):
        internship = _internship(scores=())
        with self.assertRaises(ValueError):
            self.service.generate_certificate(internship, self.intern, self.job_posting)

    def test_accepts_if_at_least_one_evaluation_passes(self):
        internship = _internship(scores=(30, 60))
        certificate = self.service.generate_certificate(
            internship, self.intern, self.job_posting
        )
        self.assertIsNotNone(certificate)


class TestQrCode(unittest.TestCase):
    @patch(UUID4_PATH)
    def test_generate_uses_deterministic_uuid_without_coupling_an_http_url(self, uuid4_mock):
        uuid4_mock.return_value = MagicMock(hex="abcdef1234567890")
        qr = QrCode.generate(5)
        self.assertEqual("CERT-5-abcdef12", qr.value)
        self.assertIsNone(qr.verification_url)
        self.assertEqual(hashlib.sha256(b"CERT-5-abcdef12").hexdigest(), qr.integrity_hash)

    @patch(UUID4_PATH)
    def test_generate_accepts_injected_verification_url(self, uuid4_mock):
        uuid4_mock.return_value = MagicMock(hex="abcdef1234567890")
        qr = QrCode.generate(5, verification_url="https://chambeaya.pe/verify/CERT-5-abcdef12")
        self.assertEqual("https://chambeaya.pe/verify/CERT-5-abcdef12", qr.verification_url)

    @patch(UUID4_PATH)
    def test_verify_accepts_correct_value(self, uuid4_mock):
        uuid4_mock.return_value = MagicMock(hex="abcdef1234567890")
        qr = QrCode.generate(5)
        self.assertTrue(qr.verify("CERT-5-abcdef12"))

    @patch(UUID4_PATH)
    def test_verify_rejects_tampered_value(self, uuid4_mock):
        uuid4_mock.return_value = MagicMock(hex="abcdef1234567890")
        qr = QrCode.generate(5)
        self.assertFalse(qr.verify("CERT-5-abcdef13"))

    def test_verify_rejects_qr_without_value_or_hash(self):
        self.assertFalse(QrCode(value=None, integrity_hash="h").verify("x"))
        self.assertFalse(QrCode(value="CERT-1-a", integrity_hash=None).verify("CERT-1-a"))

    def test_verify_rejects_tampered_hash(self):
        qr = QrCode(value="CERT-1-a", integrity_hash="no-coincide")
        self.assertFalse(qr.verify("CERT-1-a"))


class TestPdfFile(unittest.TestCase):
    def setUp(self):
        self.pdf = PdfFile.create(3, "contenido original")

    def test_create_computes_hash_without_coupling_an_http_url(self):
        self.assertIsNone(self.pdf.url)
        self.assertEqual(
            hashlib.sha256(b"contenido original").hexdigest(), self.pdf.integrity_hash
        )

    def test_create_accepts_injected_url(self):
        pdf = PdfFile.create(3, "contenido original", url="https://cdn.chambeaya.pe/3.pdf")
        self.assertEqual("https://cdn.chambeaya.pe/3.pdf", pdf.url)

    def test_create_without_content_raises(self):
        with self.assertRaises(ValueError):
            PdfFile.create(3, "")
        with self.assertRaises(ValueError):
            PdfFile.create(3, None)

    def test_integrity_with_equal_content(self):
        self.assertTrue(self.pdf.verify_integrity("contenido original"))

    def test_integrity_with_bytes_content(self):
        self.assertTrue(self.pdf.verify_integrity(b"contenido original"))

    def test_integrity_with_changed_content(self):
        self.assertFalse(self.pdf.verify_integrity("contenido modificado"))

    def test_integrity_with_missing_content(self):
        self.assertFalse(self.pdf.verify_integrity(None))

    def test_integrity_with_empty_hash(self):
        self.assertFalse(PdfFile(integrity_hash="").verify_integrity("contenido original"))
        self.assertFalse(PdfFile(integrity_hash=None).verify_integrity("x"))


class TestCertificate(unittest.TestCase):
    def test_generate_pdf_sets_document_without_coupled_http_route(self):
        certificate = Certificate(internship_id=4)
        document = certificate.generate_pdf("texto")
        self.assertIs(document, certificate.document)
        self.assertIsNone(document.url)

    def test_verify_integrity_without_document_returns_false(self):
        self.assertFalse(Certificate(internship_id=4).verify_integrity("texto"))

    def test_verify_integrity_delegates_to_the_document(self):
        certificate = Certificate(internship_id=4)
        certificate.generate_pdf("texto")
        self.assertTrue(certificate.verify_integrity("texto"))
        self.assertFalse(certificate.verify_integrity("otro"))

    def test_verify_qr_with_correct_value(self):
        certificate = Certificate(internship_id=4, qr_code=QrCode.generate(4))
        self.assertTrue(certificate.verify_qr(certificate.qr_code.value))

    def test_verify_qr_rejects_tampered_value(self):
        certificate = Certificate(internship_id=4, qr_code=QrCode.generate(4))
        self.assertFalse(certificate.verify_qr(certificate.qr_code.value + "x"))

    def test_verify_qr_without_qr_returns_false(self):
        self.assertFalse(Certificate(internship_id=1).verify_qr("X"))


if __name__ == "__main__":
    unittest.main()
