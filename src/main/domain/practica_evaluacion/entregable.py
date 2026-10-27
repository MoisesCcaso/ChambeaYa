#!/usr/bin/python
# -*- coding: utf-8 -*-

from datetime import datetime, timezone


class Entregable:
    def __init__(self, id=None, practica_id=None, archivo=None, fecha_subida=None):
        self.id = id
        self.practica_id = practica_id
        self.archivo = archivo
        self.fecha_subida = fecha_subida

    @staticmethod
    def crear(practica_id, archivo):
        if not archivo or not str(archivo).strip():
            raise ValueError("Debe adjuntarse un archivo para el entregable")

        return Entregable(
            practica_id=practica_id,
            archivo=str(archivo).strip(),
            fecha_subida=datetime.now(timezone.utc),
        )