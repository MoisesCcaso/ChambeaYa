"""I-06 - Pruebas unitarias del servicio de aplicación de perfil con dobles (autospec).

Código bajo prueba:
- src/main/application/perfil_application_service.py
"""

import unittest
from unittest.mock import create_autospec

from application.perfil_application_service import PerfilApplicationService
from domain.auth.i_usuario_repository import IUsuarioRepository
from domain.auth.usuario import Usuario
from domain.perfil.empresa import Empresa
from domain.perfil.i_perfil_repository import IPerfilRepository
from domain.perfil.practicante import Practicante
from domain.perfil.ruc import RUC


class TestPerfilService(unittest.TestCase):
    """Pruebas aisladas de PerfilApplicationService usando autospecs de sus repositorios."""

    def setUp(self):
        self.perfil_repository = create_autospec(
            IPerfilRepository, instance=True, spec_set=True
        )
        self.usuario_repository = create_autospec(
            IUsuarioRepository, instance=True, spec_set=True
        )
        self.service = PerfilApplicationService(
            perfil_repository=self.perfil_repository,
            usuario_repository=self.usuario_repository,
        )

    def _usuario_practicante_activo(self, usuario_id=10):
        return Usuario(
            id=usuario_id,
            email="practicante@test.local",
            password_hash="hash",
            tipo=Usuario.TIPO_PRACTICANTE,
            estado=Usuario.ESTADO_ACTIVO,
        )

    def _usuario_empresa_activo(self, usuario_id=20):
        return Usuario(
            id=usuario_id,
            email="empresa@test.local",
            password_hash="hash",
            tipo=Usuario.TIPO_EMPRESA,
            estado=Usuario.ESTADO_ACTIVO,
        )

    def test_update_practicante_activo_crea_o_actualiza_verifica_identidad_y_guarda(self):
        usuario = self._usuario_practicante_activo(usuario_id=10)
        self.usuario_repository.find_by_id.return_value = usuario
        self.perfil_repository.find_practicante_by_user_id.return_value = None
        self.perfil_repository.save_practicante.side_effect = lambda p: p

        datos = {
            "nombres": "Ana",
            "apellidos": "Torres",
            "dni": "  71234567  ",
            "carnet_universitario": "  20214567  ",
            "habilidades": [" Python ", "SQL", "Python"],
            "formacion_educativa": [" UNSA ", "Inglés"],
        }

        resultado = self.service.update_practicante(10, datos)

        self.usuario_repository.find_by_id.assert_called_once_with(10)
        self.perfil_repository.find_practicante_by_user_id.assert_called_once_with(10)
        self.perfil_repository.save_practicante.assert_called_once()

        practicante_guardado = self.perfil_repository.save_practicante.call_args[0][0]
        self.assertIs(resultado, practicante_guardado)
        self.assertEqual(practicante_guardado.usuario_id, 10)
        self.assertEqual(practicante_guardado.nombres, "Ana")
        self.assertEqual(practicante_guardado.apellidos, "Torres")
        self.assertEqual(practicante_guardado.dni, "71234567")
        self.assertEqual(practicante_guardado.carnet_universitario, "20214567")
        self.assertEqual(practicante_guardado.habilidades, ["Python", "SQL"])
        self.assertEqual(practicante_guardado.formacion_educativa, ["UNSA", "Inglés"])
        self.assertTrue(practicante_guardado.identidad_verificada)
        # 2 habilidades (10) + 2 formaciones (10) + identidad verificada (25) = 45.0
        self.assertEqual(practicante_guardado.score_reputacion, 45.0)

    def test_update_practicante_existente_limpia_identidad_cuando_se_envia_vacia(self):
        usuario = self._usuario_practicante_activo(usuario_id=10)
        existente = Practicante(
            id=5,
            usuario_id=10,
            nombres="Ana",
            apellidos="Torres",
            dni="71234567",
            identidad_verificada=True,
            score_reputacion=25.0,
        )
        self.usuario_repository.find_by_id.return_value = usuario
        self.perfil_repository.find_practicante_by_user_id.return_value = existente
        self.perfil_repository.save_practicante.side_effect = lambda p: p

        resultado = self.service.update_practicante(
            10, {"dni": "   ", "carnet_universitario": None}
        )

        self.assertIs(resultado, existente)
        self.assertIsNone(existente.dni)
        self.assertIsNone(existente.carnet_universitario)
        self.assertFalse(existente.identidad_verificada)
        self.assertEqual(existente.score_reputacion, 0.0)
        self.perfil_repository.save_practicante.assert_called_once_with(existente)

    def test_update_practicante_rechaza_usuario_inexistente_antes_de_guardar(self):
        self.usuario_repository.find_by_id.return_value = None

        with self.assertRaisesRegex(ValueError, "Usuario no encontrado"):
            self.service.update_practicante(99, {"nombres": "Ana"})

        self.usuario_repository.find_by_id.assert_called_once_with(99)
        self.perfil_repository.find_practicante_by_user_id.assert_not_called()
        self.perfil_repository.save_practicante.assert_not_called()

    def test_update_practicante_rechaza_usuario_inactivo_antes_de_guardar(self):
        usuario_inactivo = Usuario(
            id=10,
            email="pendiente@test.local",
            password_hash="hash",
            tipo=Usuario.TIPO_PRACTICANTE,
            estado=Usuario.ESTADO_PENDIENTE,
        )
        self.usuario_repository.find_by_id.return_value = usuario_inactivo

        with self.assertRaisesRegex(ValueError, "La cuenta no está activa"):
            self.service.update_practicante(10, {"nombres": "Ana"})

        self.usuario_repository.find_by_id.assert_called_once_with(10)
        self.perfil_repository.find_practicante_by_user_id.assert_not_called()
        self.perfil_repository.save_practicante.assert_not_called()

    def test_update_practicante_rechaza_usuario_tipo_empresa_antes_de_guardar(self):
        usuario_empresa = self._usuario_empresa_activo(usuario_id=20)
        self.usuario_repository.find_by_id.return_value = usuario_empresa

        with self.assertRaisesRegex(ValueError, "El usuario no es practicante"):
            self.service.update_practicante(20, {"nombres": "Ana"})

        self.usuario_repository.find_by_id.assert_called_once_with(20)
        self.perfil_repository.find_practicante_by_user_id.assert_not_called()
        self.perfil_repository.save_practicante.assert_not_called()

    def test_get_practicante_profile_y_operaciones_de_habilidad_formacion_e_identidad(self):
        usuario = self._usuario_practicante_activo(usuario_id=10)
        self.usuario_repository.find_by_id.return_value = usuario
        self.perfil_repository.find_practicante_by_user_id.return_value = None
        self.perfil_repository.save_practicante.side_effect = lambda p: p

        self.assertIsNone(self.service.get_practicante_profile(10))

        con_habilidad = self.service.add_habilidad(10, "  Python  ")
        self.assertEqual(con_habilidad.habilidades, ["Python"])
        self.assertEqual(con_habilidad.score_reputacion, 5.0)

        self.perfil_repository.find_practicante_by_user_id.return_value = con_habilidad
        con_formacion = self.service.add_formacion(10, "  UNSA  ")
        self.assertEqual(con_formacion.formacion_educativa, ["UNSA"])
        self.assertEqual(con_formacion.score_reputacion, 10.0)

        con_identidad = self.service.register_identity(
            10, dni="71234567", carnet_universitario="20210001"
        )
        self.assertTrue(con_identidad.identidad_verificada)
        self.assertEqual(con_identidad.score_reputacion, 35.0)

    def test_update_y_get_empresa_profile_y_guardas_de_empresa(self):
        usuario_empresa = self._usuario_empresa_activo(usuario_id=20)
        self.usuario_repository.find_by_id.return_value = usuario_empresa
        self.perfil_repository.find_empresa_by_user_id.return_value = None
        self.perfil_repository.save_empresa.side_effect = lambda e: e

        # Guardado válido de empresa
        empresa_guardada = self.service.update_empresa(
            20, {"razon_social": "  Acme S.A.C.  ", "ruc": "20100070970"}
        )
        self.assertEqual(empresa_guardada.usuario_id, 20)
        self.assertEqual(empresa_guardada.razon_social, "Acme S.A.C.")
        self.assertIsInstance(empresa_guardada.ruc, RUC)
        self.assertTrue(empresa_guardada.verificada)
        self.perfil_repository.save_empresa.assert_called_once_with(empresa_guardada)

        self.perfil_repository.find_empresa_by_user_id.return_value = empresa_guardada
        self.assertIs(self.service.get_empresa_profile(20), empresa_guardada)

        # Actualizar empresa ya existente
        existente = Empresa(
            id=3, usuario_id=20, razon_social="Anterior S.A.C.", ruc=RUC("20100070970")
        )
        self.perfil_repository.find_empresa_by_user_id.return_value = existente
        actualizada = self.service.update_empresa(
            20, {"razon_social": "Nueva Razón S.A.C."}
        )
        self.assertIs(actualizada, existente)
        self.assertEqual(actualizada.razon_social, "Nueva Razón S.A.C.")
        self.assertTrue(actualizada.verificada)

        # Razón social vacía
        with self.assertRaisesRegex(ValueError, "La razón social es obligatoria"):
            self.service.update_empresa(20, {"razon_social": "   ", "ruc": "20100070970"})

        # RUC inválido
        with self.assertRaisesRegex(ValueError, "El RUC no es válido"):
            self.service.update_empresa(
                20, {"razon_social": "Acme S.A.C.", "ruc": "20100070975"}
            )

        # Guardas de usuario para empresa: inexistente, tipo practicante, inactivo
        self.usuario_repository.find_by_id.return_value = None
        with self.assertRaisesRegex(ValueError, "Usuario no encontrado"):
            self.service.update_empresa(99, {"razon_social": "X", "ruc": "20100070970"})

        self.usuario_repository.find_by_id.return_value = self._usuario_practicante_activo(10)
        with self.assertRaisesRegex(ValueError, "El usuario no es empresa"):
            self.service.update_empresa(10, {"razon_social": "X", "ruc": "20100070970"})

        self.usuario_repository.find_by_id.return_value = Usuario(
            id=20,
            email="emp@test.local",
            password_hash="h",
            tipo=Usuario.TIPO_EMPRESA,
            estado=Usuario.ESTADO_PENDIENTE,
        )
        with self.assertRaisesRegex(ValueError, "La cuenta no está activa"):
            self.service.update_empresa(20, {"razon_social": "X", "ruc": "20100070970"})

    def test_verify_profile_y_get_reputation_score(self):
        self.perfil_repository.find_practicante_by_user_id.return_value = None
        with self.assertRaisesRegex(ValueError, "Perfil de practicante no encontrado"):
            self.service.verify_profile(10)
        self.assertEqual(self.service.get_reputation_score(10), 0.0)

        practicante = Practicante(
            usuario_id=10, identidad_verificada=True, score_reputacion=65.0
        )
        self.perfil_repository.find_practicante_by_user_id.return_value = practicante
        self.assertTrue(self.service.verify_profile(10))
        self.assertEqual(self.service.get_reputation_score(10), 65.0)

    def test_requiere_repositorios_configurados(self):
        sin_perfil_repo = PerfilApplicationService(
            perfil_repository=None, usuario_repository=self.usuario_repository
        )
        with self.assertRaisesRegex(
            RuntimeError, "requiere un repositorio de perfil"
        ):
            sin_perfil_repo.get_practicante_profile(10)

        sin_usuario_repo = PerfilApplicationService(
            perfil_repository=self.perfil_repository, usuario_repository=None
        )
        with self.assertRaisesRegex(
            RuntimeError, "requiere un repositorio de usuario"
        ):
            sin_usuario_repo.get_practicante_profile(10)


if __name__ == "__main__":
    unittest.main()
