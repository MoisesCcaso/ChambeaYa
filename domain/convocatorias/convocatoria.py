#!/usr/bin/python
# -*- coding: utf-8 -*-

class Convocatoria:
    ESTADO_BORRADOR = "borrador"
    ESTADO_PUBLICADA = "publicada"
    ESTADO_CERRADA = "cerrada"

    def __init__(self, id=None, empresa_id=None, titulo=None, estado=None):
        self.id = id
        self.empresa_id = empresa_id
        self.titulo = titulo
        self.estado = estado

    def publicar(self):
        """Publica la convocatoria si está en estado borrador."""
        if self.estado != self.ESTADO_BORRADOR:
            raise ValueError("Solo una convocatoria en borrador puede publicarse")

        self.estado = self.ESTADO_PUBLICADA

    def cerrar(self):
        pass
