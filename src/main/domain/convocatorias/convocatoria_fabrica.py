#!/usr/bin/python
# -*- coding: utf-8 -*-
from domain.convocatorias.convocatoria import Convocatoria

class ConvocatoriaFabrica:
    def crear_convocatoria(self, empresa_id, titulo, habilidades_requeridas=None, descripcion=None, beneficios=None):

        if not empresa_id:
            raise ValueError("La empresa es obligatoria")
        if not titulo or not str(titulo).strip():
            raise ValueError("El título es obligatorio")
        if habilidades_requeridas is not None and not isinstance(
            habilidades_requeridas, list
        ):
            raise ValueError("Las habilidades requeridas deben ser una lista")
        if beneficios is not None and not isinstance(beneficios, list):
            raise ValueError("Los beneficios deben ser una lista")

        convocatoria = Convocatoria()
        convocatoria.empresa_id = empresa_id
        convocatoria.titulo = str(titulo).strip()
        convocatoria.descripcion = (
            str(descripcion).strip() if descripcion is not None else None
        )
        convocatoria.estado = Convocatoria.ESTADO_BORRADOR
        for habilidad in habilidades_requeridas or []:
            convocatoria.agregar_habilidad_requerida(habilidad)
        for beneficio in beneficios or []:
            convocatoria.agregar_beneficio(beneficio)
        return convocatoria
