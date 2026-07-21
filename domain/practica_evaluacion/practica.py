#!/usr/bin/python
# -*- coding: utf-8 -*-

from domain.practica_evaluacion.entregable import Entregable


class Practica:
    ESTADO_EN_CURSO = "en_curso"
    ESTADO_FINALIZADA = "finalizada"

    def __init__(
        self,
        id=None,
        postulacion_id=None,
        practicante_id=None,
        estado=None,
        entregables=None,
    ):
        self.id = id
        self.postulacion_id = postulacion_id
        self.practicante_id = practicante_id
        self.estado = estado or self.ESTADO_EN_CURSO
        self.entregables = entregables or []

    def subir_entregable(self, descripcion=None, archivo_url=None):
        if not descripcion and not archivo_url:
            raise ValueError("Se requiere una descripción o un archivo del entregable")
        if self.estado != self.ESTADO_EN_CURSO:
            raise ValueError("No se pueden subir entregables a una práctica finalizada")

        entregable = Entregable(
            practica_id=self.id,
            descripcion=descripcion,
            archivo_url=archivo_url,
        )
        self.entregables.append(entregable)
        return entregable

    def registrar_evaluacion(self):
        raise NotImplementedError("Registro de evaluación asignado al módulo empresa")

    def finalizar(self):
        raise NotImplementedError("Finalización de práctica asignada al módulo empresa")
