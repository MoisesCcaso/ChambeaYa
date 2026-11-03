"""I-05 - Pruebas del repositorio SQLAlchemy de perfil con SQLite en memoria, sin dobles.

Código bajo prueba:
- src/main/infrastructure/sqlalchemy_perfil_repository.py
"""

import unittest

import pytest

from domain.perfil.empresa import Empresa
from domain.perfil.practicante import Practicante
from domain.perfil.ruc import RUC
from frameworks.sqlalchemy_orm.database import db
from frameworks.sqlalchemy_orm.models.usuario_model import UsuarioModel
from infrastructure.sqlalchemy_perfil_repository import SqlAlchemyPerfilRepository


class TestPerfilRepository(unittest.TestCase):
    """Pruebas de persistencia, lectura y conversión para SqlAlchemyPerfilRepository."""

    @pytest.fixture(autouse=True)
    def _inyectar_contexto(self, app_context):
        self.app_context = app_context

    def setUp(self):
        self.repository = SqlAlchemyPerfilRepository()

    def _crear_usuario_en_db(self, email, tipo="practicante", estado="activo"):
        usuario = UsuarioModel(
            email=email,
            password_hash="hash_prueba",
            tipo=tipo,
            estado=estado,
        )
        db.session.add(usuario)
        db.session.commit()
        return usuario

    def test_guardar_y_recargar_perfil_de_practicante_listas_y_banderas(self):
        usuario = self._crear_usuario_en_db("practicante1@test.local", tipo="practicante")
        practicante = Practicante(
            usuario_id=usuario.id,
            nombres="Lucía",
            apellidos="Mendoza",
            dni="71234567",
            carnet_universitario="20210987",
            habilidades=["Python", "SQL", "Flask"],
            formacion_educativa=["UNSA - Ciencia de la Computación", "Inglés B2"],
            score_reputacion=50.0,
            identidad_verificada=True,
        )

        guardado = self.repository.save_practicante(practicante)

        self.assertIsNotNone(guardado.id)
        self.assertEqual(guardado.usuario_id, usuario.id)
        self.assertEqual(guardado.nombres, "Lucía")
        self.assertEqual(guardado.apellidos, "Mendoza")
        self.assertEqual(guardado.dni, "71234567")
        self.assertEqual(guardado.carnet_universitario, "20210987")
        self.assertEqual(guardado.habilidades, ["Python", "SQL", "Flask"])
        self.assertEqual(
            guardado.formacion_educativa,
            ["UNSA - Ciencia de la Computación", "Inglés B2"],
        )
        self.assertEqual(guardado.score_reputacion, 50.0)
        self.assertTrue(guardado.identidad_verificada)

        por_usuario = self.repository.find_practicante_by_user_id(usuario.id)
        por_id = self.repository.find_practicante_by_id(guardado.id)

        for recuperado in (por_usuario, por_id):
            self.assertIsNotNone(recuperado)
            self.assertIsInstance(recuperado, Practicante)
            self.assertEqual(recuperado.id, guardado.id)
            self.assertEqual(recuperado.usuario_id, usuario.id)
            self.assertEqual(recuperado.nombres, "Lucía")
            self.assertEqual(recuperado.apellidos, "Mendoza")
            self.assertEqual(recuperado.dni, "71234567")
            self.assertEqual(recuperado.carnet_universitario, "20210987")
            self.assertEqual(recuperado.habilidades, ["Python", "SQL", "Flask"])
            self.assertEqual(
                recuperado.formacion_educativa,
                ["UNSA - Ciencia de la Computación", "Inglés B2"],
            )
            self.assertEqual(recuperado.score_reputacion, 50.0)
            self.assertTrue(recuperado.identidad_verificada)

    def test_actualizar_practicante_existente_por_id_y_por_usuario_id(self):
        usuario = self._crear_usuario_en_db("practicante2@test.local", tipo="practicante")
        inicial = self.repository.save_practicante(
            Practicante(
                usuario_id=usuario.id,
                nombres="Pedro",
                apellidos="Ramos",
                habilidades=["Git"],
                formacion_educativa=["UNSA"],
                score_reputacion=10.0,
                identidad_verificada=False,
            )
        )

        # Actualización cuando viene con id existente
        inicial.nombres = "Pedro Alberto"
        inicial.habilidades = ["Git", "Docker"]
        inicial.identidad_verificada = True
        inicial.score_reputacion = 40.0
        actualizado_por_id = self.repository.save_practicante(inicial)
        self.assertEqual(actualizado_por_id.id, inicial.id)
        self.assertEqual(actualizado_por_id.nombres, "Pedro Alberto")
        self.assertEqual(actualizado_por_id.habilidades, ["Git", "Docker"])
        self.assertTrue(actualizado_por_id.identidad_verificada)

        # Actualización cuando id es None pero el usuario_id ya existe en BD
        sin_id = Practicante(
            id=None,
            usuario_id=usuario.id,
            nombres="Pedro Final",
            apellidos="Ramos",
            habilidades=["Docker"],
            formacion_educativa=["UNSA", "Maestría"],
            score_reputacion=15.0,
            identidad_verificada=False,
        )
        actualizado_por_usuario = self.repository.save_practicante(sin_id)
        self.assertEqual(actualizado_por_usuario.id, inicial.id)
        self.assertEqual(actualizado_por_usuario.nombres, "Pedro Final")
        self.assertEqual(actualizado_por_usuario.habilidades, ["Docker"])
        self.assertEqual(actualizado_por_usuario.formacion_educativa, ["UNSA", "Maestría"])
        self.assertFalse(actualizado_por_usuario.identidad_verificada)

    def test_guardar_y_recuperar_empresa_con_ruc_encapsulado(self):
        usuario = self._crear_usuario_en_db("empresa1@test.local", tipo="empresa")
        empresa = Empresa(
            usuario_id=usuario.id,
            razon_social="Innovación Digital S.A.C.",
            ruc=RUC("20100070970"),
            verificada=True,
        )

        guardada = self.repository.save_empresa(empresa)

        self.assertIsNotNone(guardada.id)
        self.assertEqual(guardada.usuario_id, usuario.id)
        self.assertEqual(guardada.razon_social, "Innovación Digital S.A.C.")
        self.assertIsInstance(guardada.ruc, RUC)
        self.assertEqual(guardada.ruc.numero, "20100070970")
        self.assertTrue(guardada.ruc.es_valido())
        self.assertTrue(guardada.verificada)

        recuperada = self.repository.find_empresa_by_user_id(usuario.id)
        self.assertIsNotNone(recuperada)
        self.assertIsInstance(recuperada, Empresa)
        self.assertEqual(recuperada.id, guardada.id)
        self.assertEqual(recuperada.usuario_id, usuario.id)
        self.assertEqual(recuperada.razon_social, "Innovación Digital S.A.C.")
        self.assertIsInstance(recuperada.ruc, RUC)
        self.assertEqual(recuperada.ruc.numero, "20100070970")
        self.assertTrue(recuperada.verificada)

        # Actualizar empresa existente por id y por usuario_id
        recuperada.razon_social = "Innovación Digital Perú S.A.C."
        actualizada_id = self.repository.save_empresa(recuperada)
        self.assertEqual(actualizada_id.id, guardada.id)
        self.assertEqual(actualizada_id.razon_social, "Innovación Digital Perú S.A.C.")

        actualizada_usuario = self.repository.save_empresa(
            Empresa(
                id=None,
                usuario_id=usuario.id,
                razon_social="Innovación Global S.A.C.",
                ruc=RUC("20100070988"),
                verificada=False,
            )
        )
        self.assertEqual(actualizada_usuario.id, guardada.id)
        self.assertEqual(actualizada_usuario.razon_social, "Innovación Global S.A.C.")
        self.assertEqual(actualizada_usuario.ruc.numero, "20100070988")
        self.assertFalse(actualizada_usuario.verificada)

    def test_busquedas_inexistentes_devuelven_none(self):
        self.assertIsNone(self.repository.find_practicante_by_user_id(99999))
        self.assertIsNone(self.repository.find_practicante_by_id(99999))
        self.assertIsNone(self.repository.find_empresa_by_user_id(99999))

    def test_load_list_maneja_valores_vacios_json_invalido_y_no_listas(self):
        self.assertEqual(self.repository._load_list(None), [])
        self.assertEqual(self.repository._load_list(""), [])
        self.assertEqual(self.repository._load_list("json-corrupto{"), [])
        self.assertEqual(self.repository._load_list('{"clave": "valor"}'), [])
        self.assertEqual(self.repository._load_list('["Python", "SQL"]'), ["Python", "SQL"])


if __name__ == "__main__":
    unittest.main()
