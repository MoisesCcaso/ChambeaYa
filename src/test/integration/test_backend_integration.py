import io
import tempfile
import unittest
from unittest.mock import patch

from frameworks.flask_mvc.app import create_app
from frameworks.sqlalchemy_orm.database import db
from infrastructure.smtp_auth_email_sender import SmtpAuthEmailSender
from infrastructure.sqlalchemy_usuario_repository import SqlAlchemyUsuarioRepository


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
            json={
                "email": email,
                "password": password,
                "password_confirmation": password,
                "tipo": tipo,
            },
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
                "password_confirmation": "12345678",
                "tipo": "practicante",
            },
        )
        self.request(
            self.practicante,
            "post",
            "/auth/register",
            400,
            json={
                "email": "debil@example.com",
                "password": "sololetras",
                "password_confirmation": "sololetras",
                "tipo": "practicante",
            },
        )
        self.request(
            self.practicante,
            "post",
            "/auth/register",
            400,
            json={
                "email": "diferentes@example.com",
                "password": "Segura123",
                "password_confirmation": "Distinta123",
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
                "password_confirmation": "Original123",
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

    def test_activation_token_is_emailed_and_hidden_in_normal_mode(self):
        self.app.config["EXPOSE_AUTH_TOKENS"] = False
        registered = self.request(
            self.practicante,
            "post",
            "/auth/register",
            201,
            json={
                "email": "verificacion@example.com",
                "password": "Segura123",
                "password_confirmation": "Segura123",
                "tipo": "practicante",
            },
        ).get_json()
        self.assertNotIn("activation_token", registered)
        self.request(
            self.practicante,
            "post",
            "/auth/login",
            401,
            json={
                "email": "verificacion@example.com",
                "password": "Segura123",
            },
        )

        with self.app.app_context():
            first_token = (
                SqlAlchemyUsuarioRepository()
                .find_by_email("verificacion@example.com")
                .activation_token
            )
        resent = self.request(
            self.practicante,
            "post",
            "/auth/resend-activation",
            200,
            json={"email": "verificacion@example.com"},
        ).get_json()
        self.assertNotIn("activation_token", resent)
        with self.app.app_context():
            second_token = (
                SqlAlchemyUsuarioRepository()
                .find_by_email("verificacion@example.com")
                .activation_token
            )
        self.assertNotEqual(first_token, second_token)

        self.request(
            self.practicante,
            "post",
            "/auth/activate",
            200,
            json={"token": second_token},
        )
        self.request(
            self.practicante,
            "post",
            "/auth/login",
            200,
            json={
                "email": "verificacion@example.com",
                "password": "Segura123",
            },
        )

    def test_smtp_sender_builds_activation_email(self):
        sender = SmtpAuthEmailSender(
            delivery_mode="smtp",
            app_url="http://127.0.0.1:5000",
            server="smtp.example.com",
            port=587,
            username="mailer@example.com",
            password="smtp-secret",
            use_tls=True,
            sender="ChambeaYa <mailer@example.com>",
        )
        with patch(
            "infrastructure.smtp_auth_email_sender.smtplib.SMTP"
        ) as smtp_class:
            smtp = smtp_class.return_value.__enter__.return_value
            sender.send_activation("usuario@example.com", "token-seguro")

        smtp_class.assert_called_once_with(
            "smtp.example.com",
            587,
            timeout=15,
        )
        smtp.starttls.assert_called_once()
        smtp.login.assert_called_once_with("mailer@example.com", "smtp-secret")
        message = smtp.send_message.call_args.args[0]
        self.assertEqual("usuario@example.com", message["To"])
        plain_text = next(
            part.get_content()
            for part in message.walk()
            if part.get_content_type() == "text/plain"
        )
        self.assertIn(
            "http://127.0.0.1:5000/activar?token=token-seguro",
            plain_text,
        )

        self.app.config["MAIL_DELIVERY_MODE"] = "smtp"
        runner = self.app.test_cli_runner()
        with patch.object(SmtpAuthEmailSender, "send_test") as send_test:
            result = runner.invoke(
                args=["test-email", "--to", "destino@example.com"]
            )
        self.assertEqual(0, result.exit_code, result.output)
        self.assertIn("Correo de prueba enviado", result.output)
        send_test.assert_called_once_with("destino@example.com")

    def test_web_views_and_app_access(self):
        for path in (
            "/",
            "/ingresar",
            "/registro",
            "/activar",
            "/recuperar",
            "/restablecer",
            "/verificar-certificado",
        ):
            response = self.request(self.practicante, "get", path, 200)
            self.assertEqual("text/html", response.mimetype)

        anonymous_app = self.practicante.get("/app")
        self.assertEqual(302, anonymous_app.status_code)
        self.assertTrue(anonymous_app.location.endswith("/ingresar"))

        register_view = self.request(self.practicante, "get", "/registro", 200)
        self.assertIn(b'name="password_confirmation"', register_view.data)
        self.assertIn(b'id="password-requirements"', register_view.data)
        activate_view = self.request(self.practicante, "get", "/activar", 200)
        self.assertIn(b'id="activation-email-field"', activate_view.data)

        registered = self.register_activate_login(
            self.practicante,
            "vista@example.com",
            "Vista1234",
            "practicante",
        )
        self.assertIsNotNone(registered["id"])
        app_view = self.request(self.practicante, "get", "/app", 200)
        self.assertIn(b'id="app-shell"', app_view.data)
        self.assertIn(b'id="confirmation-dialog"', app_view.data)
        self.assertIn(b'data-filter="cancelada"', app_view.data)

        for asset in (
            "/static/css/app.css",
            "/static/js/common.js",
            "/static/js/auth.js",
            "/static/js/verify.js",
            "/static/js/app.js",
            "/static/icons.svg",
            "/static/img/chambeaYa_icon.ico",
            "/static/img/chambeaya-logo-horizontal.png",
            "/static/img/chambeaya-logo-square.png",
        ):
            response = self.request(self.practicante, "get", asset, 200)
            self.assertGreater(len(response.data), 0)
            response.close()

        app_script = self.request(
            self.practicante,
            "get",
            "/static/js/app.js",
            200,
        )
        for action in (
            b"data-delete-opening",
            b"data-duplicate-opening",
            b"data-reopen-opening",
            b"data-cancel-application",
            b"data-reconsider-candidate",
            b"data-delete-deliverable",
            b"data-delete-evaluation",
        ):
            self.assertIn(action, app_script.data)
        app_script.close()

    def test_demo_seed_is_repeatable_and_covers_main_views(self):
        self.app.config["DEMO_MODE"] = True
        login_view = self.request(self.practicante, "get", "/ingresar", 200)
        self.assertIn(b"data-demo-login", login_view.data)

        runner = self.app.test_cli_runner()
        first_seed = runner.invoke(args=["seed-demo"])
        self.assertEqual(0, first_seed.exit_code, first_seed.output)
        second_seed = runner.invoke(args=["seed-demo"])
        self.assertEqual(0, second_seed.exit_code, second_seed.output)
        self.assertIn("no se duplicaron datos", second_seed.output)

        self.request(
            self.practicante,
            "post",
            "/auth/login",
            200,
            json={
                "email": "practicante@demo.local",
                "password": "Demo1234",
            },
        )
        self.request(
            self.empresa,
            "post",
            "/auth/login",
            200,
            json={
                "email": "empresa@demo.local",
                "password": "Demo1234",
            },
        )

        self.assertGreaterEqual(
            len(self.request(self.practicante, "get", "/convocatorias", 200).get_json()),
            3,
        )
        self.assertEqual(
            2,
            len(self.request(self.practicante, "get", "/postulaciones/me", 200).get_json()),
        )
        self.assertGreaterEqual(
            len(self.request(self.practicante, "get", "/matching/sugerencias", 200).get_json()),
            2,
        )
        self.assertEqual(
            1,
            len(self.request(self.practicante, "get", "/practicas", 200).get_json()),
        )
        self.assertGreaterEqual(
            len(self.request(self.empresa, "get", "/convocatorias/mis", 200).get_json()),
            4,
        )

    def test_new_company_completes_profile_before_creating_openings(self):
        self.register_activate_login(
            self.empresa,
            "empresa-nueva@example.com",
            "Empresa123",
            "empresa",
        )

        missing_profile = self.request(self.empresa, "get", "/perfil/me", 404)
        self.assertEqual(
            "Perfil de empresa no encontrado",
            missing_profile.get_json()["error"],
        )
        self.request(
            self.empresa,
            "post",
            "/convocatorias",
            400,
            json={"titulo": "Convocatoria prematura"},
        )

        company = self.request(
            self.empresa,
            "put",
            "/perfil/me/empresa",
            200,
            json={
                "razon_social": "Empresa Nueva S.A.C.",
                "ruc": "20100070970",
            },
        ).get_json()
        self.assertTrue(company["verificada"])

        opening = self.request(
            self.empresa,
            "post",
            "/convocatorias",
            201,
            json={
                "titulo": "Practicante de sistemas",
                "descripcion": "Apoyo al equipo de desarrollo.",
                "habilidades_requeridas": ["Python"],
                "beneficios": ["Mentoría"],
            },
        ).get_json()
        self.assertEqual("borrador", opening["estado"])

    def test_profile_lists_and_identity_can_be_cleared(self):
        self.register_activate_login(
            self.practicante,
            "perfil-editable@example.com",
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
                "dni": "12345678",
                "carnet_universitario": "20260001",
                "habilidades": ["Python", "SQL"],
                "formacion_educativa": ["UNSA"],
            },
        )
        updated = self.request(
            self.practicante,
            "put",
            "/perfil/me",
            200,
            json={
                "nombres": "Ana",
                "apellidos": "Torres",
                "dni": None,
                "carnet_universitario": None,
                "habilidades": ["Python"],
                "formacion_educativa": [],
            },
        ).get_json()
        self.assertEqual(["Python"], updated["habilidades"])
        self.assertEqual([], updated["formacion_educativa"])
        self.assertIsNone(updated["dni"])
        self.assertIsNone(updated["carnet_universitario"])
        self.assertFalse(updated["identidad_verificada"])

    def test_opening_management_actions(self):
        opening = self.prepare_users_and_convocatoria()
        opening_id = opening["id"]

        self.request(
            self.empresa,
            "delete",
            f"/convocatorias/{opening_id}",
            400,
        )
        closed = self.request(
            self.empresa,
            "post",
            f"/convocatorias/{opening_id}/cerrar",
            200,
        ).get_json()
        self.assertEqual("cerrada", closed["estado"])
        reopened = self.request(
            self.empresa,
            "post",
            f"/convocatorias/{opening_id}/reabrir",
            200,
        ).get_json()
        self.assertEqual("publicada", reopened["estado"])
        self.assertIsNone(reopened["fecha_cierre"])

        duplicate = self.request(
            self.empresa,
            "post",
            f"/convocatorias/{opening_id}/duplicar",
            201,
        ).get_json()
        self.assertEqual("borrador", duplicate["estado"])
        self.assertEqual("Copia de Backend Python", duplicate["titulo"])
        self.assertEqual(opening["habilidades_requeridas"], duplicate["habilidades_requeridas"])
        deleted = self.request(
            self.empresa,
            "delete",
            f"/convocatorias/{duplicate['id']}",
            200,
        ).get_json()
        self.assertEqual(duplicate["id"], deleted["id"])
        self.request(
            self.empresa,
            "get",
            f"/convocatorias/{duplicate['id']}",
            404,
        )

    def test_application_withdrawal_and_candidate_reconsideration(self):
        opening = self.prepare_users_and_convocatoria()
        opening_id = opening["id"]
        first = self.request(
            self.practicante,
            "post",
            f"/postulaciones/convocatorias/{opening_id}",
            201,
        ).get_json()
        cancelled = self.request(
            self.practicante,
            "post",
            f"/postulaciones/{first['id']}/cancelar",
            200,
        ).get_json()
        self.assertEqual("cancelada", cancelled["estado"])
        reactivated = self.request(
            self.practicante,
            "post",
            f"/postulaciones/convocatorias/{opening_id}",
            201,
        ).get_json()
        self.assertEqual(first["id"], reactivated["id"])
        self.assertEqual("pendiente", reactivated["estado"])

        second_client = self.app.test_client()
        self.register_activate_login(
            second_client,
            "segundo-practicante@example.com",
            "Student123",
            "practicante",
        )
        self.request(
            second_client,
            "put",
            "/perfil/me",
            200,
            json={
                "nombres": "Luis",
                "apellidos": "Ramos",
                "habilidades": ["Python"],
            },
        )
        second = self.request(
            second_client,
            "post",
            f"/postulaciones/convocatorias/{opening_id}",
            201,
        ).get_json()

        self.request(
            self.empresa,
            "post",
            f"/postulaciones/{first['id']}/seleccionar",
            200,
        )
        reconsidered = self.request(
            self.empresa,
            "post",
            f"/postulaciones/{second['id']}/reconsiderar",
            200,
        ).get_json()
        self.assertEqual("pendiente", reconsidered["estado"])
        self.request(
            self.empresa,
            "post",
            f"/postulaciones/{second['id']}/seleccionar",
            200,
        )
        candidates = self.request(
            self.empresa,
            "get",
            f"/postulaciones/convocatorias/{opening_id}",
            200,
        ).get_json()
        states = {item["id"]: item["estado"] for item in candidates}
        self.assertEqual("rechazada", states[first["id"]])
        self.assertEqual("seleccionada", states[second["id"]])

        self.request(
            self.empresa,
            "post",
            "/practicas",
            201,
            json={"postulacion_id": second["id"]},
        )
        self.request(
            self.empresa,
            "post",
            f"/postulaciones/{second['id']}/reconsiderar",
            400,
        )

    def test_deliverables_and_evaluations_can_be_deleted_in_progress(self):
        opening = self.prepare_users_and_convocatoria()
        application = self.request(
            self.practicante,
            "post",
            f"/postulaciones/convocatorias/{opening['id']}",
            201,
        ).get_json()
        self.request(
            self.empresa,
            "post",
            f"/postulaciones/{application['id']}/seleccionar",
            200,
        )
        practice = self.request(
            self.empresa,
            "post",
            "/practicas",
            201,
            json={"postulacion_id": application["id"]},
        ).get_json()
        practice_id = practice["id"]

        uploaded = self.request(
            self.practicante,
            "post",
            f"/practicas/{practice_id}/entregables",
            201,
            data={"archivo": (io.BytesIO(b"%PDF removable"), "borrador.pdf")},
            content_type="multipart/form-data",
        ).get_json()
        deliverable_id = self.request(
            self.practicante,
            "get",
            f"/practicas/{practice_id}/entregables",
            200,
        ).get_json()[0]["id"]
        evaluation = self.request(
            self.empresa,
            "post",
            f"/practicas/{practice_id}/evaluar",
            201,
            json={"puntaje": 80},
        )
        self.assertEqual("EN_CURSO", uploaded["estado"])
        evaluation_id = self.request(
            self.empresa,
            "get",
            f"/practicas/{practice_id}/evaluaciones",
            200,
        ).get_json()[0]["id"]
        self.assertEqual(201, evaluation.status_code)

        self.request(
            self.empresa,
            "delete",
            f"/practicas/{practice_id}/entregables/{deliverable_id}",
            400,
        )
        self.request(
            self.practicante,
            "delete",
            f"/practicas/{practice_id}/evaluaciones/{evaluation_id}",
            400,
        )
        self.request(
            self.practicante,
            "delete",
            f"/practicas/{practice_id}/entregables/{deliverable_id}",
            200,
        )
        self.request(
            self.empresa,
            "delete",
            f"/practicas/{practice_id}/evaluaciones/{evaluation_id}",
            200,
        )
        self.assertEqual(
            [],
            self.request(
                self.practicante,
                "get",
                f"/practicas/{practice_id}/entregables",
                200,
            ).get_json(),
        )
        self.assertEqual(
            [],
            self.request(
                self.empresa,
                "get",
                f"/practicas/{practice_id}/evaluaciones",
                200,
            ).get_json(),
        )

        self.request(
            self.practicante,
            "post",
            f"/practicas/{practice_id}/entregables",
            201,
            data={"archivo": (io.BytesIO(b"%PDF final"), "final.pdf")},
            content_type="multipart/form-data",
        )
        final_deliverable_id = self.request(
            self.practicante,
            "get",
            f"/practicas/{practice_id}/entregables",
            200,
        ).get_json()[0]["id"]
        self.request(
            self.empresa,
            "post",
            f"/practicas/{practice_id}/evaluar",
            201,
            json={"puntaje": 90},
        )
        final_evaluation_id = self.request(
            self.empresa,
            "get",
            f"/practicas/{practice_id}/evaluaciones",
            200,
        ).get_json()[0]["id"]
        self.request(
            self.empresa,
            "post",
            f"/practicas/{practice_id}/finalizar",
            200,
        )
        self.request(
            self.practicante,
            "delete",
            f"/practicas/{practice_id}/entregables/{final_deliverable_id}",
            400,
        )
        self.request(
            self.empresa,
            "delete",
            f"/practicas/{practice_id}/evaluaciones/{final_evaluation_id}",
            400,
        )


if __name__ == "__main__":
    unittest.main()
