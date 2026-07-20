#!/usr/bin/python
# -*- coding: utf-8 -*-


class PracticaController:
    def __init__(self, practica_application_service=None):
        self.practica_application_service = practica_application_service

    def start(self, postulacion_id, practicante_id):
        self._require_service()
        practica = self.practica_application_service.start_practica(postulacion_id, practicante_id)
        return self._serialize_practica(practica), 201

    def upload_deliverable(self, usuario_id, practica_id, payload):
        self._require_service()
        practica = self.practica_application_service.upload_deliverable(
            usuario_id, practica_id, payload.get("archivo")
        )
        return self._serialize_practica(practica), 201

    def get_deliverables_history(self, usuario_id, practica_id):
        self._require_service()
        entregables = self.practica_application_service.get_deliverables_history(usuario_id, practica_id)
        return [self._serialize_entregable(e) for e in entregables], 200

    def register_evaluation(self, practica_id, payload):
        self._require_service()
        practica = self.practica_application_service.evaluate(practica_id, payload.get("puntaje"))
        return self._serialize_practica(practica), 201

    def get_evaluations_history(self, usuario_id, practica_id):
        self._require_service()
        evaluaciones = self.practica_application_service.get_evaluations_history(usuario_id, practica_id)
        return [self._serialize_evaluacion(e) for e in evaluaciones], 200

    def finish(self, practica_id):
        self._require_service()
        practica = self.practica_application_service.finish(practica_id)
        return self._serialize_practica(practica), 200

    def _require_service(self):
        if self.practica_application_service is None:
            raise RuntimeError("PracticaController requiere un servicio de aplicación")

    def _serialize_practica(self, practica):
        return {
            "id": practica.id,
            "postulacion_id": practica.postulacion_id,
            "practicante_id": practica.practicante_id,
            "estado": practica.estado,
        }

    def _serialize_entregable(self, entregable):
        return {
            "id": entregable.id,
            "practica_id": entregable.practica_id,
            "archivo": entregable.archivo,
            "fecha_subida": entregable.fecha_subida.isoformat() if entregable.fecha_subida else None,
        }

    def _serialize_evaluacion(self, evaluacion):
        return {
            "id": evaluacion.id,
            "practica_id": evaluacion.practica_id,
            "puntaje": evaluacion.puntaje,
            "fecha_evaluacion": evaluacion.fecha_evaluacion.isoformat() if evaluacion.fecha_evaluacion else None,
            "aprobada": evaluacion.esta_aprobada(),
        }