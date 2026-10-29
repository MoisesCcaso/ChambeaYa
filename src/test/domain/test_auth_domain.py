"""Pruebas unitarias de las reglas del dominio de autenticación."""

import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from werkzeug.security import check_password_hash

from domain.auth.autenticacion_dominio_servicio import AutenticacionDominioServicio
from domain.auth.token_recuperacion import TokenRecuperacion
from domain.auth.usuario import Usuario


class UsuarioTest(unittest.TestCase):
    def test_registrar_usuario_valido_devuelve_el_mismo_usuario(self):
        usuario = Usuario(
            email="persona@example.com",
            password_hash="hash-seguro",
            tipo=Usuario.TIPO_PRACTICANTE,
        )

        resultado = usuario.registrar()

        self.assertIs(resultado, usuario)
        self.assertEqual(usuario.estado, Usuario.ESTADO_PENDIENTE)

    def test_registrar_rechaza_email_ausente(self):
        usuario = Usuario(password_hash="hash-seguro", tipo=Usuario.TIPO_EMPRESA)

        with self.assertRaisesRegex(ValueError, "El email es obligatorio"):
            usuario.registrar()

    def test_registrar_rechaza_password_ausente(self):
        usuario = Usuario(email="persona@example.com", tipo=Usuario.TIPO_EMPRESA)

        with self.assertRaisesRegex(ValueError, "La contraseña es obligatoria"):
            usuario.registrar()

    def test_registrar_rechaza_tipo_no_permitido(self):
        usuario = Usuario(
            email="persona@example.com",
            password_hash="hash-seguro",
            tipo="administrador",
        )

        with self.assertRaisesRegex(ValueError, "El tipo de usuario no es válido"):
            usuario.registrar()

    def test_login_rechaza_usuario_no_activo(self):
        usuario = Usuario(estado=Usuario.ESTADO_PENDIENTE)

        with self.assertRaisesRegex(ValueError, "La cuenta no está activa"):
            usuario.login()

    def test_login_devuelve_usuario_activo(self):
        usuario = Usuario(estado=Usuario.ESTADO_ACTIVO)

        self.assertIs(usuario.login(), usuario)

    def test_activar_cambia_estado_y_limpia_token_de_activacion(self):
        usuario = Usuario(
            activation_token="token-activacion",
            activation_token_expires_at=datetime.now(timezone.utc),
        )

        resultado = usuario.activar()

        self.assertIs(resultado, usuario)
        self.assertEqual(usuario.estado, Usuario.ESTADO_ACTIVO)
        self.assertIsNone(usuario.activation_token)
        self.assertIsNone(usuario.activation_token_expires_at)

    def test_asignar_tokens_guarda_valor_y_expiracion(self):
        expiracion = datetime(2030, 1, 1, tzinfo=timezone.utc)
        usuario = Usuario()
        token_activacion = TokenRecuperacion("activacion", expiracion)
        token_recuperacion = TokenRecuperacion("recuperacion", expiracion)

        self.assertIs(usuario.asignar_token_activacion(token_activacion), usuario)
        self.assertIs(usuario.asignar_token_recuperacion(token_recuperacion), usuario)

        self.assertEqual(usuario.activation_token, "activacion")
        self.assertEqual(usuario.activation_token_expires_at, expiracion)
        self.assertEqual(usuario.password_reset_token, "recuperacion")
        self.assertEqual(usuario.password_reset_expires_at, expiracion)

    def test_actualizar_password_guarda_hash_y_limpia_token_de_recuperacion(self):
        usuario = Usuario(
            password_reset_token="token-anterior",
            password_reset_expires_at=datetime(2030, 1, 1, tzinfo=timezone.utc),
        )

        resultado = usuario.actualizar_password("nuevo-hash")

        self.assertIs(resultado, usuario)
        self.assertEqual(usuario.password_hash, "nuevo-hash")
        self.assertIsNone(usuario.password_reset_token)
        self.assertIsNone(usuario.password_reset_expires_at)

    def test_actualizar_password_rechaza_hash_vacio(self):
        usuario = Usuario()

        with self.assertRaisesRegex(ValueError, "La contraseña es obligatoria"):
            usuario.actualizar_password("")


