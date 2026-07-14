#!/usr/bin/python
# -*- coding: utf-8 -*-

class UsuarioController:
    def __init__(self, usuario_application_service=None):
        self.usuario_application_service = usuario_application_service

    def register(self, payload):
        self._require_service()
        usuario = self.usuario_application_service.register_user(
            email=payload.get("email"),
            password=payload.get("password"),
            tipo=payload.get("tipo"),
        )

        return self._serialize_usuario(usuario), 201

    def login(self, payload):
        self._require_service()
        usuario = self.usuario_application_service.authenticate(
            email=payload.get("email"),
            password=payload.get("password"),
        )

        return self._serialize_usuario(usuario), 200

    def recover_password(self):
        pass

    def activate_account(self):
        pass

    def get_authenticated_user(self, usuario_id):
        self._require_service()
        usuario = self.usuario_application_service.find_by_id(usuario_id)
        if usuario is None:
            raise ValueError("Usuario no encontrado")

        return self._serialize_usuario(usuario), 200

    def _require_service(self):
        if self.usuario_application_service is None:
            raise RuntimeError("UsuarioController requiere un servicio de aplicación")

    def _serialize_usuario(self, usuario):
        return {
            "id": usuario.id,
            "email": usuario.email,
            "tipo": usuario.tipo,
            "estado": usuario.estado,
        }
