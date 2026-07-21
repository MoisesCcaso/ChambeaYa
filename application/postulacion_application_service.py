#!/usr/bin/python
# -*- coding: utf-8 -*-

from domain.convocatorias.postulacion import Postulacion


class PostulacionApplicationService:
    def __init__(self, postulacion_repository=None, perfil_repository=None):
        self.postulacion_repository = postulacion_repository
        self.perfil_repository = perfil_repository

    def postular_a_convocatoria(self, usuario_id, convocatoria_id):
        self._require_repositories()

        if convocatoria_id is None:
            raise ValueError("La convocatoria es obligatoria")

        practicante = self.perfil_repository.find_practicante_by_user_id(usuario_id)
        if practicante is None:
            raise ValueError("Perfil de practicante no encontrado")

        existente = self.postulacion_repository.find_by_practicante_and_convocatoria(
            practicante.id, convocatoria_id
        )
        if existente is not None:
            raise ValueError("Ya existe una postulación a esta convocatoria")

        postulacion = Postulacion(
            convocatoria_id=convocatoria_id,
            practicante_id=practicante.id,
        )
        postulacion.postular()
        return self.postulacion_repository.save(postulacion)

    def accept(self):
        raise NotImplementedError("Aceptar postulación asignado al módulo empresa")

    def reject(self):
        raise NotImplementedError("Rechazar postulación asignado al módulo empresa")

    def select_candidate(self):
        raise NotImplementedError("Seleccionar candidato asignado al módulo empresa")

    def _require_repositories(self):
        if self.postulacion_repository is None:
            raise RuntimeError(
                "PostulacionApplicationService requiere un repositorio de postulación"
            )
        if self.perfil_repository is None:
            raise RuntimeError(
                "PostulacionApplicationService requiere un repositorio de perfil"
            )
