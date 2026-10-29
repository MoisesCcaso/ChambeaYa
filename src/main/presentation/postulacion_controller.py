#!/usr/bin/python
# -*- coding: utf-8 -*-

class PostulacionController:
    def __init__(self, postulacion_application_service=None):
        self.postulacion_application_service = postulacion_application_service
 

    def postular(self, usuario_id, convocatoria_id):
        self._require_service()
        postulacion = self.postulacion_application_service.apply(
            usuario_id, convocatoria_id
        )
        return self._serialize_postulacion(postulacion), 201

    def list_mine(self, usuario_id):
        self._require_service()
        resultados = self.postulacion_application_service.list_for_practicante(
            usuario_id
        )
        data = []
        for postulacion, convocatoria in resultados:
            item = self._serialize_postulacion(postulacion)
            item["convocatoria"] = (
                {
                    "id": convocatoria.id,
                    "titulo": convocatoria.titulo,
                    "estado": convocatoria.estado,
                }
                if convocatoria
                else None
            )
            data.append(item)
        return data, 200

    def list_for_convocatoria(self, empresa_id, convocatoria_id):
        self._require_service()
        resultados = self.postulacion_application_service.list_for_convocatoria(
            empresa_id, convocatoria_id
        )
        data = []
        for postulacion, practicante, practica in resultados:
            item = self._serialize_postulacion(postulacion)
            item["practicante"] = (
                {
                    "id": practicante.id,
                    "nombres": practicante.nombres,
                    "apellidos": practicante.apellidos,
                    "habilidades": practicante.habilidades,
                    "score_reputacion": practicante.score_reputacion,
                    "identidad_verificada": practicante.identidad_verificada,
                }
                if practicante
                else None
            )
            item["practica_iniciada"] = practica is not None
            data.append(item)
        return data, 200

    def reject(self, empresa_id, postulacion_id):
        self._require_service()
        postulacion = self.postulacion_application_service.reject_candidate(
            empresa_id, postulacion_id
        )
        return self._serialize_postulacion(postulacion), 200

    def select(self, empresa_id, postulacion_id):
        self._require_service()
        postulacion = self.postulacion_application_service.select_candidate(empresa_id, postulacion_id)
        return self._serialize_postulacion(postulacion), 200

    def cancel(self, usuario_id, postulacion_id):
        self._require_service()
        postulacion = self.postulacion_application_service.cancel(
            usuario_id, postulacion_id
        )
        return self._serialize_postulacion(postulacion), 200

    def reconsider(self, empresa_id, postulacion_id):
        self._require_service()
        postulacion = self.postulacion_application_service.reconsider_candidate(
            empresa_id, postulacion_id
        )
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
