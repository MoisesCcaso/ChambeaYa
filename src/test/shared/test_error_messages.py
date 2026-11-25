import unittest
from pathlib import Path

from shared.error_messages import JOB_APPLICATION_NOT_FOUND

APPLICATION_DIR = Path(__file__).resolve().parents[2] / "main" / "application"
SERVICES = (
    "postulacion_application_service.py",
    "practica_application_service.py",
    "certificacion_application_service.py",
)


class TestErrorMessages(unittest.TestCase):
    def test_job_application_not_found_constant(self):
        self.assertEqual(JOB_APPLICATION_NOT_FOUND, "Postulación no encontrada")

    def test_services_do_not_repeat_the_job_application_not_found_literal(self):
        for name in SERVICES:
            with self.subTest(service=name):
                source = (APPLICATION_DIR / name).read_text(encoding="utf-8")
                self.assertNotIn('"Postulación no encontrada"', source)