#!/usr/bin/python
# -*- coding: utf-8 -*-

from domain.practica_evaluacion.practica import Practica


class PracticaFabrica:
    def __init__(self):
        pass

    def iniciar_practica(self, postulacion_id, practicante_id):
        if postulacion_id is None or practicante_id is None:
            raise ValueError("Se requiere postulación y practicante para iniciar la práctica")

        return Practica(
            postulacion_id=postulacion_id,
            practicante_id=practicante_id,
            estado=Practica.ESTADO_EN_CURSO,
        )