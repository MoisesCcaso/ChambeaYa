#!/usr/bin/python
# -*- coding: utf-8 -*-

from frameworks.sqlalchemy_orm.database import db
from frameworks.sqlalchemy_orm.models.mixins import TimestampMixin


class CertificadoModel(TimestampMixin, db.Model):
    __tablename__ = "certificados"

    id = db.Column(db.Integer, primary_key=True)
    practica_id = db.Column(db.Integer, db.ForeignKey("practicas.id"), nullable=False)
    codigo_qr_valor = db.Column(db.String(80), unique=True, nullable=True)
    codigo_qr_url_verificacion = db.Column(db.String(255), nullable=True)
    codigo_qr_hash = db.Column(db.String(64), nullable=True)
    documento_url = db.Column(db.String(255), nullable=True)
    documento_hash = db.Column(db.String(64), nullable=True)