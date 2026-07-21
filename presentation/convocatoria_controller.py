#!/usr/bin/python
# -*- coding: utf-8 -*-

from presentation._serializers import format_fecha


class ConvocatoriaController:
    def __init__(self, convocatoria_application_service=None):
        self.convocatoria_application_service = convocatoria_application_service

    def list_abiertas(self):
        self._require_service()
        convocatorias = self.convocatoria_application_service.listar_convocatorias_abiertas()
        data = [self._serialize_convocatoria(c) for c in convocatorias]
        return {"convocatorias": data}, 200

    def create(self):
        raise NotImplementedError("Creación de convocatoria asignada al módulo empresa")

    def publish(self):
        raise NotImplementedError("Publicación de convocatoria asignada al módulo empresa")

    def close(self):
        raise NotImplementedError("Cierre de convocatoria asignado al módulo empresa")

    def _require_service(self):
        if self.convocatoria_application_service is None:
            raise RuntimeError("ConvocatoriaController requiere un servicio de aplicación")

    def _serialize_convocatoria(self, convocatoria):
        return {
            "id": convocatoria.id,
            "titulo": convocatoria.titulo,
            "descripcion": convocatoria.descripcion,
            "habilidades_requeridas": convocatoria.habilidades_requeridas,
            "estado": convocatoria.estado,
            "fecha_publicacion": format_fecha(convocatoria.fecha_publicacion),
            "fecha_cierre": format_fecha(convocatoria.fecha_cierre),
        }
