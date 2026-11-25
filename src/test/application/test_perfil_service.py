"""I-06 - Pruebas unitarias de los servicios de aplicación de perfil con dobles (autospec).

Código bajo prueba:
- src/main/application/practicante_application_service.py
- src/main/application/empresa_application_service.py
"""

import unittest
from unittest.mock import create_autospec

from application.empresa_application_service import EmpresaApplicationService
from application.practicante_application_service import PracticanteApplicationService
from identity.domain.i_user_repository import IUserRepository
from identity.domain.user import User
from domain.perfil.empresa import Empresa
from domain.perfil.i_empresa_repository import IEmpresaRepository
from domain.perfil.i_perfil_repository import IPerfilRepository
from domain.perfil.i_practicante_repository import IPracticanteRepository
from domain.perfil.practicante import Practicante
from domain.perfil.ruc import RUC


class TestPerfilService(unittest.TestCase):
    """Practicante y Empresa con el IPerfilRepository unificado, como los cablea dependencies.py."""

    def setUp(self):
        self.perfil_repository = create_autospec(
            IPerfilRepository, instance=True, spec_set=True
        )
        self.user_repository = create_autospec(
            IUserRepository, instance=True, spec_set=True
        )
        self.practicante_service = PracticanteApplicationService(
            practicante_repository=self.perfil_repository,
            user_repository=self.user_repository,
        )
        self.empresa_service = EmpresaApplicationService(
            empresa_repository=self.perfil_repository,
            user_repository=self.user_repository,
        )

    def _usuario_practicante_activo(self, user_id=10):
        return User(
            id=user_id,
            email="practicante@test.local",
            password_hash="hash",
            role=User.ROLE_INTERN,
            status=User.STATUS_ACTIVE,
        )

    def _usuario_empresa_activo(self, user_id=20):
        return User(
            id=user_id,
            email="empresa@test.local",
            password_hash="hash",
            role=User.ROLE_COMPANY,
            status=User.STATUS_ACTIVE,
        )

    def test_update_practicante_activo_crea_o_actualiza_verifica_identidad_y_guarda(self):
        user = self._usuario_practicante_activo(user_id=10)
        self.user_repository.find_by_id.return_value = user
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

        result = self.practicante_service.update_practicante(10, datos)

        self.user_repository.find_by_id.assert_called_once_with(10)
        self.perfil_repository.find_practicante_by_user_id.assert_called_once_with(10)
        self.perfil_repository.save_practicante.assert_called_once()

        practicante_guardado = self.perfil_repository.save_practicante.call_args[0][0]
        self.assertIs(result, practicante_guardado)
        self.assertEqual(practicante_guardado.user_id, 10)
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
        user = self._usuario_practicante_activo(user_id=10)
        existing = Practicante(
            id=5,
            user_id=10,
            nombres="Ana",
            apellidos="Torres",
            dni="71234567",
            identidad_verificada=True,
            score_reputacion=25.0,
        )
        self.user_repository.find_by_id.return_value = user
        self.perfil_repository.find_practicante_by_user_id.return_value = existing
        self.perfil_repository.save_practicante.side_effect = lambda p: p

        result = self.practicante_service.update_practicante(
            10, {"dni": "   ", "carnet_universitario": None}
        )

        self.assertIs(result, existing)
        self.assertIsNone(existing.dni)
        self.assertIsNone(existing.carnet_universitario)
        self.assertFalse(existing.identidad_verificada)
        self.assertEqual(existing.score_reputacion, 0.0)
        self.perfil_repository.save_practicante.assert_called_once_with(existing)

    def test_update_practicante_rechaza_usuario_inexistente_antes_de_guardar(self):
        self.user_repository.find_by_id.return_value = None

        with self.assertRaisesRegex(ValueError, "Usuario no encontrado"):
            self.practicante_service.update_practicante(99, {"nombres": "Ana"})

        self.user_repository.find_by_id.assert_called_once_with(99)
        self.perfil_repository.find_practicante_by_user_id.assert_not_called()
        self.perfil_repository.save_practicante.assert_not_called()

    def test_update_practicante_rechaza_usuario_inactivo_antes_de_guardar(self):
        usuario_inactivo = User(
            id=10,
            email="pendiente@test.local",
            password_hash="hash",
            role=User.ROLE_INTERN,
            status=User.STATUS_PENDING,
        )
        self.user_repository.find_by_id.return_value = usuario_inactivo

        with self.assertRaisesRegex(ValueError, "La cuenta no está activa"):
            self.practicante_service.update_practicante(10, {"nombres": "Ana"})

        self.user_repository.find_by_id.assert_called_once_with(10)
        self.perfil_repository.find_practicante_by_user_id.assert_not_called()
        self.perfil_repository.save_practicante.assert_not_called()

    def test_update_practicante_rechaza_usuario_tipo_empresa_antes_de_guardar(self):
        usuario_empresa = self._usuario_empresa_activo(user_id=20)
        self.user_repository.find_by_id.return_value = usuario_empresa

        with self.assertRaisesRegex(ValueError, "El usuario no es practicante"):
            self.practicante_service.update_practicante(20, {"nombres": "Ana"})

        self.user_repository.find_by_id.assert_called_once_with(20)
        self.perfil_repository.find_practicante_by_user_id.assert_not_called()
        self.perfil_repository.save_practicante.assert_not_called()

    def test_get_practicante_profile_y_operaciones_de_habilidad_formacion_e_identidad(self):
        user = self._usuario_practicante_activo(user_id=10)
        self.user_repository.find_by_id.return_value = user
        self.perfil_repository.find_practicante_by_user_id.return_value = None
        self.perfil_repository.save_practicante.side_effect = lambda p: p

        self.assertIsNone(self.practicante_service.get_practicante_profile(10))

        con_habilidad = self.practicante_service.add_habilidad(10, "  Python  ")
        self.assertEqual(con_habilidad.habilidades, ["Python"])
        self.assertEqual(con_habilidad.score_reputacion, 5.0)

        self.perfil_repository.find_practicante_by_user_id.return_value = con_habilidad
        con_formacion = self.practicante_service.add_formacion(10, "  UNSA  ")
        self.assertEqual(con_formacion.formacion_educativa, ["UNSA"])
        self.assertEqual(con_formacion.score_reputacion, 10.0)

        con_identidad = self.practicante_service.register_identity(
            10, dni="71234567", carnet_universitario="20210001"
        )
        self.assertTrue(con_identidad.identidad_verificada)
        self.assertEqual(con_identidad.score_reputacion, 35.0)

    def test_update_y_get_empresa_profile_y_guardas_de_empresa(self):
        usuario_empresa = self._usuario_empresa_activo(user_id=20)
        self.user_repository.find_by_id.return_value = usuario_empresa
        self.perfil_repository.find_empresa_by_user_id.return_value = None
        self.perfil_repository.save_empresa.side_effect = lambda e: e

        # Guardado válido de empresa
        empresa_guardada = self.empresa_service.update_empresa(
            20, {"razon_social": "  Acme S.A.C.  ", "ruc": "20100070970"}
        )
        self.assertEqual(empresa_guardada.user_id, 20)
        self.assertEqual(empresa_guardada.razon_social, "Acme S.A.C.")
        self.assertIsInstance(empresa_guardada.ruc, RUC)
        self.assertTrue(empresa_guardada.verificada)
        self.perfil_repository.save_empresa.assert_called_once_with(empresa_guardada)

        self.perfil_repository.find_empresa_by_user_id.return_value = empresa_guardada
        self.assertIs(self.empresa_service.get_empresa_profile(20), empresa_guardada)

        # Actualizar empresa ya existente
        existing = Empresa(
            id=3, user_id=20, razon_social="Anterior S.A.C.", ruc=RUC("20100070970")
        )
        self.perfil_repository.find_empresa_by_user_id.return_value = existing
        actualizada = self.empresa_service.update_empresa(
            20, {"razon_social": "Nueva Razón S.A.C."}
        )
        self.assertIs(actualizada, existing)
        self.assertEqual(actualizada.razon_social, "Nueva Razón S.A.C.")
        self.assertTrue(actualizada.verificada)

        # Razón social vacía
        with self.assertRaisesRegex(ValueError, "La razón social es obligatoria"):
            self.empresa_service.update_empresa(20, {"razon_social": "   ", "ruc": "20100070970"})

        # RUC inválido
        with self.assertRaisesRegex(ValueError, "El RUC no es válido"):
            self.empresa_service.update_empresa(
                20, {"razon_social": "Acme S.A.C.", "ruc": "20100070975"}
            )

        # Guardas de usuario para empresa: inexistente, tipo practicante, inactivo
        self.user_repository.find_by_id.return_value = None
        with self.assertRaisesRegex(ValueError, "Usuario no encontrado"):
            self.empresa_service.update_empresa(99, {"razon_social": "X", "ruc": "20100070970"})

        self.user_repository.find_by_id.return_value = self._usuario_practicante_activo(10)
        with self.assertRaisesRegex(ValueError, "El usuario no es empresa"):
            self.empresa_service.update_empresa(10, {"razon_social": "X", "ruc": "20100070970"})

        self.user_repository.find_by_id.return_value = User(
            id=20,
            email="emp@test.local",
            password_hash="h",
            role=User.ROLE_COMPANY,
            status=User.STATUS_PENDING,
        )
        with self.assertRaisesRegex(ValueError, "La cuenta no está activa"):
            self.empresa_service.update_empresa(20, {"razon_social": "X", "ruc": "20100070970"})

    def test_verify_profile_y_get_reputation_score(self):
        self.perfil_repository.find_practicante_by_user_id.return_value = None
        with self.assertRaisesRegex(ValueError, "Perfil de practicante no encontrado"):
            self.practicante_service.verify_profile(10)
        self.assertEqual(self.practicante_service.get_reputation_score(10), 0.0)

        practicante = Practicante(
            user_id=10, identidad_verificada=True, score_reputacion=65.0
        )
        self.perfil_repository.find_practicante_by_user_id.return_value = practicante
        self.assertTrue(self.practicante_service.verify_profile(10))
        self.assertEqual(self.practicante_service.get_reputation_score(10), 65.0)

    def test_requiere_repositorios_configurados(self):
        sin_perfil_repo = PracticanteApplicationService(
            practicante_repository=None, user_repository=self.user_repository
        )
        with self.assertRaisesRegex(
            RuntimeError, "requiere un repositorio de practicante"
        ):
            sin_perfil_repo.get_practicante_profile(10)

        sin_usuario_repo = PracticanteApplicationService(
            practicante_repository=self.perfil_repository, user_repository=None
        )
        with self.assertRaisesRegex(
            RuntimeError, "requiere un repositorio de usuario"
        ):
            sin_usuario_repo.get_practicante_profile(10)

        sin_empresa_repo = EmpresaApplicationService(
            empresa_repository=None, user_repository=self.user_repository
        )
        with self.assertRaisesRegex(
            RuntimeError, "requiere un repositorio de empresa"
        ):
            sin_empresa_repo.get_empresa_profile(20)


