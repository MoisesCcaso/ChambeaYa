import unittest

from bootstrap.app import create_app
from certification.presentation.certificate_routes import build_verification_url


class CertificateQrUrlTest(unittest.TestCase):
    def test_qr_links_to_verification_view_with_codigo_param(self):
        app = create_app("testing")
        app.config["APP_URL"] = "http://cliente.test/"
        with app.app_context():
            self.assertEqual(
                "http://cliente.test/verificar-certificado?codigo=ABC-123",
                build_verification_url("ABC-123"),
            )
