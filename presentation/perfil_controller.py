#!/usr/bin/python
# -*- coding: utf-8 -*-

class PerfilController:
    def __init__(self, perfil_application_service=None):
        self.perfil_application_service = perfil_application_service

    def get_practicante(self, usuario_id):
        self._require_service()
        practicante = self.perfil_application_service.get_practicante_profile(usuario_id)
        if practicante is None:
            return None, 404

        return self._serialize_practicante(practicante), 200

    def update_practicante(self, usuario_id, payload):
        self._require_service()
        practicante = self.perfil_application_service.update_practicante(usuario_id, payload)
        return self._serialize_practicante(practicante), 200

    def add_habilidad(self, usuario_id, payload):
        self._require_service()
        practicante = self.perfil_application_service.add_habilidad(
            usuario_id,
            payload.get("habilidad"),
        )
        return self._serialize_practicante(practicante), 200

    def add_formacion(self, usuario_id, payload):
        self._require_service()
        practicante = self.perfil_application_service.add_formacion(
            usuario_id,
            payload.get("formacion"),
        )
        return self._serialize_practicante(practicante), 200

    def update_empresa(self):
        raise NotImplementedError("El perfil de empresa no pertenece a RF.2")

    def verify_identity(self, usuario_id, payload):
        self._require_service()
        practicante = self.perfil_application_service.register_identity(
            usuario_id,
            dni=payload.get("dni"),
            carnet_universitario=payload.get("carnet_universitario"),
        )
        return self._serialize_practicante(practicante), 200

    def get_reputation_score(self, usuario_id):
        self._require_service()
        return {
            "score_reputacion": self.perfil_application_service.get_reputation_score(usuario_id)
        }, 200

    def _require_service(self):
        if self.perfil_application_service is None:
            raise RuntimeError("PerfilController requiere un servicio de aplicación")

    def _serialize_practicante(self, practicante):
        return {
            "id": practicante.id,
            "usuario_id": practicante.usuario_id,
            "nombres": practicante.nombres,
            "apellidos": practicante.apellidos,
            "dni": practicante.dni,
            "carnet_universitario": practicante.carnet_universitario,
            "habilidades": practicante.habilidades,
            "formacion_educativa": practicante.formacion_educativa,
            "score_reputacion": practicante.score_reputacion,
            "identidad_verificada": practicante.identidad_verificada,
        }