class TestPracticanteApplicationService(unittest.TestCase):
    """Pruebas aisladas de PracticanteApplicationService usando IPracticanteRepository segregado."""

    def setUp(self):
        self.practicante_repo = create_autospec(IPracticanteRepository, instance=True, spec_set=True)
        self.usuario_repo = create_autospec(IUserRepository, instance=True, spec_set=True)
        self.service = PracticanteApplicationService(
            practicante_repository=self.practicante_repo,
            user_repository=self.usuario_repo,
        )

    def test_actualiza_habilidades_y_reputacion_con_repo_segregado(self):
        user = User(id=22, email="student@test.pe", password_hash="hash", role=User.ROLE_INTERN, status=User.STATUS_ACTIVE)
        self.usuario_repo.find_by_id.return_value = user
        self.practicante_repo.find_practicante_by_user_id.return_value = None
        self.practicante_repo.save_practicante.side_effect = lambda p: p

        practicante = self.service.add_habilidad(22, "FastAPI")
        self.assertIn("FastAPI", practicante.habilidades)
        self.practicante_repo.save_practicante.assert_called_once()

    def test_requiere_repositorios(self):
        sin_repo = PracticanteApplicationService(practicante_repository=None, user_repository=self.usuario_repo)
        with self.assertRaises(RuntimeError):
            sin_repo.get_profile(22)


