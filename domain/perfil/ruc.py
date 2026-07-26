#!/usr/bin/python
# -*- coding: utf-8 -*-

class RUC:
    def __init__(self, numero=None):
        self.numero = numero

    def es_valido(self):
        """
        Valida el número de RUC (formato + dígito verificador,
        algoritmo SUNAT módulo 11).
        """
        prefijos_validos = ("10", "15", "17", "20")
        factores = (5, 4, 3, 2, 7, 6, 5, 4, 3, 2)
        numero = self.numero

        if not numero or not isinstance(numero, str) or not numero.isdigit() or len(numero) != 11:
            return False

        if numero[:2] not in prefijos_validos:
            return False

        digitos = [int(d) for d in numero[:10]]
        suma = sum(d * f for d, f in zip(digitos, factores))
        resto = suma % 11
        resultado = 11 - resto

        if resultado == 10:
            digito_verificador = 0
        elif resultado == 11:
            digito_verificador = 1
        else:
            digito_verificador = resultado

        return digito_verificador == int(numero[10])