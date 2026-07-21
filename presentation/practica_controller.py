#!/usr/bin/python
# -*- coding: utf-8 -*-

from presentation._serializers import format_fecha


class PracticaController:
    def __init__(self, practica_application_service=None):
        self.practica_application_service = practica_application_service

    def list_mis_practicas(self, usuario_id):
        self._require_service()
        practicas = self.practica_application_service.ver_mis_practicas(usuario_id)
        data = [self._serialize_practica(p) for p in practicas]
        return {"practicas": data}, 200

    def subir_entregable(self, usuario_id, practica_id, payload):
        self._require_service()
        practica = self.practica_application_service.subir_entregable(
            usuario_id=usuario_id,
            practica_id=practica_id,
            descripcion=payload.get("descripcion"),
            archivo_url=payload.get("archivo_url"),
        )
        return self._serialize_practica(practica), 201

    def register_evaluation(self):
        raise NotImplementedError("Registro de evaluación asignado al módulo empresa")

    def finish(self):
        raise NotImplementedError("Finalización de práctica asignada al módulo empresa")

    def _require_service(self):
        if self.practica_application_service is None:
            raise RuntimeError("PracticaController requiere un servicio de aplicación")

    def _serialize_practica(self, practica):
        return {
            "id": practica.id,
            "postulacion_id": practica.postulacion_id,
            "practicante_id": practica.practicante_id,
            "estado": practica.estado,
            "entregables": [self._serialize_entregable(e) for e in practica.entregables],
        }

    def _serialize_entregable(self, entregable):
        return {
            "id": entregable.id,
            "descripcion": entregable.descripcion,
            "archivo_url": entregable.archivo_url,
            "fecha_subida": format_fecha(entregable.fecha_subida),
        }
