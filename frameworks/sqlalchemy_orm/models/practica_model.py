#!/usr/bin/python
# -*- coding: utf-8 -*-

from frameworks.sqlalchemy_orm.database import db


class PracticaModel(db.Model):
    __tablename__ = "practicas"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    postulacion_id = db.Column(db.Integer, nullable=False)  # sin FK: postulacion_model.py aún no existe
    practicante_id = db.Column(db.Integer, db.ForeignKey("practicantes.id"), nullable=False)
    estado = db.Column(db.String(20), nullable=False, default="EN_CURSO")

    entregables = db.relationship(
        "EntregableModel", backref="practica", cascade="all, delete-orphan", lazy="select"
    )
    evaluaciones = db.relationship(
        "EvaluacionModel", backref="practica", cascade="all, delete-orphan", lazy="select"
    )