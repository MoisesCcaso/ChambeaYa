#!/usr/bin/python
# -*- coding: utf-8 -*-

class Postulacion:
    ESTADO_PENDIENTE = "pendiente"
    ESTADO_SELECCIONADA = "seleccionada"
    ESTADO_RECHAZADA = "rechazada"
    ESTADO_CANCELADA = "cancelada"

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

    def cancelar(self):
        if self.estado != self.ESTADO_PENDIENTE:
            raise ValueError("Solo una postulación pendiente puede retirarse")
        self.estado = self.ESTADO_CANCELADA
        return self

    def reactivar(self):
        if self.estado != self.ESTADO_CANCELADA:
            raise ValueError("Solo una postulación retirada puede reactivarse")
        self.estado = self.ESTADO_PENDIENTE
        return self

    def reconsiderar(self):
        if self.estado not in (
            self.ESTADO_SELECCIONADA,
            self.ESTADO_RECHAZADA,
        ):
            raise ValueError(
                "Solo una postulación seleccionada o rechazada puede reconsiderarse"
            )
        self.estado = self.ESTADO_PENDIENTE
        return self
