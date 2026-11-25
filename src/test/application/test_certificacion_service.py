"""I-20 - Pruebas del servicio de aplicación de certificación (dobles autospec).

Código bajo prueba: application/certificacion_application_service.py
"""
import unittest
from types import SimpleNamespace
from unittest.mock import create_autospec

from application.certificacion_application_service import CertificacionApplicationService
from domain.certificacion.certificado import Certificado
from domain.certificacion.i_certificado_repository import ICertificadoRepository
from recruitment.domain.i_job_posting_repository import IJobPostingRepository
from recruitment.domain.i_job_application_repository import IJobApplicationRepository
from profiles.domain.i_profile_repository import IProfileRepository
from internships.domain.evaluation import Evaluation
from internships.domain.i_internship_repository import IInternshipRepository
from internships.domain.internship import Internship

COMPANY_ID = 10
INTERNSHIP_ID = 7


class TestCertificacionService(unittest.TestCase):
    def setUp(self):
        self.certificados = create_autospec(ICertificadoRepository, instance=True)
        self.internship_list = create_autospec(IInternshipRepository, instance=True)
        self.job_applications = create_autospec(IJobApplicationRepository, instance=True)
        self.job_postings = create_autospec(IJobPostingRepository, instance=True)
        self.profiles_repo = create_autospec(IProfileRepository, instance=True)
        self.service = CertificacionApplicationService(
            certificado_repository=self.certificados,
            internship_repository=self.internship_list,
            job_application_repository=self.job_applications,
            job_posting_repository=self.job_postings,
            profile_repository=self.profiles_repo,
        )

        self.internship = Internship(
            id=INTERNSHIP_ID, job_application_id=20, intern_id=30,
            status=Internship.STATUS_FINISHED,
            evaluations=[Evaluation(internship_id=INTERNSHIP_ID, score=90)],
        )
        self.job_application = SimpleNamespace(id=20, job_posting_id=40)
        self.job_posting = SimpleNamespace(id=40, company_id=COMPANY_ID, title="Practicas QA")
        self.intern = SimpleNamespace(id=30, first_names="Ana", last_names="Quispe")

        self.internship_list.find_by_id.return_value = self.internship
        self.job_applications.find_by_id.return_value = self.job_application
        self.job_postings.find_by_id.return_value = self.job_posting
        self.profiles_repo.find_intern_by_id.return_value = self.intern
        self.certificados.find_by_practica_id.return_value = None
        self.certificados.save.side_effect = lambda certificado: certificado

    # ---- issue_certificate ----
    def test_devuelve_certificado_existente_con_false(self):
        existing = Certificado(id=1, internship_id=INTERNSHIP_ID)
        self.certificados.find_by_practica_id.return_value = existing

        result = self.service.issue_certificate(COMPANY_ID, INTERNSHIP_ID)

        self.assertEqual((existing, False), result)
        self.certificados.save.assert_not_called()

    def test_guarda_certificado_nuevo_y_devuelve_tupla_con_true(self):
        certificado, creado = self.service.issue_certificate(COMPANY_ID, INTERNSHIP_ID)

        self.assertTrue(creado)
        self.assertEqual(INTERNSHIP_ID, certificado.internship_id)
        self.assertIn("Ana Quispe", certificado.documento.contenido)
        self.internship_list.find_by_id.assert_called_once_with(INTERNSHIP_ID)
        self.job_applications.find_by_id.assert_called_once_with(20)
        self.job_postings.find_by_id.assert_called_once_with(40)
        self.profiles_repo.find_intern_by_id.assert_called_once_with(30)
        self.certificados.find_by_practica_id.assert_called_once_with(INTERNSHIP_ID)
        self.certificados.save.assert_called_once_with(certificado)

    def test_emite_certificado_y_notifica_al_practicante(self):
        mock_notif_service = unittest.mock.Mock()
        self.service.notification_service = mock_notif_service
        self.intern.user_id = 99

        certificado, creado = self.service.issue_certificate(COMPANY_ID, INTERNSHIP_ID)

        self.assertTrue(creado)
        mock_notif_service.create_notification.assert_called_once_with(
            recipient_user_id=99,
            notification_type="CERTIFICADO_EMITIDO",
            message="Tu certificado digital ha sido emitido",
            metadata={"practica_id": INTERNSHIP_ID},
        )

    def test_emite_certificado_tolera_fallo_en_notificacion(self):
        mock_notif_service = unittest.mock.Mock()
        mock_notif_service.create_notification.side_effect = RuntimeError("SMTP Error")
        self.service.notification_service = mock_notif_service
        self.intern.user_id = 99

        certificado, creado = self.service.issue_certificate(COMPANY_ID, INTERNSHIP_ID)

        self.assertTrue(creado)
        self.assertEqual(INTERNSHIP_ID, certificado.internship_id)

    def test_practica_inexistente_lanza_error(self):
        self.internship_list.find_by_id.return_value = None
        with self.assertRaisesRegex(ValueError, "Práctica no encontrada"):
            self.service.issue_certificate(COMPANY_ID, INTERNSHIP_ID)
        self.certificados.save.assert_not_called()

    def test_postulacion_inexistente_lanza_error(self):
        self.job_applications.find_by_id.return_value = None
        with self.assertRaisesRegex(ValueError, "Postulación no encontrada"):
            self.service.issue_certificate(COMPANY_ID, INTERNSHIP_ID)

    def test_convocatoria_inexistente_lanza_error(self):
        self.job_postings.find_by_id.return_value = None
        with self.assertRaisesRegex(ValueError, "Convocatoria no encontrada"):
            self.service.issue_certificate(COMPANY_ID, INTERNSHIP_ID)

    def test_empresa_ajena_no_puede_emitir(self):
        with self.assertRaisesRegex(ValueError, "no pertenece"):
            self.service.issue_certificate(999, INTERNSHIP_ID)
        self.certificados.save.assert_not_called()

    def test_practicante_inexistente_lanza_error(self):
        self.profiles_repo.find_intern_by_id.return_value = None
        with self.assertRaisesRegex(ValueError, "Practicante no encontrado"):
            self.service.issue_certificate(COMPANY_ID, INTERNSHIP_ID)

    def test_practica_no_finalizada_no_se_certifica_ni_se_guarda(self):
        self.internship.status = Internship.STATUS_IN_PROGRESS
        with self.assertRaises(ValueError):
            self.service.issue_certificate(COMPANY_ID, INTERNSHIP_ID)
        self.certificados.save.assert_not_called()

    # ---- verify_certificate ----
    def test_verifica_certificado_valido(self):
        certificado, _ = self.service.issue_certificate(COMPANY_ID, INTERNSHIP_ID)
        self.certificados.find_by_codigo.return_value = certificado

        valido = self.service.verify_certificate(certificado.codigo_qr.value)

        self.assertTrue(valido)
        self.certificados.find_by_codigo.assert_called_once_with(certificado.codigo_qr.value)

    def test_verificacion_falla_si_el_pdf_fue_alterado(self):
        certificado, _ = self.service.issue_certificate(COMPANY_ID, INTERNSHIP_ID)
        certificado.documento.contenido = "contenido adulterado"
        self.certificados.find_by_codigo.return_value = certificado

        self.assertFalse(self.service.verify_certificate(certificado.codigo_qr.value))

    def test_verificacion_falla_si_no_hay_documento(self):
        certificado, _ = self.service.issue_certificate(COMPANY_ID, INTERNSHIP_ID)
        certificado.documento = None
        self.certificados.find_by_codigo.return_value = certificado

        self.assertFalse(self.service.verify_certificate(certificado.codigo_qr.value))

    def test_verificacion_de_codigo_inexistente_lanza_error(self):
        self.certificados.find_by_codigo.return_value = None
        with self.assertRaisesRegex(ValueError, "Certificado no encontrado"):
            self.service.verify_certificate("CERT-0-xxxxxxxx")

    # ---- find_by_practica_id ----
    def test_find_by_practica_id_delega_en_el_repositorio(self):
        existing = Certificado(id=1, internship_id=INTERNSHIP_ID)
        self.certificados.find_by_practica_id.return_value = existing

        self.assertIs(existing, self.service.find_by_practica_id(INTERNSHIP_ID))
        self.certificados.find_by_practica_id.assert_called_once_with(INTERNSHIP_ID)

    # ---- repositorios requeridos ----
    def test_sin_repositorios_lanza_runtime_error(self):
        service = CertificacionApplicationService()
        with self.assertRaises(RuntimeError):
            service.issue_certificate(COMPANY_ID, INTERNSHIP_ID)
        with self.assertRaises(RuntimeError):
            service.verify_certificate("X")
        with self.assertRaises(RuntimeError):
            service.find_by_practica_id(INTERNSHIP_ID)

    def test_falta_un_solo_repositorio_lanza_runtime_error(self):
        service = CertificacionApplicationService(
            certificado_repository=self.certificados,
            internship_repository=self.internship_list,
            job_application_repository=self.job_applications,
            job_posting_repository=self.job_postings,
            profile_repository=None,
        )
        with self.assertRaises(RuntimeError):
            service.find_by_practica_id(INTERNSHIP_ID)


if __name__ == "__main__":
    unittest.main()
