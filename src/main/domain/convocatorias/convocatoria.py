#!/usr/bin/python
# -*- coding: utf-8 -*-

from datetime import datetime, timezone
from domain.convocatorias.estado_convocatoria import estado_desde_nombre


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
        self._estado = estado_desde_nombre(estado, fecha_cierre)
        self.habilidades_requeridas = habilidades_requeridas or []
        self.beneficios = beneficios or []
        self.fecha_publicacion = fecha_publicacion

    @property
    def estado(self):
        return self._estado.nombre

    @estado.setter
    def estado(self, nombre):
        self._estado = estado_desde_nombre(nombre)

    @property
    def fecha_cierre(self):
        """Solo tiene valor mientras la convocatoria esta cerrada."""
        return self._estado.fecha_cierre

    def publicar(self):
        """Publica la convocatoria si está en estado borrador."""
        self._estado = self._estado.publicar()
        self.fecha_publicacion = datetime.now(timezone.utc)
        return self

    def cerrar(self):
        self._estado = self._estado.cerrar(datetime.now(timezone.utc))
        return self

    def reabrir(self):
        self._estado = self._estado.reabrir()
        self.fecha_publicacion = datetime.now(timezone.utc)
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
            self.titulo = self.normalizar_titulo(titulo)
        if descripcion is not None:
            self.descripcion = str(descripcion).strip()
        if habilidades_requeridas is not None:
            self.validar_lista(habilidades_requeridas, "Las habilidades requeridas")
            self.habilidades_requeridas = []
            for habilidad in habilidades_requeridas:
                self.agregar_habilidad_requerida(habilidad)
        if beneficios is not None:
            self.validar_lista(beneficios, "Los beneficios")
            self.beneficios = []
            for beneficio in beneficios:
                self.agregar_beneficio(beneficio)
        return self

    @staticmethod
    def normalizar_titulo(titulo):
        titulo_normalizado = str(titulo).strip() if titulo is not None else ""
        if not titulo_normalizado:
            raise ValueError("El título es obligatorio")
        return titulo_normalizado

    @staticmethod
    def validar_lista(valores, nombre):
        if not isinstance(valores, list):
            raise ValueError(f"{nombre} deben ser una lista")
        return valores

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
