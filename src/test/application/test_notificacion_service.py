"""I-22 - Pruebas del servicio de aplicación de notificaciones (dobles autospec).

Código bajo prueba: application/notificacion_application_service.py
"""
import unittest
from unittest.mock import create_autospec

from application.notificacion_application_service import NotificacionApplicationService
from domain.notificaciones.i_notificacion_reader import INotificacionReader
from domain.notificaciones.i_notificacion_writer import INotificacionWriter
from domain.notificaciones.notificacion import Notificacion


class TestNotificacionService(unittest.TestCase):
    def setUp(self):
        self.reader = create_autospec(INotificacionReader, instance=True)
        self.writer = create_autospec(INotificacionWriter, instance=True)
        self.service = NotificacionApplicationService(writer=self.writer, reader=self.reader)

    def test_lista_notificaciones_delegando_en_el_reader(self):
        esperado = [Notificacion(id=1), Notificacion(id=2)]
        self.reader.find_by_usuario_id.return_value = esperado

        resultado = self.service.list_notifications(5)

        self.assertEqual(esperado, resultado)
        self.reader.find_by_usuario_id.assert_called_once_with(5)

    def test_marca_una_notificacion_como_leida_con_usuario_e_id_correctos(self):
        leida = Notificacion(id=9, leida=True)
        self.writer.mark_as_read.return_value = leida

        resultado = self.service.mark_as_read(5, 9)

        self.assertIs(leida, resultado)
        self.writer.mark_as_read.assert_called_once_with(5, 9)

    def test_marcar_notificacion_ajena_propaga_el_error_del_writer(self):
        self.writer.mark_as_read.side_effect = ValueError("Notificación no encontrada")
        with self.assertRaises(ValueError):
            self.service.mark_as_read(5, 9)

    def test_marca_todas_como_leidas_para_el_usuario(self):
        self.service.mark_all_as_read(5)
        self.writer.mark_all_as_read.assert_called_once_with(5)

    def test_cuenta_no_leidas_delegando_en_el_reader(self):
        self.reader.count_unread.return_value = 3

        self.assertEqual(3, self.service.count_unread(5))
        self.reader.count_unread.assert_called_once_with(5)

    def test_crea_notificacion_y_la_guarda_con_el_writer(self):
        self.writer.save.side_effect = lambda notificacion: notificacion

        creada = self.service.create_notification(
            5, Notificacion.TIPO_CERTIFICADO_EMITIDO, "Tu certificado está listo",
            metadata={"practica_id": 7},
        )

        self.writer.save.assert_called_once_with(creada)
        self.assertEqual(5, creada.usuario_destino_id)
        self.assertEqual(Notificacion.TIPO_CERTIFICADO_EMITIDO, creada.tipo)
        self.assertEqual("Tu certificado está listo", creada.mensaje)
        self.assertEqual({"practica_id": 7}, creada.metadata)
        self.assertFalse(creada.leida)

    def test_crea_notificacion_sin_metadata_usa_diccionario_vacio(self):
        self.writer.save.side_effect = lambda notificacion: notificacion
        creada = self.service.create_notification(5, Notificacion.TIPO_NUEVAS_SUGERENCIAS, "Hola")
        self.assertEqual({}, creada.metadata)

    def test_el_reader_no_se_usa_para_operaciones_de_escritura(self):
        self.service.mark_all_as_read(5)
        self.service.mark_as_read(5, 1)
        self.assertEqual([], self.reader.method_calls)

    def test_el_writer_no_se_usa_para_operaciones_de_lectura(self):
        self.service.list_notifications(5)
        self.service.count_unread(5)
        self.assertEqual([], self.writer.method_calls)

    def test_sin_writer_las_escrituras_lanzan_runtime_error(self):
        servicio = NotificacionApplicationService(reader=self.reader)
        with self.assertRaises(RuntimeError):
            servicio.create_notification(5, "T", "m")
        with self.assertRaises(RuntimeError):
            servicio.mark_as_read(5, 1)
        with self.assertRaises(RuntimeError):
            servicio.mark_all_as_read(5)

    def test_sin_reader_las_lecturas_lanzan_runtime_error(self):
        servicio = NotificacionApplicationService(writer=self.writer)
        with self.assertRaises(RuntimeError):
            servicio.list_notifications(5)
        with self.assertRaises(RuntimeError):
            servicio.count_unread(5)


if __name__ == "__main__":
    unittest.main()
