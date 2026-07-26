#!/usr/bin/python
# -*- coding: utf-8 -*-
from domain.notificaciones.notificacion import Notificacion
from domain.notificaciones.i_notificacion_writer import INotificacionWriter
from domain.notificaciones.i_notificacion_reader import INotificacionReader


class NotificacionApplicationService:
    def __init__(self, writer=None, reader=None):
        self.writer = writer
        self.reader = reader

    def create_notification(self, usuario_destino_id, tipo, mensaje, metadata=None):
        self._require_writer()
        notificacion = Notificacion(
            usuario_destino_id=usuario_destino_id,
            tipo=tipo,
            mensaje=mensaje,
            metadata=metadata,
        )
        return self.writer.save(notificacion)

    def list_notifications(self, usuario_id):
        self._require_reader()
        return self.reader.find_by_usuario_id(usuario_id)

    def mark_as_read(self, notificacion_id):
        self._require_writer()
        return self.writer.mark_as_read(notificacion_id)

    def mark_all_as_read(self, usuario_id):
        self._require_writer()
        return self.writer.mark_all_as_read(usuario_id)

    def count_unread(self, usuario_id):
        self._require_reader()
        return self.reader.count_unread(usuario_id)

    def _require_writer(self):
        if self.writer is None:
            raise RuntimeError("NotificacionApplicationService requiere un writer")

    def _require_reader(self):
        if self.reader is None:
            raise RuntimeError("NotificacionApplicationService requiere un reader")
