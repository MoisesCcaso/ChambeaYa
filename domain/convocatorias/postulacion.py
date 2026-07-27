#!/usr/bin/python
# -*- coding: utf-8 -*-

class Postulacion:
    ESTADO_PENDIENTE = "pendiente"
    ESTADO_SELECCIONADA = "seleccionada"
    ESTADO_RECHAZADA = "rechazada"

    def __init__(self, id=None, convocatoria_id=None, practicante_id=None, estado=None):
       self.id = id
       self.convocatoria_id = convocatoria_id
       self.practicante_id = practicante_id
       self.estado = estado or self.ESTADO_PENDIENTE

    def aceptar(self):
        return self.seleccionar()

    def rechazar(self):
        if self.estado != self.ESTADO_PENDIENTE:
            raise ValueError("Solo una postulación pendiente puede rechazarse")
        self.estado = self.ESTADO_RECHAZADA
        return self

    def seleccionar(self):
        """Selecciona la postulación si está pendiente."""
        if self.estado != self.ESTADO_PENDIENTE:
            raise ValueError("Solo una postulación pendiente puede seleccionarse")

        self.estado = self.ESTADO_SELECCIONADA
        return self
