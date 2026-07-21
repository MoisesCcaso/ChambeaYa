#!/usr/bin/python
# -*- coding: utf-8 -*-

class PostulacionController:
    def __init__(self, postulacion_application_service=None):
        self.postulacion_application_service = postulacion_application_service

    def postular(self, usuario_id, convocatoria_id):
        self._require_service()
        postulacion = self.postulacion_application_service.postular_a_convocatoria(
            usuario_id=usuario_id,
            convocatoria_id=convocatoria_id,
        )
        return self._serialize_postulacion(postulacion), 201

    def accept(self):
        raise NotImplementedError("Aceptar postulación asignado al módulo empresa")

    def reject(self):
        raise NotImplementedError("Rechazar postulación asignado al módulo empresa")

    def select(self):
        raise NotImplementedError("Seleccionar candidato asignado al módulo empresa")

    def _require_service(self):
        if self.postulacion_application_service is None:
            raise RuntimeError("PostulacionController requiere un servicio de aplicación")

    def _serialize_postulacion(self, postulacion):
        return {
            "id": postulacion.id,
            "convocatoria_id": postulacion.convocatoria_id,
            "practicante_id": postulacion.practicante_id,
            "estado": postulacion.estado,
            "fecha_postulacion": self._format_fecha(postulacion.fecha_postulacion),
        }

    def _format_fecha(self, fecha):
        if fecha is None:
            return None

        return fecha.isoformat()
