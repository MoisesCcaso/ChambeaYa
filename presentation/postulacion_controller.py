#!/usr/bin/python
# -*- coding: utf-8 -*-

class PostulacionController:
    def __init__(self, postulacion_application_service=None):
        self.postulacion_application_service = postulacion_application_service
 

    def postular(self):
        pass

    def accept(self):
        pass

    def reject(self):
        pass

    def select(self, empresa_id, postulacion_id):
        self._require_service()
        postulacion = self.postulacion_application_service.select_candidate(empresa_id, postulacion_id)
        return self._serialize_postulacion(postulacion), 200

    def _require_service(self):
        if self.postulacion_application_service is None:
            raise RuntimeError("PostulacionController requiere un application service")

    def _serialize_postulacion(self, postulacion):
        return {
            "id": postulacion.id,
            "convocatoria_id": postulacion.convocatoria_id,
            "practicante_id": postulacion.practicante_id,
            "estado": postulacion.estado,
        }
