"""I-18 - Pruebas unitarias del dominio de certificación.

Código bajo prueba:
    domain/certificacion/certificado.py, archivo_pdf.py, codigo_qr.py,
    certificacion_dominio_servicio.py
"""
import hashlib
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from certification.domain.archivo_pdf import ArchivoPDF
from certification.domain.certificacion_dominio_servicio import CertificacionDominioServicio
from certification.domain.certificado import Certificado
from certification.domain.codigo_qr import CodigoQR
from internships.domain.evaluation import Evaluation
from internships.domain.internship import Internship

UUID4_PATH = "certification.domain.codigo_qr.uuid4"


def _practica(status=Internship.STATUS_FINISHED, puntajes=(80,), internship_id=7):
    evaluations = [Evaluation(internship_id=internship_id, score=p) for p in puntajes]
    return Internship(id=internship_id, job_application_id=1, intern_id=2,
                    status=status, evaluations=evaluations)


def _datos_certificado():
    intern = SimpleNamespace(first_names="Ana", last_names="Quispe")
    job_posting = SimpleNamespace(title="Practicas de Backend")
    return intern, job_posting


class TestCertificacionDominioServicio(unittest.TestCase):
    def setUp(self):
        self.service = CertificacionDominioServicio()
        self.intern, self.job_posting = _datos_certificado()

    def test_genera_certificado_para_practica_finalizada_y_aprobada(self):
        internship = _practica()
        certificado = self.service.generar_certificado(
            internship, self.intern, self.job_posting
        )
        self.assertEqual(7, certificado.internship_id)
        self.assertIsNotNone(certificado.codigo_qr)
        self.assertIsNotNone(certificado.documento)
        self.assertIn("Ana Quispe", certificado.documento.contenido)
        self.assertIn("Practicas de Backend", certificado.documento.contenido)

    def test_rechaza_practica_en_curso(self):
        internship = _practica(status=Internship.STATUS_IN_PROGRESS)
        with self.assertRaises(ValueError):
            self.service.generar_certificado(internship, self.intern, self.job_posting)

    def test_rechaza_practica_finalizada_sin_evaluacion_aprobada(self):
        internship = _practica(puntajes=(59.99,))
        with self.assertRaises(ValueError):
            self.service.generar_certificado(internship, self.intern, self.job_posting)

    def test_rechaza_practica_finalizada_sin_evaluaciones(self):
        internship = _practica(puntajes=())
        with self.assertRaises(ValueError):
            self.service.generar_certificado(internship, self.intern, self.job_posting)

    def test_acepta_si_al_menos_una_evaluacion_aprueba(self):
        internship = _practica(puntajes=(30, 60))
        certificado = self.service.generar_certificado(
            internship, self.intern, self.job_posting
        )
        self.assertIsNotNone(certificado)


class TestCodigoQR(unittest.TestCase):
    @patch(UUID4_PATH)
    def test_generar_usa_uuid_determinista_sin_acoplar_url_http(self, uuid4_mock):
        uuid4_mock.return_value = MagicMock(hex="abcdef1234567890")
        qr = CodigoQR.generar(5)
        self.assertEqual("CERT-5-abcdef12", qr.value)
        self.assertIsNone(qr.url_verificacion)
        self.assertEqual(hashlib.sha256(b"CERT-5-abcdef12").hexdigest(), qr.hash_integridad)

    @patch(UUID4_PATH)
    def test_generar_acepta_url_verificacion_inyectada(self, uuid4_mock):
        uuid4_mock.return_value = MagicMock(hex="abcdef1234567890")
        qr = CodigoQR.generar(5, url_verificacion="https://chambeaya.pe/verify/CERT-5-abcdef12")
        self.assertEqual("https://chambeaya.pe/verify/CERT-5-abcdef12", qr.url_verificacion)

    @patch(UUID4_PATH)
    def test_verificar_acepta_valor_correcto(self, uuid4_mock):
        uuid4_mock.return_value = MagicMock(hex="abcdef1234567890")
        qr = CodigoQR.generar(5)
        self.assertTrue(qr.verificar("CERT-5-abcdef12"))

    @patch(UUID4_PATH)
    def test_verificar_rechaza_valor_alterado(self, uuid4_mock):
        uuid4_mock.return_value = MagicMock(hex="abcdef1234567890")
        qr = CodigoQR.generar(5)
        self.assertFalse(qr.verificar("CERT-5-abcdef13"))

    def test_verificar_rechaza_qr_sin_valor_o_sin_hash(self):
        self.assertFalse(CodigoQR(value=None, hash_integridad="h").verificar("x"))
        self.assertFalse(CodigoQR(value="CERT-1-a", hash_integridad=None).verificar("CERT-1-a"))

    def test_verificar_rechaza_hash_manipulado(self):
        qr = CodigoQR(value="CERT-1-a", hash_integridad="no-coincide")
        self.assertFalse(qr.verificar("CERT-1-a"))


