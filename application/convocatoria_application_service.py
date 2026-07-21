#!/usr/bin/python
# -*- coding: utf-8 -*-
from domain.convocatorias.convocatoria_fabrica import ConvocatoriaFabrica

class ConvocatoriaApplicationService:
    def __init__(self, convocatoria_repository=None, convocatoria_fabrica=None):
        self.convocatoria_repository = convocatoria_repository
        self.convocatoria_fabrica = convocatoria_fabrica or ConvocatoriaFabrica()

    def create_convocatoria(self, empresa_id, data):
        self._require_repository()
        titulo = data.get("titulo")
        convocatoria = self.convocatoria_fabrica.crear_convocatoria(empresa_id, titulo)
        return self.convocatoria_repository.save(convocatoria)

    def publish(self):
        pass

    def close(self):
        pass

    def search(self):
        pass

    def _require_repository(self):
        if self.convocatoria_repository is None:
            raise RuntimeError("ConvocatoriaApplicationService requiere un repositorio")
