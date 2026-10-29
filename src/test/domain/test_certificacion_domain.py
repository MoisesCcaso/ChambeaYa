"""I-18 - Pruebas unitarias del dominio de certificación.

Código bajo prueba:
    domain/certificacion/certificado.py, archivo_pdf.py, codigo_qr.py,
    certificacion_dominio_servicio.py
"""
import hashlib
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from domain.certificacion.archivo_pdf import ArchivoPDF
from domain.certificacion.certificacion_dominio_servicio import CertificacionDominioServicio
from domain.certificacion.certificado import Certificado
from domain.certificacion.codigo_qr import CodigoQR
from domain.practica_evaluacion.evaluacion import Evaluacion
from domain.practica_evaluacion.practica import Practica

UUID4_PATH = "domain.certificacion.codigo_qr.uuid4"


def _practica(estado=Practica.ESTADO_FINALIZADA, puntajes=(80,), practica_id=7):
    evaluaciones = [Evaluacion(practica_id=practica_id, puntaje=p) for p in puntajes]
    return Practica(id=practica_id, postulacion_id=1, practicante_id=2,
                    estado=estado, evaluaciones=evaluaciones)


def _datos_certificado():
    practicante = SimpleNamespace(nombres="Ana", apellidos="Quispe")
    convocatoria = SimpleNamespace(titulo="Practicas de Backend")
    return practicante, convocatoria


class TestCertificacionDominioServicio(unittest.TestCase):
    def setUp(self):
        self.servicio = CertificacionDominioServicio()
        self.practicante, self.convocatoria = _datos_certificado()

    def test_genera_certificado_para_practica_finalizada_y_aprobada(self):
        practica = _practica()
        certificado = self.servicio.generar_certificado(
            practica, self.practicante, self.convocatoria
        )
        self.assertEqual(7, certificado.practica_id)
        self.assertIsNotNone(certificado.codigo_qr)
        self.assertIsNotNone(certificado.documento)
        self.assertIn("Ana Quispe", certificado.documento.contenido)
        self.assertIn("Practicas de Backend", certificado.documento.contenido)

    def test_rechaza_practica_en_curso(self):
        practica = _practica(estado=Practica.ESTADO_EN_CURSO)
        with self.assertRaises(ValueError):
            self.servicio.generar_certificado(practica, self.practicante, self.convocatoria)

    def test_rechaza_practica_finalizada_sin_evaluacion_aprobada(self):
        practica = _practica(puntajes=(59.99,))
        with self.assertRaises(ValueError):
            self.servicio.generar_certificado(practica, self.practicante, self.convocatoria)

    def test_rechaza_practica_finalizada_sin_evaluaciones(self):
        practica = _practica(puntajes=())
        with self.assertRaises(ValueError):
            self.servicio.generar_certificado(practica, self.practicante, self.convocatoria)

    def test_acepta_si_al_menos_una_evaluacion_aprueba(self):
        practica = _practica(puntajes=(30, 60))
        certificado = self.servicio.generar_certificado(
            practica, self.practicante, self.convocatoria
        )
        self.assertIsNotNone(certificado)

    def test_verificar_codigo_qr_con_valor_correcto(self):
        certificado = self.servicio.generar_certificado(
            _practica(), self.practicante, self.convocatoria
        )
        self.assertTrue(
            self.servicio.verificar_codigo_qr(certificado, certificado.codigo_qr.valor)
        )

    def test_verificar_codigo_qr_rechaza_valor_alterado(self):
        certificado = self.servicio.generar_certificado(
            _practica(), self.practicante, self.convocatoria
        )
        self.assertFalse(
            self.servicio.verificar_codigo_qr(certificado, certificado.codigo_qr.valor + "x")
        )

    def test_verificar_codigo_qr_sin_qr_devuelve_false(self):
        self.assertFalse(self.servicio.verificar_codigo_qr(Certificado(practica_id=1), "X"))


class TestCodigoQR(unittest.TestCase):
    @patch(UUID4_PATH)
    def test_generar_usa_uuid_determinista(self, uuid4_mock):
        uuid4_mock.return_value = MagicMock(hex="abcdef1234567890")
        qr = CodigoQR.generar(5)
        self.assertEqual("CERT-5-abcdef12", qr.valor)
        self.assertEqual("/certificados/verificar/CERT-5-abcdef12", qr.url_verificacion)
        self.assertEqual(hashlib.sha256(b"CERT-5-abcdef12").hexdigest(), qr.hash_integridad)

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
        self.assertFalse(CodigoQR(valor=None, hash_integridad="h").verificar("x"))
        self.assertFalse(CodigoQR(valor="CERT-1-a", hash_integridad=None).verificar("CERT-1-a"))

    def test_verificar_rechaza_hash_manipulado(self):
        qr = CodigoQR(valor="CERT-1-a", hash_integridad="no-coincide")
        self.assertFalse(qr.verificar("CERT-1-a"))


class TestArchivoPDF(unittest.TestCase):
    def setUp(self):
        self.pdf = ArchivoPDF.crear(3, "contenido original")

    def test_crear_calcula_url_y_hash(self):
        self.assertEqual("/certificados/practica/3/pdf", self.pdf.url)
        self.assertEqual(
            hashlib.sha256(b"contenido original").hexdigest(), self.pdf.hash_integridad
        )

    def test_crear_sin_contenido_lanza_error(self):
        with self.assertRaises(ValueError):
            ArchivoPDF.crear(3, "")
        with self.assertRaises(ValueError):
            ArchivoPDF.crear(3, None)

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
    def test_generar_pdf_asigna_documento(self):
        certificado = Certificado(practica_id=4)
        documento = certificado.generar_pdf("texto")
        self.assertIs(documento, certificado.documento)
        self.assertEqual("/certificados/practica/4/pdf", documento.url)

    def test_verificar_integridad_sin_documento_devuelve_false(self):
        self.assertFalse(Certificado(practica_id=4).verificar_integridad("texto"))

    def test_verificar_integridad_delega_en_el_documento(self):
        certificado = Certificado(practica_id=4)
        certificado.generar_pdf("texto")
        self.assertTrue(certificado.verificar_integridad("texto"))
        self.assertFalse(certificado.verificar_integridad("otro"))


if __name__ == "__main__":
    unittest.main()
