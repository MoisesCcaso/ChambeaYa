#!/usr/bin/python
# -*- coding: utf-8 -*-
from domain.convocatorias.convocatoria import Convocatoria

class ConvocatoriaFabrica:
    def __init__(self):
        pass

    def crear_convocatoria(self, empresa_id, titulo, habilidades_requeridas=None, descripcion=None, beneficios=None):

        if not empresa_id:
            raise ValueError("La empresa es obligatoria")
        if not titulo:
            raise ValueError("El título es obligatorio")

        convocatoria = Convocatoria()
        convocatoria.empresa_id = empresa_id
        convocatoria.titulo = titulo
        convocatoria.descripcion = descripcion
        convocatoria.estado = Convocatoria.ESTADO_BORRADOR
        for habilidad in habilidades_requeridas or []:
            convocatoria.agregar_habilidad_requerida(habilidad)
        for beneficio in beneficios or []:
            convocatoria.agregar_beneficio(beneficio)
        return convocatoria
