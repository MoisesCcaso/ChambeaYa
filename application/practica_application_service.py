#!/usr/bin/python
# -*- coding: utf-8 -*-}
from typing import Final

from domain.convocatorias.postulacion import Postulacion

from domain.practica_evaluacion.practica_fabrica import PracticaFabrica

NOT_FOUND: Final = "Práctica no encontrada"


class PracticaApplicationService:
    def __init__(self, practica_repository=None, perfil_repository=None, postulacion_repository=None, convocatoria_repository=None):
        self.practica_repository = practica_repository
        self.perfil_repository = perfil_repository
        self.postulacion_repository = postulacion_repository
        self.convocatoria_repository = convocatoria_repository

    def start_practica(self, empresa_id, postulacion_id):
        self._require_repositories()
        postulacion = self.postulacion_repository.find_by_id(postulacion_id)
        if postulacion is None:
            raise ValueError("Postulación no encontrada")
        if postulacion.estado != Postulacion.ESTADO_SELECCIONADA:
            raise ValueError("La postulación debe estar seleccionada para iniciar la práctica")

        convocatoria = self.convocatoria_repository.find_by_id(postulacion.convocatoria_id)
        if convocatoria is None:
            raise ValueError("Convocatoria no encontrada")
        if convocatoria.empresa_id != empresa_id:
            raise ValueError("La postulación no pertenece a esta empresa")

        existente = self.practica_repository.find_by_postulacion_id(postulacion_id)
        if existente is not None:
            raise ValueError("La práctica ya fue iniciada")

        practica = PracticaFabrica().iniciar_practica(
            postulacion_id, postulacion.practicante_id
        )
        return self.practica_repository.save(practica)

    def upload_deliverable(self, usuario_id, practica_id, archivo):
        self._require_repositories()
        practica = self._get_practica_autorizada(usuario_id, practica_id)
        practica.subir_entregable(archivo)
        return self.practica_repository.save(practica)

    def get_deliverables_history(self, usuario_id, practica_id):
        self._require_repositories()
        practica = self._get_practica_visible(usuario_id, practica_id)
        return practica.obtener_historial_entregables()

    def delete_deliverable(self, usuario_id, practica_id, entregable_id):
        self._require_repositories()
        practica = self._get_practica_autorizada(usuario_id, practica_id)
        eliminado = practica.eliminar_entregable(entregable_id)
        self.practica_repository.save(practica)
        return eliminado

    def evaluate(self, empresa_id, practica_id, puntaje):
        self._require_repositories()
        practica = self.practica_repository.find_by_id(practica_id)
        if practica is None:
            raise ValueError(NOT_FOUND)
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
        practica = self._get_practica_visible(usuario_id, practica_id)
        return practica.obtener_historial_evaluaciones()

    def delete_evaluation(self, empresa_id, practica_id, evaluacion_id):
        self._require_repositories()
        practica = self.practica_repository.find_by_id(practica_id)
        if practica is None:
            raise ValueError(NOT_FOUND)
        self._require_empresa_owner(empresa_id, practica)
        eliminada = practica.eliminar_evaluacion(evaluacion_id)
        self.practica_repository.save(practica)
        return eliminada

    def finish(self, empresa_id, practica_id):
        self._require_repositories()
        practica = self.practica_repository.find_by_id(practica_id)
        if practica is None:
            raise ValueError(NOT_FOUND)
        self._require_empresa_owner(empresa_id, practica)

        practica.finalizar()
        return self.practica_repository.save(practica)

    def list_for_user(self, usuario_id):
        self._require_repositories()
        practicante = self.perfil_repository.find_practicante_by_user_id(usuario_id)
        if practicante is not None:
            return self.practica_repository.find_by_practicante_id(practicante.id)

        empresa = self.perfil_repository.find_empresa_by_user_id(usuario_id)
        if empresa is None:
            raise ValueError("Perfil no encontrado")

        practicas = []
        for convocatoria in self.convocatoria_repository.find_by_empresa_id(empresa.id):
            for postulacion in self.postulacion_repository.find_by_convocatoria_id(
                convocatoria.id
            ):
                practica = self.practica_repository.find_by_postulacion_id(postulacion.id)
                if practica is not None:
                    practicas.append(practica)
        return practicas

    def get_for_user(self, usuario_id, practica_id):
        self._require_repositories()
        return self._get_practica_visible(usuario_id, practica_id)

    def _get_practica_autorizada(self, usuario_id, practica_id):
        practicante = self.perfil_repository.find_practicante_by_user_id(usuario_id)
        if practicante is None:
            raise ValueError("Perfil de practicante no encontrado")

        practica = self.practica_repository.find_by_id(practica_id)
        if practica is None:
            raise ValueError(NOT_FOUND)

        if practica.practicante_id != practicante.id:
            raise ValueError("No autorizado para acceder a esta práctica")

        return practica

    def _get_practica_visible(self, usuario_id, practica_id):
        practica = self.practica_repository.find_by_id(practica_id)
        if practica is None:
            raise ValueError(NOT_FOUND)

        practicante = self.perfil_repository.find_practicante_by_user_id(usuario_id)
        if practicante is not None and practica.practicante_id == practicante.id:
            return practica

        empresa = self.perfil_repository.find_empresa_by_user_id(usuario_id)
        if empresa is not None:
            self._require_empresa_owner(empresa.id, practica)
            return practica

        raise ValueError("No autorizado para acceder a esta práctica")

    def _require_empresa_owner(self, empresa_id, practica):
        postulacion = self.postulacion_repository.find_by_id(practica.postulacion_id)
        if postulacion is None:
            raise ValueError("Postulación no encontrada")
        convocatoria = self.convocatoria_repository.find_by_id(postulacion.convocatoria_id)
        if convocatoria is None:
            raise ValueError("Convocatoria no encontrada")
        if convocatoria.empresa_id != empresa_id:
            raise ValueError("La práctica no pertenece a esta empresa")
        return convocatoria

    def _require_repositories(self):
        if any(
            repository is None
            for repository in (
                self.practica_repository,
                self.perfil_repository,
                self.postulacion_repository,
                self.convocatoria_repository,
            )
        ):
            raise RuntimeError("PracticaApplicationService requiere todos sus repositorios")
