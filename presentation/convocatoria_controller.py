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

    def close(self):
        pass

    def list(self):
        pass
    def _require_service(self):
        if self.convocatoria_application_service is None:
            raise RuntimeError("ConvocatoriaController requiere un application service")

    def _serialize_convocatoria(self, convocatoria):
        return {
            "id": convocatoria.id,
            "empresa_id": convocatoria.empresa_id,
            "titulo": convocatoria.titulo,
            "estado": convocatoria.estado,
        }