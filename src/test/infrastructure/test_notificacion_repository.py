"""I-19 - Pruebas del repositorio de notificaciones (SQLite en memoria, sin dobles).

Código bajo prueba: infrastructure/sqlalchemy_notificacion_repository.py
"""
import unittest

import pytest
from domain.notificaciones.notificacion import Notificacion
from frameworks.sqlalchemy_orm.database import db
from frameworks.sqlalchemy_orm.models.notificacion_model import NotificacionModel
from frameworks.sqlalchemy_orm.models.usuario_model import UsuarioModel
from infrastructure.sqlalchemy_notificacion_repository import SqlAlchemyNotificacionRepository


class TestNotificacionRepository(unittest.TestCase):
    @pytest.fixture(autouse=True)
    def _inyectar_contexto(self, app_context):
        self.app_context = app_context

    def setUp(self):
        self.repo = SqlAlchemyNotificacionRepository()

    def _crear_usuario(self, email):
        usuario = UsuarioModel(email=email, password_hash="hash", tipo="practicante")
        db.session.add(usuario)
        db.session.commit()
        return usuario.id

    def _guardar(self, usuario_id, mensaje="Hola", tipo=Notificacion.TIPO_NUEVAS_SUGERENCIAS,
                 metadata=None):
        return self.repo.save(
            Notificacion(usuario_destino_id=usuario_id, tipo=tipo, mensaje=mensaje,
                         metadata=metadata)
        )

    def test_guarda_notificacion_nueva_y_la_devuelve_con_id(self):
        usuario_id = self._crear_usuario("a@example.com")
        guardada = self._guardar(usuario_id, "Nueva sugerencia", metadata={"convocatoria_id": 3})

        self.assertIsNotNone(guardada.id)
        self.assertEqual(usuario_id, guardada.usuario_destino_id)
        self.assertEqual("Nueva sugerencia", guardada.mensaje)
        self.assertEqual({"convocatoria_id": 3}, guardada.metadata)
        self.assertFalse(guardada.leida)
        self.assertIsNotNone(guardada.created_at)

    def test_guardar_notificacion_existente_actualiza_el_registro(self):
        usuario_id = self._crear_usuario("a@example.com")
        guardada = self._guardar(usuario_id)
        guardada.marcar_como_leida()
        self.repo.save(guardada)

        self.assertEqual(1, NotificacionModel.query.count())
        self.assertTrue(NotificacionModel.query.first().leida)

    def test_lista_solo_las_notificaciones_del_usuario(self):
        u1 = self._crear_usuario("a@example.com")
        u2 = self._crear_usuario("b@example.com")
        propias = {self._guardar(u1, "uno").id, self._guardar(u1, "dos").id}
        self._guardar(u2, "ajena")

        resultado = self.repo.find_by_usuario_id(u1)

        self.assertEqual(propias, {n.id for n in resultado})

    def test_lista_vacia_si_el_usuario_no_tiene_notificaciones(self):
        usuario_id = self._crear_usuario("a@example.com")
        self.assertEqual([], self.repo.find_by_usuario_id(usuario_id))

    def test_consulta_solo_las_no_leidas(self):
        usuario_id = self._crear_usuario("a@example.com")
        pendiente = self._guardar(usuario_id, "pendiente")
        leida = self._guardar(usuario_id, "leida")
        self.repo.mark_as_read(usuario_id, leida.id)

        resultado = self.repo.find_unread_by_usuario_id(usuario_id)

        self.assertEqual([pendiente.id], [n.id for n in resultado])

    def test_cuenta_las_pendientes(self):
        usuario_id = self._crear_usuario("a@example.com")
        otro = self._crear_usuario("b@example.com")
        self._guardar(usuario_id)
        leida = self._guardar(usuario_id)
        self._guardar(otro)
        self.repo.mark_as_read(usuario_id, leida.id)

        self.assertEqual(1, self.repo.count_unread(usuario_id))
        self.assertEqual(1, self.repo.count_unread(otro))

    def test_cuenta_cero_sin_notificaciones(self):
        usuario_id = self._crear_usuario("a@example.com")
        self.assertEqual(0, self.repo.count_unread(usuario_id))

    def test_marca_como_leida_una_notificacion_propia(self):
        usuario_id = self._crear_usuario("a@example.com")
        guardada = self._guardar(usuario_id)

        actualizada = self.repo.mark_as_read(usuario_id, guardada.id)

        self.assertTrue(actualizada.leida)
        self.assertTrue(db.session.get(NotificacionModel, guardada.id).leida)

    def test_usuario_no_puede_marcar_como_leida_una_notificacion_ajena(self):
        propietario = self._crear_usuario("a@example.com")
        intruso = self._crear_usuario("b@example.com")
        guardada = self._guardar(propietario)

        with self.assertRaises(ValueError):
            self.repo.mark_as_read(intruso, guardada.id)

        self.assertFalse(db.session.get(NotificacionModel, guardada.id).leida)

    def test_marcar_notificacion_inexistente_lanza_error(self):
        usuario_id = self._crear_usuario("a@example.com")
        with self.assertRaises(ValueError):
            self.repo.mark_as_read(usuario_id, 9999)

    def test_marcar_todas_solo_cambia_las_pendientes_de_ese_usuario(self):
        u1 = self._crear_usuario("a@example.com")
        u2 = self._crear_usuario("b@example.com")
        self._guardar(u1)
        self._guardar(u1)
        ajena = self._guardar(u2)

        self.repo.mark_all_as_read(u1)

        self.assertEqual(0, self.repo.count_unread(u1))
        self.assertEqual(1, self.repo.count_unread(u2))
        self.assertFalse(db.session.get(NotificacionModel, ajena.id).leida)

    def test_metadata_invalida_se_carga_como_diccionario_vacio(self):
        usuario_id = self._crear_usuario("a@example.com")
        guardada = self._guardar(usuario_id)
        db.session.get(NotificacionModel, guardada.id).metadata_json = "{no es json"
        db.session.commit()

        self.assertEqual({}, self.repo.find_by_usuario_id(usuario_id)[0].metadata)


if __name__ == "__main__":
    unittest.main()
