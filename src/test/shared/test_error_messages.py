import unittest
from pathlib import Path

from shared.error_messages import POSTULACION_NO_ENCONTRADA

APPLICATION_DIR = Path(__file__).resolve().parents[2] / "main" / "application"
SERVICIOS = (
    "postulacion_application_service.py",
    "practica_application_service.py",
    "certificacion_application_service.py",
)


class TestMensajesError(unittest.TestCase):
    def test_constante_postulacion_no_encontrada(self):
        self.assertEqual(POSTULACION_NO_ENCONTRADA, "Postulación no encontrada")

    def test_servicios_no_repiten_el_literal_postulacion_no_encontrada(self):
        for nombre in SERVICIOS:
            with self.subTest(servicio=nombre):
                fuente = (APPLICATION_DIR / nombre).read_text(encoding="utf-8")
                self.assertNotIn('"Postulación no encontrada"', fuente)