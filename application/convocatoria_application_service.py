#!/usr/bin/python
# -*- coding: utf-8 -*-

class ConvocatoriaApplicationService:
    def __init__(self, convocatoria_repository=None):
        self.convocatoria_repository = convocatoria_repository

    def listar_convocatorias_abiertas(self):
        self._require_repository()
        convocatorias = self.convocatoria_repository.find_abiertas()
        return convocatorias or []

    def create_convocatoria(self):
        raise NotImplementedError("Creación de convocatoria asignada al módulo empresa")

    def publish(self):
        raise NotImplementedError("Publicación de convocatoria asignada al módulo empresa")

    def close(self):
        raise NotImplementedError("Cierre de convocatoria asignado al módulo empresa")

    def _require_repository(self):
        if self.convocatoria_repository is None:
            raise RuntimeError("ConvocatoriaApplicationService requiere un repositorio")
