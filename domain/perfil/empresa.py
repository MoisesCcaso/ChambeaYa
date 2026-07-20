#!/usr/bin/python
# -*- coding: utf-8 -*-

class Empresa:
    def __init__(self, id=None, usuario_id=None, ruc=None, verificada=False):
        self.id = id
        self.usuario_id = usuario_id
        self.ruc = ruc
        self.verificada = verificada

    def verificar_ruc(self):
        """
        Delega la validación en el value object RUC (self.ruc)
        y actualiza self.verificada.
        """
        self.verificada = bool(self.ruc) and self.ruc.es_valido()
        return self.verificada