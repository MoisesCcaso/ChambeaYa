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
        descripcion = data.get("descripcion")
        habilidades_requeridas = data.get("habilidades_requeridas")
        beneficios = data.get("beneficios")
        convocatoria = self.convocatoria_fabrica.crear_convocatoria(
            empresa_id, titulo, descripcion=descripcion,
            habilidades_requeridas=habilidades_requeridas, beneficios=beneficios
        )
        return self.convocatoria_repository.save(convocatoria)

    def publish(self, empresa_id, convocatoria_id):
        self._require_repository()
        convocatoria = self.convocatoria_repository.find_by_id(convocatoria_id)
        if convocatoria is None:
            raise ValueError("Convocatoria no encontrada")
        if convocatoria.empresa_id != empresa_id:
            raise ValueError("La convocatoria no pertenece a esta empresa")

        convocatoria.publicar()
        return self.convocatoria_repository.save(convocatoria)

    def update(self, empresa_id, convocatoria_id, data):
        self._require_repository()
        convocatoria = self._find_owned(empresa_id, convocatoria_id)
        convocatoria.actualizar(
            titulo=data.get("titulo"),
            descripcion=data.get("descripcion"),
            habilidades_requeridas=data.get("habilidades_requeridas"),
            beneficios=data.get("beneficios"),
        )
        return self.convocatoria_repository.save(convocatoria)

    def close(self, empresa_id, convocatoria_id):
        self._require_repository()
        convocatoria = self._find_owned(empresa_id, convocatoria_id)
        convocatoria.cerrar()
        return self.convocatoria_repository.save(convocatoria)

    def reopen(self, empresa_id, convocatoria_id):
        self._require_repository()
        convocatoria = self._find_owned(empresa_id, convocatoria_id)
        convocatoria.reabrir()
        return self.convocatoria_repository.save(convocatoria)

    def duplicate(self, empresa_id, convocatoria_id):
        self._require_repository()
        original = self._find_owned(empresa_id, convocatoria_id)
        return self.create_convocatoria(
            empresa_id,
            {
                "titulo": f"Copia de {original.titulo}",
                "descripcion": original.descripcion,
                "habilidades_requeridas": list(original.habilidades_requeridas),
                "beneficios": list(original.beneficios),
            },
        )

    def delete(self, empresa_id, convocatoria_id):
        self._require_repository()
        convocatoria = self._find_owned(empresa_id, convocatoria_id)
        convocatoria.validar_eliminacion()
        if not self.convocatoria_repository.delete(convocatoria_id):
            raise ValueError("Convocatoria no encontrada")
        return convocatoria

    def search(self, query=None, estado=None):
        self._require_repository()
        return self.convocatoria_repository.search(query=query, estado=estado)

    def find_by_id(self, convocatoria_id):
        self._require_repository()
        convocatoria = self.convocatoria_repository.find_by_id(convocatoria_id)
        if convocatoria is None:
            raise ValueError("Convocatoria no encontrada")
        return convocatoria

    def list_for_empresa(self, empresa_id):
        self._require_repository()
        return self.convocatoria_repository.find_by_empresa_id(empresa_id)

    def _find_owned(self, empresa_id, convocatoria_id):
        convocatoria = self.convocatoria_repository.find_by_id(convocatoria_id)
        if convocatoria is None:
            raise ValueError("Convocatoria no encontrada")
        if convocatoria.empresa_id != empresa_id:
            raise ValueError("La convocatoria no pertenece a esta empresa")
        return convocatoria

    def _require_repository(self):
        if self.convocatoria_repository is None:
            raise RuntimeError("ConvocatoriaApplicationService requiere un repositorio")
