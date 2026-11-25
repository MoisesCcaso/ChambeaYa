"""Protección CSRF y SECRET_KEY (hotspots de SonarQube S4502 y S2068)."""

import importlib
import os
import re
import unittest
from unittest.mock import patch

import config
from config import ProductionConfig
from bootstrap.app import create_app
from shared.database import db


class CsrfProtectionTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.app.config.update(SECRET_KEY="testing-secret", WTF_CSRF_ENABLED=True)
        with self.app.app_context():
            db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def _token(self):
        html = self.client.get("/ingresar").get_data(as_text=True)
        return re.search(r'<meta name="csrf-token" content="([^"]+)"', html).group(1)

    def test_post_sin_token_csrf_es_rechazado(self):
        response = self.client.post("/auth/login", json={"email": "a@b.com", "password": "x"})
        self.assertEqual(400, response.status_code)
        self.assertIn("Solicitud rechazada", response.get_json()["error"])

    def test_post_con_token_csrf_llega_a_la_ruta(self):
        response = self.client.post(
            "/auth/login",
            json={"email": "a@b.com", "password": "x"},
            headers={"X-CSRFToken": self._token()},
        )
        self.assertEqual(401, response.status_code)

    def test_api_client_gets_csrf_token_as_json_and_can_post(self):
        token_response = self.client.get("/auth/csrf-token")
        self.assertEqual(200, token_response.status_code)
        token = token_response.get_json()["csrf_token"]

        response = self.client.post(
            "/auth/login",
            json={"email": "a@b.com", "password": "x"},
            headers={"X-CSRFToken": token},
        )
        self.assertEqual(401, response.status_code)
        self.assertEqual({"error": "Credenciales inválidas"}, response.get_json())

    def test_get_no_requiere_token(self):
        self.assertEqual(200, self.client.get("/convocatorias").status_code)


class SecretKeyTest(unittest.TestCase):
    def test_produccion_sin_secret_key_falla(self):
        with patch.object(ProductionConfig, "SECRET_KEY", None):
            with self.assertRaisesRegex(RuntimeError, "SECRET_KEY"):
                create_app("production")

    def test_desarrollo_sin_secret_key_genera_una_aleatoria(self):
        entorno = {k: v for k, v in os.environ.items() if k != "SECRET_KEY"}
        try:
            with patch.dict(os.environ, entorno, clear=True), patch("dotenv.load_dotenv"):
                first_result = importlib.reload(config).DevelopmentConfig.SECRET_KEY
                second_result = importlib.reload(config).DevelopmentConfig.SECRET_KEY
                self.assertIsNone(config.ProductionConfig.SECRET_KEY)
        finally:
            importlib.reload(config)
        self.assertEqual(64, len(first_result))
        self.assertNotEqual(first_result, second_result)


if __name__ == "__main__":
    unittest.main()
