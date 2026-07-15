#!/usr/bin/python
# -*- coding: utf-8 -*-

from domain.auth.i_usuario_repository import IUsuarioRepository
from domain.auth.usuario import Usuario
from frameworks.sqlalchemy_orm.database import db
from frameworks.sqlalchemy_orm.models.usuario_model import UsuarioModel


class SqlAlchemyUsuarioRepository(IUsuarioRepository):
    def __init__(self):
        pass

    def save(self, usuario):
        model = None
        if usuario.id is not None:
            model = db.session.get(UsuarioModel, usuario.id)

        if model is None:
            model = UsuarioModel()
            db.session.add(model)

        model.email = usuario.email
        model.password_hash = usuario.password_hash
        model.tipo = usuario.tipo
        model.estado = usuario.estado
        model.activation_token = usuario.activation_token
        model.activation_token_expires_at = usuario.activation_token_expires_at
        model.password_reset_token = usuario.password_reset_token
        model.password_reset_expires_at = usuario.password_reset_expires_at

        db.session.commit()
        return self._to_domain(model)

    def find_by_email(self, email):
        model = UsuarioModel.query.filter_by(email=email).first()
        return self._to_domain(model)

    def find_by_id(self, usuario_id):
        model = db.session.get(UsuarioModel, usuario_id)
        return self._to_domain(model)

    def find_by_activation_token(self, token):
        model = UsuarioModel.query.filter_by(activation_token=token).first()
        return self._to_domain(model)

    def find_by_password_reset_token(self, token):
        model = UsuarioModel.query.filter_by(password_reset_token=token).first()
        return self._to_domain(model)

    def _to_domain(self, model):
        if model is None:
            return None

        return Usuario(
            id=model.id,
            email=model.email,
            password_hash=model.password_hash,
            tipo=model.tipo,
            estado=model.estado,
            activation_token=model.activation_token,
            activation_token_expires_at=model.activation_token_expires_at,
            password_reset_token=model.password_reset_token,
            password_reset_expires_at=model.password_reset_expires_at,
        )
