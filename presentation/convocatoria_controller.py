#!/usr/bin/python
# -*- coding: utf-8 -*-

class ConvocatoriaController:
    def __init__(self, convocatoria_application_service=None):
        self.convocatoria_application_service = convocatoria_application_service

    def create(self, empresa_id, payload):
        self._require_service()
        convocatoria = self.convocatoria_application_service.create_convocatoria(empresa_id, payload)
        return self._serialize_convocatoria(convocatoria), 201

    def publish(self, empresa_id, convocatoria_id):
        self._require_service()
        convocatoria = self.convocatoria_application_service.publish(empresa_id, convocatoria_id)
        return self._serialize_convocatoria(convocatoria), 200

    def close(self, empresa_id, convocatoria_id):
        self._require_service()
        convocatoria = self.convocatoria_application_service.close(
            empresa_id, convocatoria_id
        )
        return self._serialize_convocatoria(convocatoria), 200

    def update(self, empresa_id, convocatoria_id, payload):
        self._require_service()
        convocatoria = self.convocatoria_application_service.update(
            empresa_id, convocatoria_id, payload
        )
        return self._serialize_convocatoria(convocatoria), 200

    def list(self, query=None, estado=None):
        self._require_service()
        convocatorias = self.convocatoria_application_service.search(query, estado)
        return [self._serialize_convocatoria(item) for item in convocatorias], 200

    def get(self, convocatoria_id):
        self._require_service()
        convocatoria = self.convocatoria_application_service.find_by_id(convocatoria_id)
        return self._serialize_convocatoria(convocatoria), 200

    def list_for_empresa(self, empresa_id):
        self._require_service()
        convocatorias = self.convocatoria_application_service.list_for_empresa(
            empresa_id
        )
        return [self._serialize_convocatoria(item) for item in convocatorias], 200

    def _require_service(self):
        if self.convocatoria_application_service is None:
            raise RuntimeError("ConvocatoriaController requiere un application service")

    def _serialize_convocatoria(self, convocatoria):
        return {
            "id": convocatoria.id,
            "empresa_id": convocatoria.empresa_id,
            "titulo": convocatoria.titulo,
            "descripcion": convocatoria.descripcion,
            "estado": convocatoria.estado,
            "habilidades_requeridas": convocatoria.habilidades_requeridas,
            "beneficios": convocatoria.beneficios,
            "fecha_publicacion": (
                convocatoria.fecha_publicacion.isoformat()
                if convocatoria.fecha_publicacion
                else None
            ),
            "fecha_cierre": (
                convocatoria.fecha_cierre.isoformat()
                if convocatoria.fecha_cierre
                else None
            ),
        }
