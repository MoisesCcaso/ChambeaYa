#!/usr/bin/python
# -*- coding: utf-8 -*-

class Entregable:
    def __init__(
        self,
        id=None,
        practica_id=None,
        descripcion=None,
        archivo_url=None,
        fecha_subida=None,
    ):
        self.id = id
        self.practica_id = practica_id
        self.descripcion = descripcion
        self.archivo_url = archivo_url
        self.fecha_subida = fecha_subida
