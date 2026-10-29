"""I-20 - Pruebas del servicio de aplicación de certificación (dobles autospec).

Código bajo prueba: application/certificacion_application_service.py
"""
import unittest
from types import SimpleNamespace
from unittest.mock import create_autospec

from application.certificacion_application_service import CertificacionApplicationService
from domain.certificacion.certificado import Certificado
from domain.certificacion.i_certificado_repository import ICertificadoRepository
from domain.convocatorias.i_convocatoria_repository import IConvocatoriaRepository
from domain.convocatorias.i_postulacion_repository import IPostulacionRepository
from domain.perfil.i_perfil_repository import IPerfilRepository
from domain.practica_evaluacion.evaluacion import Evaluacion
from domain.practica_evaluacion.i_practica_repository import IPracticaRepository
from domain.practica_evaluacion.practica import Practica

EMPRESA_ID = 10
PRACTICA_ID = 7


class TestCertificacionService(unittest.TestCase):
    def setUp(self):
        self.certificados = create_autospec(ICertificadoRepository, instance=True)
        self.practicas = create_autospec(IPracticaRepository, instance=True)
        self.postulaciones = create_autospec(IPostulacionRepository, instance=True)
        self.convocatorias = create_autospec(IConvocatoriaRepository, instance=True)
        self.perfiles = create_autospec(IPerfilRepository, instance=True)
        self.service = CertificacionApplicationService(
            certificado_repository=self.certificados,
            practica_repository=self.practicas,
            postulacion_repository=self.postulaciones,
            convocatoria_repository=self.convocatorias,
            perfil_repository=self.perfiles,
        )

        self.practica = Practica(
            id=PRACTICA_ID, postulacion_id=20, practicante_id=30,
            estado=Practica.ESTADO_FINALIZADA,
            evaluaciones=[Evaluacion(practica_id=PRACTICA_ID, puntaje=90)],
        )
        self.postulacion = SimpleNamespace(id=20, convocatoria_id=40)
        self.convocatoria = SimpleNamespace(id=40, empresa_id=EMPRESA_ID, titulo="Practicas QA")
        self.practicante = SimpleNamespace(id=30, nombres="Ana", apellidos="Quispe")

        self.practicas.find_by_id.return_value = self.practica
        self.postulaciones.find_by_id.return_value = self.postulacion
        self.convocatorias.find_by_id.return_value = self.convocatoria
        self.perfiles.find_practicante_by_id.return_value = self.practicante
        self.certificados.find_by_practica_id.return_value = None
        self.certificados.save.side_effect = lambda certificado: certificado

    # ---- issue_certificate ----
    def test_devuelve_certificado_existente_con_false(self):
        existente = Certificado(id=1, practica_id=PRACTICA_ID)
        self.certificados.find_by_practica_id.return_value = existente

        resultado = self.service.issue_certificate(EMPRESA_ID, PRACTICA_ID)

        self.assertEqual((existente, False), resultado)
        self.certificados.save.assert_not_called()

    def test_guarda_certificado_nuevo_y_devuelve_tupla_con_true(self):
        certificado, creado = self.service.issue_certificate(EMPRESA_ID, PRACTICA_ID)

        self.assertTrue(creado)
        self.assertEqual(PRACTICA_ID, certificado.practica_id)
        self.assertIn("Ana Quispe", certificado.documento.contenido)
        self.practicas.find_by_id.assert_called_once_with(PRACTICA_ID)
        self.postulaciones.find_by_id.assert_called_once_with(20)
        self.convocatorias.find_by_id.assert_called_once_with(40)
        self.perfiles.find_practicante_by_id.assert_called_once_with(30)
        self.certificados.find_by_practica_id.assert_called_once_with(PRACTICA_ID)
        self.certificados.save.assert_called_once_with(certificado)

    def test_practica_inexistente_lanza_error(self):
        self.practicas.find_by_id.return_value = None
        with self.assertRaisesRegex(ValueError, "Práctica no encontrada"):
            self.service.issue_certificate(EMPRESA_ID, PRACTICA_ID)
        self.certificados.save.assert_not_called()

    def test_postulacion_inexistente_lanza_error(self):
        self.postulaciones.find_by_id.return_value = None
        with self.assertRaisesRegex(ValueError, "Postulación no encontrada"):
            self.service.issue_certificate(EMPRESA_ID, PRACTICA_ID)

    def test_convocatoria_inexistente_lanza_error(self):
        self.convocatorias.find_by_id.return_value = None
        with self.assertRaisesRegex(ValueError, "Convocatoria no encontrada"):
            self.service.issue_certificate(EMPRESA_ID, PRACTICA_ID)

    def test_empresa_ajena_no_puede_emitir(self):
        with self.assertRaisesRegex(ValueError, "no pertenece"):
            self.service.issue_certificate(999, PRACTICA_ID)
        self.certificados.save.assert_not_called()

    def test_practicante_inexistente_lanza_error(self):
        self.perfiles.find_practicante_by_id.return_value = None
        with self.assertRaisesRegex(ValueError, "Practicante no encontrado"):
            self.service.issue_certificate(EMPRESA_ID, PRACTICA_ID)

    def test_practica_no_finalizada_no_se_certifica_ni_se_guarda(self):
        self.practica.estado = Practica.ESTADO_EN_CURSO
        with self.assertRaises(ValueError):
            self.service.issue_certificate(EMPRESA_ID, PRACTICA_ID)
        self.certificados.save.assert_not_called()

    # ---- verify_certificate ----
    def test_verifica_certificado_valido(self):
        certificado, _ = self.service.issue_certificate(EMPRESA_ID, PRACTICA_ID)
        self.certificados.find_by_codigo.return_value = certificado

        valido = self.service.verify_certificate(certificado.codigo_qr.valor)

        self.assertTrue(valido)
        self.certificados.find_by_codigo.assert_called_once_with(certificado.codigo_qr.valor)

    def test_verificacion_falla_si_el_pdf_fue_alterado(self):
        certificado, _ = self.service.issue_certificate(EMPRESA_ID, PRACTICA_ID)
        certificado.documento.contenido = "contenido adulterado"
        self.certificados.find_by_codigo.return_value = certificado

        self.assertFalse(self.service.verify_certificate(certificado.codigo_qr.valor))

    def test_verificacion_falla_si_no_hay_documento(self):
        certificado, _ = self.service.issue_certificate(EMPRESA_ID, PRACTICA_ID)
        certificado.documento = None
        self.certificados.find_by_codigo.return_value = certificado

        self.assertFalse(self.service.verify_certificate(certificado.codigo_qr.valor))

    def test_verificacion_de_codigo_inexistente_lanza_error(self):
        self.certificados.find_by_codigo.return_value = None
        with self.assertRaisesRegex(ValueError, "Certificado no encontrado"):
            self.service.verify_certificate("CERT-0-xxxxxxxx")

    # ---- find_by_practica_id ----
    def test_find_by_practica_id_delega_en_el_repositorio(self):
        existente = Certificado(id=1, practica_id=PRACTICA_ID)
        self.certificados.find_by_practica_id.return_value = existente

        self.assertIs(existente, self.service.find_by_practica_id(PRACTICA_ID))
        self.certificados.find_by_practica_id.assert_called_once_with(PRACTICA_ID)

    # ---- repositorios requeridos ----
    def test_sin_repositorios_lanza_runtime_error(self):
        servicio = CertificacionApplicationService()
        with self.assertRaises(RuntimeError):
            servicio.issue_certificate(EMPRESA_ID, PRACTICA_ID)
        with self.assertRaises(RuntimeError):
            servicio.verify_certificate("X")
        with self.assertRaises(RuntimeError):
            servicio.find_by_practica_id(PRACTICA_ID)

    def test_falta_un_solo_repositorio_lanza_runtime_error(self):
        servicio = CertificacionApplicationService(
            certificado_repository=self.certificados,
            practica_repository=self.practicas,
            postulacion_repository=self.postulaciones,
            convocatoria_repository=self.convocatorias,
            perfil_repository=None,
        )
        with self.assertRaises(RuntimeError):
            servicio.find_by_practica_id(PRACTICA_ID)


if __name__ == "__main__":
    unittest.main()
