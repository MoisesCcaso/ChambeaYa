#!/usr/bin/python
# -*- coding: utf-8 -*-


class NotificacionController:
    def __init__(self, notificacion_application_service=None):
        self.notificacion_application_service = notificacion_application_service

    def list_notifications(self, usuario_id):
        self._require_service()
        notificaciones = self.notificacion_application_service.list_notifications(usuario_id)
        return [self._serialize(n) for n in notificaciones], 200

    def mark_as_read(self, usuario_id, notificacion_id):
        self._require_service()
        self.notificacion_application_service.mark_as_read(usuario_id, notificacion_id)
        return {"mensaje": "Notificación marcada como leída"}, 200

    def mark_all_as_read(self, usuario_id):
        self._require_service()
        self.notificacion_application_service.mark_all_as_read(usuario_id)
        return {"mensaje": "Todas las notificaciones marcadas como leídas"}, 200

    def count_unread(self, usuario_id):
        self._require_service()
        cantidad = self.notificacion_application_service.count_unread(usuario_id)
        return {"cantidad": cantidad}, 200

    def _require_service(self):
        if self.notificacion_application_service is None:
            raise RuntimeError("NotificacionController requiere un servicio de aplicación")

    def _serialize(self, notificacion):
        return {
            "id": notificacion.id,
            "usuario_destino_id": notificacion.usuario_destino_id,
            "tipo": notificacion.tipo,
            "mensaje": notificacion.mensaje,
            "metadata": notificacion.metadata,
            "leida": notificacion.leida,
            "created_at": notificacion.created_at.isoformat() if notificacion.created_at else None,
        }
