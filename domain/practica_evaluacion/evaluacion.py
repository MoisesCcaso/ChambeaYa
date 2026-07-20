#!/usr/bin/python
# -*- coding: utf-8 -*-

from datetime import datetime

PUNTAJE_APROBACION = 60.0


class Evaluacion:
    def __init__(self, id=None, practica_id=None, puntaje=None, fecha_evaluacion=None):
        self.id = id
        self.practica_id = practica_id
        self.puntaje = puntaje
        self.fecha_evaluacion = fecha_evaluacion

    @staticmethod
    def crear(practica_id, puntaje):
        if puntaje is None:
            raise ValueError("Debe indicarse un puntaje")
        if puntaje < 0 or puntaje > 100:
            raise ValueError("El puntaje debe estar entre 0 y 100")

        return Evaluacion(
            practica_id=practica_id,
            puntaje=puntaje,
            fecha_evaluacion=datetime.utcnow(),
        )

    def esta_aprobada(self):
        if self.puntaje is None:
            return False
        return self.puntaje >= PUNTAJE_APROBACION