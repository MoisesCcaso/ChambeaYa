#!/usr/bin/python
# -*- coding: utf-8 -*-

class PostulacionApplicationService:
    def __init__(self, postulacion_repository=None, convocatoria_repository=None):
        self.postulacion_repository = postulacion_repository
        self.convocatoria_repository = convocatoria_repository

    def apply(self):
        doSomething() # type: ignore

    def accept(self):
        doSomething() # type: ignore

    def reject(self):
        doSomething() # type: ignore

    def select_candidate(self, empresa_id, postulacion_id):
        self._require_repositories()
        postulacion = self.postulacion_repository.find_by_id(postulacion_id)
        if postulacion is None:
            raise ValueError("Postulación no encontrada")
        convocatoria = self.convocatoria_repository.find_by_id(postulacion.convocatoria_id)
        if convocatoria is None:
            raise ValueError("Convocatoria no encontrada")
        if convocatoria.empresa_id != empresa_id:
            raise ValueError("La convocatoria no pertenece a esta empresa")

        postulacion.seleccionar()
        return self.postulacion_repository.save(postulacion)

    def _require_repositories(self):
        if self.postulacion_repository is None or self.convocatoria_repository is None:
            raise RuntimeError("PostulacionApplicationService requiere ambos repositorios")