class AutenticacionDominioServicioTest(unittest.TestCase):
    def setUp(self):
        self.servicio = AutenticacionDominioServicio()

    def test_generar_password_hash_acepta_limites_de_8_y_128_caracteres(self):
        passwords = ("Abcdef1x", "A" + "b" * 126 + "1")

        for password in passwords:
            with self.subTest(longitud=len(password)):
                password_hash = self.servicio.generar_password_hash(password)
                self.assertNotEqual(password_hash, password)
                self.assertTrue(check_password_hash(password_hash, password))

    def test_generar_password_hash_rechaza_password_vacio_o_menor_a_8(self):
        for password in (None, "Abcde1x"):
            with self.subTest(password=password):
                with self.assertRaises(ValueError):
                    self.servicio.generar_password_hash(password)

    def test_generar_password_hash_rechaza_mas_de_128_caracteres(self):
        password = "A" + "b" * 127 + "1"

        with self.assertRaisesRegex(ValueError, "no puede superar 128"):
            self.servicio.generar_password_hash(password)

    def test_generar_password_hash_exige_minuscula_mayuscula_y_digito(self):
        passwords_invalidas = ("ABCDEFG1", "abcdefg1", "Abcdefgh")

        for password in passwords_invalidas:
            with self.subTest(password=password):
                with self.assertRaises(ValueError):
                    self.servicio.generar_password_hash(password)

    def test_autenticar_devuelve_false_si_no_hay_usuario(self):
        self.assertFalse(self.servicio.autenticar(None, "Abcdefg1"))

    def test_autenticar_comprueba_password_de_usuario_activo(self):
        password = "Abcdefg1"
        usuario = Usuario(
            estado=Usuario.ESTADO_ACTIVO,
            password_hash=self.servicio.generar_password_hash(password),
        )

        self.assertTrue(self.servicio.autenticar(usuario, password))
        self.assertFalse(self.servicio.autenticar(usuario, "OtraClave1"))

    def test_autenticar_rechaza_usuario_inactivo(self):
        usuario = Usuario(
            estado=Usuario.ESTADO_PENDIENTE,
            password_hash=self.servicio.generar_password_hash("Abcdefg1"),
        )

        with self.assertRaisesRegex(ValueError, "La cuenta no está activa"):
            self.servicio.autenticar(usuario, "Abcdefg1")

    def test_generar_token_crea_valor_y_expiracion_con_duracion_solicitada(self):
        antes = datetime.now(timezone.utc)

        token = self.servicio.generar_token(horas_vigencia=2)

        despues = datetime.now(timezone.utc)
        self.assertTrue(token.valor)
        self.assertGreaterEqual(token.expiracion, antes + timedelta(hours=2))
        self.assertLessEqual(token.expiracion, despues + timedelta(hours=2))

    def test_validar_token_delega_en_la_vigencia_del_token(self):
        ahora = datetime(2030, 1, 1, tzinfo=timezone.utc)
        vigente = ahora + timedelta(minutes=1)
        vencido = ahora - timedelta(minutes=1)

        with patch("domain.auth.token_recuperacion.datetime") as datetime_mock:
            datetime_mock.now.return_value = ahora
            self.assertTrue(self.servicio.validar_token("token", vigente))
            self.assertFalse(self.servicio.validar_token("token", vencido))


class TokenRecuperacionTest(unittest.TestCase):
    def test_esta_vigente_para_expiracion_futura(self):
        ahora = datetime(2030, 1, 1, tzinfo=timezone.utc)

        with patch("domain.auth.token_recuperacion.datetime") as datetime_mock:
            datetime_mock.now.return_value = ahora
            self.assertTrue(TokenRecuperacion("token", ahora + timedelta(seconds=1)).esta_vigente())

    def test_esta_vigente_devuelve_false_para_token_vencido(self):
        ahora = datetime(2030, 1, 1, tzinfo=timezone.utc)

        with patch("domain.auth.token_recuperacion.datetime") as datetime_mock:
            datetime_mock.now.return_value = ahora
            self.assertFalse(TokenRecuperacion("token", ahora - timedelta(seconds=1)).esta_vigente())

    def test_esta_vigente_devuelve_false_si_falta_valor_o_expiracion(self):
        self.assertFalse(TokenRecuperacion(None, datetime.now(timezone.utc)).esta_vigente())
        self.assertFalse(TokenRecuperacion("token", None).esta_vigente())

    def test_esta_vigente_interpreta_expiracion_sin_zona_como_utc(self):
        ahora = datetime(2030, 1, 1, tzinfo=timezone.utc)
        expiracion_sin_zona = (ahora + timedelta(seconds=1)).replace(tzinfo=None)

        with patch("domain.auth.token_recuperacion.datetime") as datetime_mock:
            datetime_mock.now.return_value = ahora
            self.assertTrue(TokenRecuperacion("token", expiracion_sin_zona).esta_vigente())


if __name__ == "__main__":
    unittest.main()
