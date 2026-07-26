#!/usr/bin/python
# -*- coding: utf-8 -*-}
from typing import Final
UNFINDED: Final = "Práctica no encontrada"

from domain.practica_evaluacion.practica_fabrica import PracticaFabrica


class PracticaApplicationService:
    def __init__(self, practica_repository=None, perfil_repository=None, postulacion_repository=None, convocatoria_repository=None):
        self.practica_repository = practica_repository
        self.perfil_repository = perfil_repository
        self.postulacion_repository = postulacion_repository
        self.convocatoria_repository = convocatoria_repository

    def start_practica(self, postulacion_id, practicante_id):
        self._require_repositories()
        practica = PracticaFabrica().iniciar_practica(postulacion_id, practicante_id)
        return self.practica_repository.save(practica)

    def upload_deliverable(self, usuario_id, practica_id, archivo):
        self._require_repositories()
        practica = self._get_practica_autorizada(usuario_id, practica_id)
        practica.subir_entregable(archivo)
        return self.practica_repository.save(practica)

    def get_deliverables_history(self, usuario_id, practica_id):
        self._require_repositories()
        practica = self._get_practica_autorizada(usuario_id, practica_id)
        return practica.obtener_historial_entregables()

    def evaluate(self, empresa_id, practica_id, puntaje):
        self._require_repositories()
        practica = self.practica_repository.find_by_id(practica_id)
        if practica is None:
            raise ValueError(UNFINDED)
        postulacion = self.postulacion_repository.find_by_id(practica.postulacion_id)
        if postulacion is None:
            raise ValueError("Postulación no encontrada")

        convocatoria = self.convocatoria_repository.find_by_id(postulacion.convocatoria_id)
        if convocatoria is None:
            raise ValueError("Convocatoria no encontrada")
        if convocatoria.empresa_id != empresa_id:
            raise ValueError("La práctica no pertenece a una convocatoria de esta empresa")

        practica.registrar_evaluacion(puntaje)
        return self.practica_repository.save(practica)

    def get_evaluations_history(self, usuario_id, practica_id):
        self._require_repositories()
        practica = self._get_practica_autorizada(usuario_id, practica_id)
        return practica.obtener_historial_evaluaciones()

    def finish(self, practica_id):
        self._require_repositories()
        practica = self.practica_repository.find_by_id(practica_id)
        if practica is None:
            raise ValueError(UNFINDED)

        practica.finalizar()
        return self.practica_repository.save(practica)

    def _get_practica_autorizada(self, usuario_id, practica_id):
        practicante = self.perfil_repository.find_practicante_by_user_id(usuario_id)
        if practicante is None:
            raise ValueError("Perfil de practicante no encontrado")

        practica = self.practica_repository.find_by_id(practica_id)
        if practica is None:
            raise ValueError(UNFINDED)

        if practica.practicante_id != practicante.id:
            raise ValueError("No autorizado para acceder a esta práctica")

        return practica

    def _require_repositories(self):
        if self.practica_repository is None:
            raise RuntimeError("PracticaApplicationService requiere un repositorio de práctica")