class TestArchivoPDF(unittest.TestCase):
    def setUp(self):
        self.pdf = ArchivoPDF.create(3, "contenido original")

    def test_crear_calcula_hash_sin_acoplar_url_http(self):
        self.assertIsNone(self.pdf.url)
        self.assertEqual(
            hashlib.sha256(b"contenido original").hexdigest(), self.pdf.hash_integridad
        )

    def test_crear_acepta_url_inyectada(self):
        pdf = ArchivoPDF.create(3, "contenido original", url="https://cdn.chambeaya.pe/3.pdf")
        self.assertEqual("https://cdn.chambeaya.pe/3.pdf", pdf.url)

    def test_crear_sin_contenido_lanza_error(self):
        with self.assertRaises(ValueError):
            ArchivoPDF.create(3, "")
        with self.assertRaises(ValueError):
            ArchivoPDF.create(3, None)

    def test_integridad_con_contenido_igual(self):
        self.assertTrue(self.pdf.verificar_integridad("contenido original"))

    def test_integridad_con_contenido_en_bytes(self):
        self.assertTrue(self.pdf.verificar_integridad(b"contenido original"))

    def test_integridad_con_contenido_cambiado(self):
        self.assertFalse(self.pdf.verificar_integridad("contenido modificado"))

    def test_integridad_con_contenido_ausente(self):
        self.assertFalse(self.pdf.verificar_integridad(None))

    def test_integridad_con_hash_vacio(self):
        self.assertFalse(ArchivoPDF(hash_integridad="").verificar_integridad("contenido original"))
        self.assertFalse(ArchivoPDF(hash_integridad=None).verificar_integridad("x"))


class TestCertificado(unittest.TestCase):
    def test_generar_pdf_asigna_documento_sin_ruta_http_acoplada(self):
        certificado = Certificado(internship_id=4)
        documento = certificado.generar_pdf("texto")
        self.assertIs(documento, certificado.documento)
        self.assertIsNone(documento.url)

    def test_verificar_integridad_sin_documento_devuelve_false(self):
        self.assertFalse(Certificado(internship_id=4).verificar_integridad("texto"))

    def test_verificar_integridad_delega_en_el_documento(self):
        certificado = Certificado(internship_id=4)
        certificado.generar_pdf("texto")
        self.assertTrue(certificado.verificar_integridad("texto"))
        self.assertFalse(certificado.verificar_integridad("otro"))

    def test_verificar_qr_con_valor_correcto(self):
        certificado = Certificado(internship_id=4, codigo_qr=CodigoQR.generar(4))
        self.assertTrue(certificado.verificar_qr(certificado.codigo_qr.value))

    def test_verificar_qr_rechaza_valor_alterado(self):
        certificado = Certificado(internship_id=4, codigo_qr=CodigoQR.generar(4))
        self.assertFalse(certificado.verificar_qr(certificado.codigo_qr.value + "x"))

    def test_verificar_qr_sin_qr_devuelve_false(self):
        self.assertFalse(Certificado(internship_id=1).verificar_qr("X"))


if __name__ == "__main__":
    unittest.main()
