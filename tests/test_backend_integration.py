import io
import tempfile
import unittest

from frameworks.flask_mvc.app import create_app
from frameworks.sqlalchemy_orm.database import db


class BackendIntegrationTest(unittest.TestCase):
    def setUp(self):
        self.uploads = tempfile.TemporaryDirectory()
        self.app = create_app("testing")
        self.app.config.update(
            SECRET_KEY="testing-secret",
            UPLOAD_FOLDER=self.uploads.name,
        )
        with self.app.app_context():
            db.create_all()
        self.empresa = self.app.test_client()
        self.practicante = self.app.test_client()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
        self.uploads.cleanup()

    def request(self, client, method, path, expected, **kwargs):
        response = getattr(client, method)(path, **kwargs)
        self.assertEqual(
            expected,
            response.status_code,
            response.get_json(silent=True),
        )
        return response

    def register_activate_login(self, client, email, password, tipo):
        registered = self.request(
            client,
            "post",
            "/auth/register",
            201,
            json={"email": email, "password": password, "tipo": tipo},
        ).get_json()
        self.request(
            client,
            "post",
            "/auth/activate",
            200,
            json={"token": registered["activation_token"]},
        )
        self.request(
            client,
            "post",
            "/auth/login",
            200,
            json={"email": email, "password": password},
        )
        return registered

    def prepare_users_and_convocatoria(self):
        self.register_activate_login(
            self.empresa,
            "empresa@example.com",
            "Empresa123",
            "empresa",
        )
        self.request(
            self.empresa,
            "put",
            "/perfil/me/empresa",
            200,
            json={"razon_social": "Tech SAC", "ruc": "20131312955"},
        )
        convocatoria = self.request(
            self.empresa,
            "post",
            "/convocatorias",
            201,
            json={
                "titulo": "Backend Python",
                "descripcion": "Desarrollo de APIs Flask",
                "habilidades_requeridas": ["Python", "Flask"],
                "beneficios": ["Mentoría"],
            },
        ).get_json()
        self.request(
            self.empresa,
            "post",
            f"/convocatorias/{convocatoria['id']}/publicar",
            200,
        )

        self.register_activate_login(
            self.practicante,
            "practicante@example.com",
            "Student123",
            "practicante",
        )
        self.request(
            self.practicante,
            "put",
            "/perfil/me",
            200,
            json={
                "nombres": "Ana",
                "apellidos": "Torres",
                "habilidades": ["python", "FLASK"],
                "formacion_educativa": ["UNSA"],
            },
        )
        return convocatoria

    def test_complete_business_flow(self):
        convocatoria = self.prepare_users_and_convocatoria()
        convocatoria_id = convocatoria["id"]

        matches = self.request(
            self.practicante, "get", "/matching/sugerencias", 200
        ).get_json()
        self.assertEqual(100.0, matches[0]["score_compatibilidad"])

        postulacion = self.request(
            self.practicante,
            "post",
            f"/postulaciones/convocatorias/{convocatoria_id}",
            201,
        ).get_json()
        self.request(
            self.practicante,
            "post",
            f"/postulaciones/convocatorias/{convocatoria_id}",
            400,
        )
        self.request(
            self.empresa,
            "post",
            f"/postulaciones/{postulacion['id']}/seleccionar",
            200,
        )

        practica = self.request(
            self.empresa,
            "post",
            "/practicas",
            201,
            json={"postulacion_id": postulacion["id"]},
        ).get_json()
        practica_id = practica["id"]

        self.request(
            self.practicante,
            "post",
            f"/practicas/{practica_id}/entregables",
            201,
            data={"archivo": (io.BytesIO(b"%PDF test"), "informe.pdf")},
            content_type="multipart/form-data",
        )
        entregables = self.request(
            self.practicante,
            "get",
            f"/practicas/{practica_id}/entregables",
            200,
        ).get_json()
        archivo = self.request(
            self.practicante,
            "get",
            entregables[0]["archivo_url"],
            200,
        )
        self.assertEqual(b"%PDF test", archivo.data)
        archivo.close()

        self.request(
            self.empresa,
            "post",
            f"/practicas/{practica_id}/evaluar",
            201,
            json={"puntaje": 90},
        )
        self.request(
            self.empresa,
            "post",
            f"/practicas/{practica_id}/finalizar",
            200,
        )

        certificado = self.request(
            self.empresa,
            "post",
            f"/certificados/{practica_id}/emitir",
            201,
        ).get_json()
        codigo = certificado["codigo_qr"]["valor"]
        certificado_consultado = self.request(
            self.practicante,
            "get",
            f"/certificados/practica/{practica_id}",
            200,
        ).get_json()
        self.assertEqual(certificado["id"], certificado_consultado["id"])
        certificado_repetido = self.request(
            self.empresa,
            "post",
            f"/certificados/{practica_id}/emitir",
            200,
        ).get_json()
        self.assertEqual(certificado["id"], certificado_repetido["id"])
        verificacion = self.request(
            self.practicante,
            "get",
            f"/certificados/verificar/{codigo}",
            200,
        ).get_json()
        self.assertTrue(verificacion["valido"])
        self.assertEqual(
            "application/pdf",
            self.request(
                self.practicante,
                "get",
                certificado["documento"]["url"],
                200,
            ).mimetype,
        )
        self.assertEqual(
            "image/png",
            self.request(
                self.practicante,
                "get",
                certificado["codigo_qr"]["imagen_url"],
                200,
            ).mimetype,
        )

    def test_authorization_and_business_guards(self):
        convocatoria = self.prepare_users_and_convocatoria()
        postulacion = self.request(
            self.practicante,
            "post",
            f"/postulaciones/convocatorias/{convocatoria['id']}",
            201,
        ).get_json()
        self.request(
            self.empresa,
            "post",
            f"/postulaciones/{postulacion['id']}/seleccionar",
            200,
        )
        practica = self.request(
            self.empresa,
            "post",
            "/practicas",
            201,
            json={"postulacion_id": postulacion["id"]},
        ).get_json()

        self.request(
            self.empresa,
            "post",
            f"/practicas/{practica['id']}/finalizar",
            400,
        )
        notificaciones = self.request(
            self.practicante, "get", "/notificaciones", 200
        ).get_json()
        self.request(
            self.empresa,
            "put",
            f"/notificaciones/{notificaciones[0]['id']}/leer",
            400,
        )
        self.request(
            self.practicante,
            "put",
            f"/notificaciones/{notificaciones[0]['id']}/leer",
            200,
        )

    def test_auth_validation_and_password_reset(self):
        self.request(
            self.practicante,
            "post",
            "/auth/register",
            400,
            json={
                "email": "correo-invalido",
                "password": "12345678",
                "tipo": "practicante",
            },
        )
        registered = self.request(
            self.practicante,
            "post",
            "/auth/register",
            201,
            json={
                "email": "reset@example.com",
                "password": "Original123",
                "tipo": "practicante",
            },
        ).get_json()
        self.request(
            self.practicante,
            "post",
            "/auth/activate",
            200,
            json={"token": registered["activation_token"]},
        )
        recovered = self.request(
            self.practicante,
            "post",
            "/auth/recover-password",
            200,
            json={"email": "reset@example.com"},
        ).get_json()
        self.request(
            self.practicante,
            "post",
            "/auth/reset-password",
            200,
            json={
                "token": recovered["password_reset_token"],
                "new_password": "NuevaClave123",
            },
        )
        self.request(
            self.practicante,
            "post",
            "/auth/login",
            200,
            json={"email": "reset@example.com", "password": "NuevaClave123"},
        )


if __name__ == "__main__":
    unittest.main()
