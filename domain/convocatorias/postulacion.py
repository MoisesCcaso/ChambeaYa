#!/usr/bin/python
# -*- coding: utf-8 -*-

class Postulacion:
    ESTADO_PENDIENTE = "pendiente"
    ESTADO_ACEPTADA = "aceptada"
    ESTADO_RECHAZADA = "rechazada"
    ESTADO_SELECCIONADA = "seleccionada"

    def __init__(
        self,
        id=None,
        convocatoria_id=None,
        practicante_id=None,
        estado=None,
        fecha_postulacion=None,
    ):
        self.id = id
        self.convocatoria_id = convocatoria_id
        self.practicante_id = practicante_id
        self.estado = estado or self.ESTADO_PENDIENTE
        self.fecha_postulacion = fecha_postulacion

    def postular(self):
        if self.convocatoria_id is None:
            raise ValueError("La convocatoria es obligatoria")
        if self.practicante_id is None:
            raise ValueError("El practicante es obligatorio")

        self.estado = self.ESTADO_PENDIENTE
        return self

    def aceptar(self):
        raise NotImplementedError("Aceptar postulación asignado al módulo empresa")

    def rechazar(self):
        raise NotImplementedError("Rechazar postulación asignado al módulo empresa")

    def seleccionar(self):
        raise NotImplementedError("Seleccionar candidato asignado al módulo empresa")
