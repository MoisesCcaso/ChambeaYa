#!/usr/bin/python
# -*- coding: utf-8 -*-

from frameworks.sqlalchemy_orm.database import db


class EntregableModel(db.Model):
    __tablename__ = "entregables"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    practica_id = db.Column(db.Integer, db.ForeignKey("practicas.id"), nullable=False)
    archivo = db.Column(db.String(255), nullable=False)
    fecha_subida = db.Column(db.DateTime, nullable=False)