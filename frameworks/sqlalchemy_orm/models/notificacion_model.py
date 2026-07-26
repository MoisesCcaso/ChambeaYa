#!/usr/bin/python
# -*- coding: utf-8 -*-

from frameworks.sqlalchemy_orm.database import db
from frameworks.sqlalchemy_orm.models.mixins import TimestampMixin


class NotificacionModel(TimestampMixin, db.Model):
    __tablename__ = "notificaciones"

    id = db.Column(db.Integer, primary_key=True)
    usuario_destino_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False, index=True)
    tipo = db.Column(db.String(50), nullable=False)
    mensaje = db.Column(db.Text, nullable=False)
    metadata = db.Column(db.Text, nullable=True)
    leida = db.Column(db.Boolean, default=False, index=True)
