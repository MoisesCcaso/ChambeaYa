#!/usr/bin/python
# -*- coding: utf-8 -*-

class PracticaApplicationService:
    def __init__(self, practica_repository=None, perfil_repository=None):
        self.practica_repository = practica_repository
        self.perfil_repository = perfil_repository

    def ver_mis_practicas(self, usuario_id):
        self._require_repositories()
        practicante = self._require_practicante(usuario_id)
        practicas = self.practica_repository.find_by_practicante_id(practicante.id)
        return practicas or []

    def subir_entregable(self, usuario_id, practica_id, descripcion=None, archivo_url=None):
        self._require_repositories()
        practicante = self._require_practicante(usuario_id)

        practica = self.practica_repository.find_by_id(practica_id)
        if practica is None:
            raise ValueError("Práctica no encontrada")
        if practica.practicante_id != practicante.id:
            raise ValueError("La práctica no pertenece al practicante")

        practica.subir_entregable(descripcion=descripcion, archivo_url=archivo_url)
        return self.practica_repository.save(practica)

    def evaluate(self):
        raise NotImplementedError("Evaluación de práctica asignada al módulo empresa")

    def finish(self):
        raise NotImplementedError("Finalización de práctica asignada al módulo empresa")

    def _require_practicante(self, usuario_id):
        practicante = self.perfil_repository.find_practicante_by_user_id(usuario_id)
        if practicante is None:
            raise ValueError("Perfil de practicante no encontrado")

        return practicante

    def _require_repositories(self):
        if self.practica_repository is None:
            raise RuntimeError(
                "PracticaApplicationService requiere un repositorio de práctica"
            )
        if self.perfil_repository is None:
            raise RuntimeError(
                "PracticaApplicationService requiere un repositorio de perfil"
            )
