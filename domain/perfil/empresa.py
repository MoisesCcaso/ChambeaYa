#!/usr/bin/python
# -*- coding: utf-8 -*-

class Empresa:
    def __init__(self):
        self.id = None
        self.usuario_id = None
        self.ruc = None
        self.verificada = None

    def verificar_ruc(self):
        """
        Delega la validación en el value object RUC (self.ruc)
        y actualiza self.verificada.
        """
        self.verificada = bool(self.ruc) and self.ruc.es_valido()
        return self.verificada