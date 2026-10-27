#!/usr/bin/python
# -*- coding: utf-8 -*-

from datetime import datetime, timezone


class Convocatoria:
    ESTADO_BORRADOR = "borrador"
    ESTADO_PUBLICADA = "publicada"
    ESTADO_CERRADA = "cerrada"

    def __init__(
        self,
        id=None,
        empresa_id=None,
        titulo=None,
        descripcion=None,
        estado=None,
        habilidades_requeridas=None,
        beneficios=None,
        fecha_publicacion=None,
        fecha_cierre=None,
    ):
        self.id = id
        self.empresa_id = empresa_id
        self.titulo = titulo
        self.descripcion = descripcion
        self.estado = estado
        self.habilidades_requeridas = habilidades_requeridas or []
        self.beneficios = beneficios or []
        self.fecha_publicacion = fecha_publicacion
        self.fecha_cierre = fecha_cierre

    def publicar(self):
        """Publica la convocatoria si está en estado borrador."""
        if self.estado != self.ESTADO_BORRADOR:
            raise ValueError("Solo una convocatoria en borrador puede publicarse")

        self.estado = self.ESTADO_PUBLICADA
        self.fecha_publicacion = datetime.now(timezone.utc)
        return self

    def cerrar(self):
        if self.estado != self.ESTADO_PUBLICADA:
            raise ValueError("Solo una convocatoria publicada puede cerrarse")
        self.estado = self.ESTADO_CERRADA
        self.fecha_cierre = datetime.now(timezone.utc)
        return self

    def reabrir(self):
        if self.estado != self.ESTADO_CERRADA:
            raise ValueError("Solo una convocatoria cerrada puede reabrirse")
        self.estado = self.ESTADO_PUBLICADA
        self.fecha_publicacion = datetime.now(timezone.utc)
        self.fecha_cierre = None
        return self

    def validar_eliminacion(self):
        if self.estado != self.ESTADO_BORRADOR:
            raise ValueError("Solo una convocatoria en borrador puede eliminarse")
        return self

    def actualizar(
        self,
        titulo=None,
        descripcion=None,
        habilidades_requeridas=None,
        beneficios=None,
    ):
        if self.estado != self.ESTADO_BORRADOR:
            raise ValueError("Solo una convocatoria en borrador puede editarse")
        if titulo is not None:
            titulo = str(titulo).strip()
            if not titulo:
                raise ValueError("El título es obligatorio")
            self.titulo = titulo
        if descripcion is not None:
            self.descripcion = str(descripcion).strip()
        if habilidades_requeridas is not None:
            if not isinstance(habilidades_requeridas, list):
                raise ValueError("Las habilidades requeridas deben ser una lista")
            self.habilidades_requeridas = []
            for habilidad in habilidades_requeridas:
                self.agregar_habilidad_requerida(habilidad)
        if beneficios is not None:
            if not isinstance(beneficios, list):
                raise ValueError("Los beneficios deben ser una lista")
            self.beneficios = []
            for beneficio in beneficios:
                self.agregar_beneficio(beneficio)
        return self

    def agregar_habilidad_requerida(self, habilidad):
        habilidad_normalizada = self._normalizar_texto(habilidad)
        if habilidad_normalizada and habilidad_normalizada not in self.habilidades_requeridas:
            self.habilidades_requeridas.append(habilidad_normalizada)
        return self
    
    def agregar_beneficio(self, beneficio):
        beneficio_normalizado = self._normalizar_texto(beneficio)
        if beneficio_normalizado and beneficio_normalizado not in self.beneficios:
            self.beneficios.append(beneficio_normalizado)
        return self
    
    def _normalizar_texto(self, valor):
        if valor is None:
            return None
        return str(valor).strip()
