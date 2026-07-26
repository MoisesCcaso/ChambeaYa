#!/usr/bin/python
# -*- coding: utf-8 -*-

from frameworks.sqlalchemy_orm.database import db


class EvaluacionModel(db.Model):
    __tablename__ = "evaluaciones"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    practica_id = db.Column(db.Integer, db.ForeignKey("practicas.id"), nullable=False)
    puntaje = db.Column(db.Float, nullable=False)
    fecha_evaluacion = db.Column(db.DateTime, nullable=False)