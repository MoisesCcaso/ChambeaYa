#!/usr/bin/python
# -*- coding: utf-8 -*-

class Notificacion:
    TIPO_POSTULACION_SELECCIONADA = "POSTULACION_SELECCIONADA"
    TIPO_EVALUACION_DISPONIBLE = "EVALUACION_DISPONIBLE"
    TIPO_CERTIFICADO_EMITIDO = "CERTIFICADO_EMITIDO"
    TIPO_NUEVAS_SUGERENCIAS = "NUEVAS_SUGERENCIAS"

    def __init__(self, id=None, usuario_destino_id=None, tipo=None, mensaje=None,
                 metadata=None, leida=False, created_at=None):
        self.id = id
        self.usuario_destino_id = usuario_destino_id
        self.tipo = tipo
        self.mensaje = mensaje
        self.metadata = metadata or {}
        self.leida = leida
        self.created_at = created_at

    def marcar_como_leida(self):
        self.leida = True
