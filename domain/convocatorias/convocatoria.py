#!/usr/bin/python
# -*- coding: utf-8 -*-

class Convocatoria:
    ESTADO_BORRADOR = "borrador"
    ESTADO_ABIERTA = "abierta"
    ESTADO_CERRADA = "cerrada"

    def __init__(
        self,
        id=None,
        empresa_id=None,
        titulo=None,
        descripcion=None,
        habilidades_requeridas=None,
        estado=None,
        fecha_publicacion=None,
        fecha_cierre=None,
    ):
        self.id = id
        self.empresa_id = empresa_id
        self.titulo = titulo
        self.descripcion = descripcion
        self.habilidades_requeridas = habilidades_requeridas or []
        self.estado = estado or self.ESTADO_BORRADOR
        self.fecha_publicacion = fecha_publicacion
        self.fecha_cierre = fecha_cierre

    def esta_abierta(self):
        return self.estado == self.ESTADO_ABIERTA

    def publicar(self):
        raise NotImplementedError("Publicación de convocatoria asignada al módulo empresa")

    def cerrar(self):
        raise NotImplementedError("Cierre de convocatoria asignado al módulo empresa")
