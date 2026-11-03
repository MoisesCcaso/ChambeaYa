"""I-03 - Pruebas del servicio de aplicación de usuarios (dobles autospec).

Código bajo prueba: application/usuario_application_service.py
"""
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import create_autospec, patch

from application.email_delivery_error import EmailDeliveryError
from application.usuario_application_service import UsuarioApplicationService
from domain.auth.autenticacion_dominio_servicio import AutenticacionDominioServicio
from domain.auth.i_auth_email_sender import IAuthEmailSender
from domain.auth.i_usuario_repository import IUsuarioRepository
from domain.auth.usuario import Usuario
from werkzeug.security import check_password_hash


class TestUsuarioService(unittest.TestCase):
    def setUp(self):
        self.repositorio = create_autospec(IUsuarioRepository, instance=True, spec_set=True)
        self.remitente = create_autospec(IAuthEmailSender, instance=True, spec_set=True)
        self.auth = AutenticacionDominioServicio()
        self.service = UsuarioApplicationService(
            usuario_repository=self.repositorio,
            autenticacion_dominio_servicio=self.auth,
            email_sender=self.remitente,
        )
        self.ahora = datetime(2030, 1, 1, tzinfo=timezone.utc)
        self._datetime_patcher = patch("domain.auth.autenticacion_dominio_servicio.datetime")
        self.datetime_mock = self._datetime_patcher.start()
        self.datetime_mock.now.return_value = self.ahora

    def tearDown(self):
        self._datetime_patcher.stop()

    def test_registro_normaliza_email_guarda_usuario_pendiente_y_envia_activacion(self):
        self.repositorio.find_by_email.return_value = None
        self.repositorio.save.side_effect = lambda usuario: usuario

        resultado = self.service.register_user(
            "  Ana.PEREZ@Example.COM ", "Abcdefg1", "Abcdefg1", Usuario.TIPO_PRACTICANTE,
        )

        self.assertEqual(resultado.email, "ana.perez@example.com")
        self.assertEqual(resultado.estado, Usuario.ESTADO_PENDIENTE)
        self.assertIsNotNone(resultado.activation_token)
        self.assertEqual(
            resultado.activation_token_expires_at, self.ahora + timedelta(hours=48)
        )
        self.repositorio.find_by_email.assert_called_once_with("ana.perez@example.com")
        self.repositorio.save.assert_called_once()
        self.remitente.send_activation.assert_called_once_with(
            "ana.perez@example.com", resultado.activation_token
        )

    def test_registro_email_duplicado_no_guarda_ni_envia(self):
        existente = Usuario(
            email="ana@test.local", password_hash="hash", tipo=Usuario.TIPO_EMPRESA
        )
        self.repositorio.find_by_email.return_value = existente

        with self.assertRaisesRegex(ValueError, "ya está registrado"):
            self.service.register_user(
                "ana@test.local", "Abcdefg1", "Abcdefg1", Usuario.TIPO_EMPRESA
            )

        self.repositorio.save.assert_not_called()
        self.remitente.send_activation.assert_not_called()

    def test_registro_contrasenas_no_coinciden_lanza_error(self):
        self.repositorio.find_by_email.return_value = None

        with self.assertRaisesRegex(ValueError, "no coinciden"):
            self.service.register_user(
                "ana@test.local", "Abcdefg1", "OtraClave1", Usuario.TIPO_PRACTICANTE
            )

        self.repositorio.save.assert_not_called()
        self.remitente.send_activation.assert_not_called()

    def test_registro_email_sender_lanza_email_delivery_error(self):
        self.repositorio.find_by_email.return_value = None
        self.repositorio.save.side_effect = lambda usuario: usuario
        self.remitente.send_activation.side_effect = EmailDeliveryError("fallo smtp")

        with self.assertRaises(EmailDeliveryError):
            self.service.register_user(
                "ana@test.local", "Abcdefg1", "Abcdefg1", Usuario.TIPO_PRACTICANTE
            )

        self.repositorio.save.assert_called_once()
        self.remitente.send_activation.assert_called_once()

    def test_authenticate_devuelve_usuario_credenciales_validas(self):
        password = "Abcdefg1"
        hash_real = self.auth.generar_password_hash(password)
        usuario = Usuario(
            email="ana@test.local",
            password_hash=hash_real,
            tipo=Usuario.TIPO_PRACTICANTE,
            estado=Usuario.ESTADO_ACTIVO,
        )
        self.repositorio.find_by_email.return_value = usuario

        resultado = self.service.authenticate("ana@test.local", password)

        self.assertIs(resultado, usuario)
        self.repositorio.find_by_email.assert_called_once_with("ana@test.local")
        self.assertTrue(check_password_hash(usuario.password_hash, password))

    def test_authenticate_rechaza_password_incorrecta(self):
        password = "Abcdefg1"
        hash_real = self.auth.generar_password_hash(password)
        usuario = Usuario(
            email="ana@test.local",
            password_hash=hash_real,
            tipo=Usuario.TIPO_PRACTICANTE,
            estado=Usuario.ESTADO_ACTIVO,
        )
        self.repositorio.find_by_email.return_value = usuario

        with self.assertRaisesRegex(ValueError, "Credenciales inválidas"):
            self.service.authenticate("ana@test.local", "OtraClave1")

    def test_authenticate_usuario_no_existente_lanza_error(self):
        self.repositorio.find_by_email.return_value = None

        with self.assertRaisesRegex(ValueError, "Credenciales inválidas"):
            self.service.authenticate("no-existe@test.local", "Abcdefg1")

    def test_recuperacion_usuario_inexistente_no_guarda_ni_envia(self):
        self.repositorio.find_by_email.return_value = None

        resultado = self.service.recover_password("no-existe@test.local")

        self.assertIsNone(resultado)
        self.repositorio.save.assert_not_called()
        self.remitente.send_password_reset.assert_not_called()

    def test_recuperacion_usuario_existente_token_dos_horas_guarda_y_envia(self):
        usuario = Usuario(
            email="ana@test.local",
            password_hash="hash",
            tipo=Usuario.TIPO_PRACTICANTE,
        )
        self.repositorio.find_by_email.return_value = usuario
        self.repositorio.save.side_effect = lambda u: u

        resultado = self.service.recover_password("ana@test.local")

        self.assertIs(resultado, usuario)
        self.assertIsNotNone(usuario.password_reset_token)
        self.assertEqual(
            usuario.password_reset_expires_at, self.ahora + timedelta(hours=2)
        )
        self.repositorio.save.assert_called_once_with(usuario)
        self.remitente.send_password_reset.assert_called_once_with(
            "ana@test.local", usuario.password_reset_token
        )

    def test_recuperacion_busca_email_normalizado(self):
        self.repositorio.find_by_email.return_value = None
        self.service.recover_password("  ANA@Example.COM ")
        self.repositorio.find_by_email.assert_called_once_with("ana@example.com")

    def test_resend_activation_usuario_inexistente_devuelve_none(self):
        self.repositorio.find_by_email.return_value = None

        resultado = self.service.resend_activation("no-existe@test.local")

        self.assertIsNone(resultado)
        self.repositorio.save.assert_not_called()
        self.remitente.send_activation.assert_not_called()

    def test_resend_activation_usuario_activo_devuelve_none(self):
        usuario = Usuario(
            email="ana@test.local",
            password_hash="hash",
            tipo=Usuario.TIPO_PRACTICANTE,
            estado=Usuario.ESTADO_ACTIVO,
        )
        self.repositorio.find_by_email.return_value = usuario

        resultado = self.service.resend_activation("ana@test.local")

        self.assertIsNone(resultado)
        self.repositorio.save.assert_not_called()
        self.remitente.send_activation.assert_not_called()

    def test_resend_activation_usuario_pendiente_envia_nuevo_token(self):
        usuario = Usuario(
            email="ana@test.local",
            password_hash="hash",
            tipo=Usuario.TIPO_PRACTICANTE,
            estado=Usuario.ESTADO_PENDIENTE,
        )
        self.repositorio.find_by_email.return_value = usuario
        self.repositorio.save.side_effect = lambda u: u

        resultado = self.service.resend_activation("ana@test.local")

        self.assertIs(resultado, usuario)
        self.assertIsNotNone(usuario.activation_token)
        self.assertEqual(
            usuario.activation_token_expires_at, self.ahora + timedelta(hours=48)
        )
        self.repositorio.save.assert_called_once_with(usuario)
        self.remitente.send_activation.assert_called_once_with(
            "ana@test.local", usuario.activation_token
        )

    def test_activate_account_token_invalido_lanza_error(self):
        self.repositorio.find_by_activation_token.return_value = None

        with self.assertRaisesRegex(ValueError, "Token de activación inválido"):
            self.service.activate_account("token-inexistente")

        self.repositorio.save.assert_not_called()

    def test_activate_account_token_expirado_lanza_error(self):
        usuario = Usuario(
            email="ana@test.local",
            password_hash="hash",
            tipo=Usuario.TIPO_PRACTICANTE,
            estado=Usuario.ESTADO_PENDIENTE,
            activation_token="token-valido",
            activation_token_expires_at=datetime(2020, 1, 1, tzinfo=timezone.utc),
        )
        self.repositorio.find_by_activation_token.return_value = usuario

        with self.assertRaisesRegex(ValueError, "Token de activación expirado"):
            self.service.activate_account("token-valido")

        self.repositorio.save.assert_not_called()

    def test_activate_account_token_valido_activa_y_guarda(self):
        usuario = Usuario(
            email="ana@test.local",
            password_hash="hash",
            tipo=Usuario.TIPO_PRACTICANTE,
            estado=Usuario.ESTADO_PENDIENTE,
            activation_token="token-valido",
            activation_token_expires_at=self.ahora + timedelta(hours=1),
        )
        self.repositorio.find_by_activation_token.return_value = usuario
        self.repositorio.save.side_effect = lambda u: u

        resultado = self.service.activate_account("token-valido")

        self.assertIs(resultado, usuario)
        self.assertEqual(usuario.estado, Usuario.ESTADO_ACTIVO)
        self.assertIsNone(usuario.activation_token)
        self.repositorio.save.assert_called_once_with(usuario)

    def test_reset_password_token_inexistente_lanza_error(self):
        self.repositorio.find_by_password_reset_token.return_value = None

        with self.assertRaisesRegex(ValueError, "Token de recuperación inválido"):
            self.service.reset_password("token-inexistente", "NuevaClave1")

        self.repositorio.save.assert_not_called()

    def test_reset_password_token_expirado_lanza_error(self):
        usuario = Usuario(
            email="ana@test.local",
            password_hash="hash",
            tipo=Usuario.TIPO_PRACTICANTE,
            estado=Usuario.ESTADO_ACTIVO,
            password_reset_token="token-valido",
            password_reset_expires_at=datetime(2020, 1, 1, tzinfo=timezone.utc),
        )
        self.repositorio.find_by_password_reset_token.return_value = usuario

        with self.assertRaisesRegex(ValueError, "Token de recuperación expirado"):
            self.service.reset_password("token-valido", "NuevaClave1")

        self.repositorio.save.assert_not_called()

    def test_reset_password_token_valido_actualiza_y_guarda(self):
        usuario = Usuario(
            email="ana@test.local",
            password_hash="hash-viejo",
            tipo=Usuario.TIPO_PRACTICANTE,
            estado=Usuario.ESTADO_ACTIVO,
            password_reset_token="token-valido",
            password_reset_expires_at=self.ahora + timedelta(hours=2),
        )
        self.repositorio.find_by_password_reset_token.return_value = usuario
        self.repositorio.save.side_effect = lambda u: u

        resultado = self.service.reset_password("token-valido", "NuevaClave1")

        self.assertIs(resultado, usuario)
        self.assertNotEqual(usuario.password_hash, "hash-viejo")
        self.assertTrue(check_password_hash(usuario.password_hash, "NuevaClave1"))
        self.assertIsNone(usuario.password_reset_token)
        self.repositorio.save.assert_called_once_with(usuario)

    def test_find_by_id_delega_en_el_repositorio(self):
        usuario = Usuario(id=7, email="ana@test.local", password_hash="hash")
        self.repositorio.find_by_id.return_value = usuario

        resultado = self.service.find_by_id(7)

        self.assertIs(resultado, usuario)
        self.repositorio.find_by_id.assert_called_once_with(7)

    def test_sin_repositorio_lanza_runtime_error(self):
        servicio = UsuarioApplicationService()
        with self.assertRaises(RuntimeError):
            servicio.register_user(
                "a@b.c", "Abcdefg1", "Abcdefg1", Usuario.TIPO_PRACTICANTE
            )

    def test_sin_remitente_lanza_runtime_error_en_registro(self):
        servicio = UsuarioApplicationService(usuario_repository=self.repositorio)
        self.repositorio.find_by_email.return_value = None

        with self.assertRaises(RuntimeError):
            servicio.register_user(
                "a@b.c", "Abcdefg1", "Abcdefg1", Usuario.TIPO_PRACTICANTE
            )

    def test_normalize_email_email_valido_devuelve_normalizado(self):
        resultado = self.service._normalize_email("  Ana.PEREZ@Example.COM ")
        self.assertEqual(resultado, "ana.perez@example.com")

    def test_normalize_email_vacio_lanza_error(self):
        with self.assertRaisesRegex(ValueError, "El email es obligatorio"):
            self.service._normalize_email("")

    def test_normalize_email_invalido_lanza_error(self):
        with self.assertRaisesRegex(ValueError, "El email no es válido"):
            self.service._normalize_email("no-es-un-email")


if __name__ == "__main__":
    unittest.main()
