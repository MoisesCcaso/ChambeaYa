#!/usr/bin/python
# -*- coding: utf-8 -*-

class Convocatoria:
    ESTADO_BORRADOR = "borrador"
    ESTADO_PUBLICADA = "publicada"
    ESTADO_CERRADA = "cerrada"

    def __init__(self, id=None, empresa_id=None, titulo=None, descripcion=None, estado=None, 
                 habilidades_requeridas=None, beneficios=None):
        self.id = id
        self.empresa_id = empresa_id
        self.titulo = titulo
        self.descripcion = descripcion
        self.estado = estado
        self.habilidades_requeridas = habilidades_requeridas or []
        self.beneficios = beneficios or []

    def publicar(self):
        """Publica la convocatoria si está en estado borrador."""
        if self.estado != self.ESTADO_BORRADOR:
            raise ValueError("Solo una convocatoria en borrador puede publicarse")

        self.estado = self.ESTADO_PUBLICADA

    def cerrar(self):
        pass

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
