#!/usr/bin/python
# -*- coding: utf-8 -*-

from domain.perfil.nombre_completo import NombreCompleto


class Practicante:
    def __init__(
        self,
        id=None,
        usuario_id=None,
        nombres=None,
        apellidos=None,
        dni=None,
        carnet_universitario=None,
        habilidades=None,
        formacion_educativa=None,
        score_reputacion=0.0,
        identidad_verificada=False,
    ):
        self.id = id
        self.usuario_id = usuario_id
        self.nombre_completo = NombreCompleto(nombres, apellidos)
        self.dni = dni
        self.carnet_universitario = carnet_universitario
        self.habilidades = habilidades or []
        self.formacion_educativa = formacion_educativa or []
        self.score_reputacion = score_reputacion
        self.identidad_verificada = identidad_verificada

    @property
    def nombres(self):
        return self.nombre_completo.nombres

    @property
    def apellidos(self):
        return self.nombre_completo.apellidos

    def actualizar_datos(self, nombres=None, apellidos=None, dni=None, carnet_universitario=None):
        if nombres is not None or apellidos is not None:
            self.nombre_completo = NombreCompleto(
                nombres if nombres is not None else self.nombres,
                apellidos if apellidos is not None else self.apellidos,
            ).validar()
        if dni is not None:
            self.dni = dni
        if carnet_universitario is not None:
            self.carnet_universitario = carnet_universitario

        return self

    def agregar_habilidad(self, habilidad):
        habilidad_normalizada = self._normalizar_texto(habilidad)
        if habilidad_normalizada and habilidad_normalizada not in self.habilidades:
            self.habilidades.append(habilidad_normalizada)
        self.calcular_score()

        return self

    def agregar_formacion(self, formacion):
        formacion_normalizada = self._normalizar_texto(formacion)
        if formacion_normalizada and formacion_normalizada not in self.formacion_educativa:
            self.formacion_educativa.append(formacion_normalizada)
        self.calcular_score()

        return self

    def reemplazar_habilidades(self, habilidades):
        if not isinstance(habilidades, list):
            raise ValueError("Las habilidades deben ser una lista")
        self.habilidades = self._normalizar_elementos(habilidades)
        self.calcular_score()
        return self

    def reemplazar_formacion(self, formaciones):
        if not isinstance(formaciones, list):
            raise ValueError("La formación educativa debe ser una lista")
        self.formacion_educativa = self._normalizar_elementos(formaciones)
        self.calcular_score()
        return self

    def verificar_identidad(self):
        if not self.dni and not self.carnet_universitario:
            raise ValueError("Se requiere DNI o carnet universitario")
        if self.dni and (not str(self.dni).isdigit() or len(str(self.dni)) != 8):
            raise ValueError("El DNI debe contener exactamente 8 dígitos")
        if self.carnet_universitario and len(str(self.carnet_universitario).strip()) < 4:
            raise ValueError("El carnet universitario no es válido")

        self.identidad_verificada = True
        self.calcular_score()
        return self

    def revocar_verificacion_identidad(self):
        self.identidad_verificada = False
        self.calcular_score()
        return self

    def calcular_score(self):
        base = 0.0
        base += min(len(self.habilidades), 10) * 5
        base += min(len(self.formacion_educativa), 5) * 5
        if self.identidad_verificada:
            base += 25

        self.score_reputacion = min(base, 100.0)
        return self.score_reputacion

    def _normalizar_texto(self, valor):
        if valor is None:
            return None

        return str(valor).strip()

    def _normalizar_elementos(self, valores):
        normalizados = []
        for valor in valores:
            valor_normalizado = self._normalizar_texto(valor)
            if valor_normalizado and valor_normalizado not in normalizados:
                normalizados.append(valor_normalizado)
        return normalizados