class TestEmpresaApplicationService(unittest.TestCase):
    """Pruebas aisladas de EmpresaApplicationService usando IEmpresaRepository segregado."""

    def setUp(self):
        self.empresa_repo = create_autospec(IEmpresaRepository, instance=True, spec_set=True)
        self.usuario_repo = create_autospec(IUserRepository, instance=True, spec_set=True)
        self.service = EmpresaApplicationService(
            empresa_repository=self.empresa_repo,
            user_repository=self.usuario_repo,
        )

    def test_actualiza_empresa_con_repo_segregado(self):
        user = User(id=33, email="empresa@test.pe", password_hash="hash", role=User.ROLE_COMPANY, status=User.STATUS_ACTIVE)
        self.usuario_repo.find_by_id.return_value = user
        self.empresa_repo.find_empresa_by_user_id.return_value = None
        self.empresa_repo.save_empresa.side_effect = lambda e: e

        empresa = self.service.update_empresa(33, {"razon_social": "Acme SAC", "ruc": "20100070988"})
        self.assertEqual(empresa.razon_social, "Acme SAC")
        self.empresa_repo.save_empresa.assert_called_once()

    def test_requiere_repositorios(self):
        sin_repo = EmpresaApplicationService(empresa_repository=None, user_repository=self.usuario_repo)
        with self.assertRaises(RuntimeError):
            sin_repo.get_profile(33)


if __name__ == "__main__":
    unittest.main()
