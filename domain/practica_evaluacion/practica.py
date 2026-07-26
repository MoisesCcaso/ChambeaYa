#!/usr/bin/python
# -*- coding: utf-8 -*-

from domain.practica_evaluacion.entregable import Entregable
from domain.practica_evaluacion.evaluacion import Evaluacion


class Practica:
    ESTADO_EN_CURSO = "EN_CURSO"
    ESTADO_FINALIZADA = "FINALIZADA"

    def __init__(self, id=None, postulacion_id=None, practicante_id=None,
                 estado=None, entregables=None, evaluaciones=None):
        self.id = id
        self.postulacion_id = postulacion_id
        self.practicante_id = practicante_id
        self.estado = estado or self.ESTADO_EN_CURSO
        self.entregables = entregables or []
        self.evaluaciones = evaluaciones or []

    def subir_entregable(self, archivo):
        if self.estado == self.ESTADO_FINALIZADA:
            raise ValueError("No se pueden subir entregables a una práctica finalizada")

        entregable = Entregable.crear(practica_id=self.id, archivo=archivo)
        self.entregables.append(entregable)
        return entregable

    def registrar_evaluacion(self, puntaje):
        if self.estado == self.ESTADO_FINALIZADA:
            raise ValueError("No se pueden registrar evaluaciones en una práctica finalizada")

        evaluacion = Evaluacion.crear(practica_id=self.id, puntaje=puntaje)
        self.evaluaciones.append(evaluacion)
        return evaluacion

    def finalizar(self):
        if not self.entregables:
            raise ValueError("No se puede finalizar una práctica sin entregables registrados")

        self.estado = self.ESTADO_FINALIZADA
        return self

    def obtener_historial_entregables(self):
        return sorted(self.entregables, key=lambda e: e.fecha_subida)

    def obtener_historial_evaluaciones(self):
        return sorted(self.evaluaciones, key=lambda e: e.fecha_evaluacion)