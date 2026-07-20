#!/usr/bin/python
# -*- coding: utf-8 -*-

import json

from domain.perfil.i_perfil_repository import IPerfilRepository
from domain.perfil.practicante import Practicante
from frameworks.sqlalchemy_orm.database import db
from frameworks.sqlalchemy_orm.models.practicante_model import PracticanteModel


class SqlAlchemyPerfilRepository(IPerfilRepository):
    def __init__(self):
        pass

    def save_practicante(self, practicante):
        model = None
        if practicante.id is not None:
            model = db.session.get(PracticanteModel, practicante.id)

        if model is None:
            model = PracticanteModel.query.filter_by(usuario_id=practicante.usuario_id).first()

        if model is None:
            model = PracticanteModel(usuario_id=practicante.usuario_id)
            db.session.add(model)

        model.nombres = practicante.nombres
        model.apellidos = practicante.apellidos
        model.dni = practicante.dni
        model.carnet_universitario = practicante.carnet_universitario
        model.habilidades = self._dump_list(practicante.habilidades)
        model.formacion_educativa = self._dump_list(practicante.formacion_educativa)
        model.score_reputacion = practicante.score_reputacion
        model.identidad_verificada = practicante.identidad_verificada

        db.session.commit()
        return self._to_practicante_domain(model)

    def save_empresa(self, empresa):
        pass

    def find_practicante_by_user_id(self, usuario_id):
        model = PracticanteModel.query.filter_by(usuario_id=usuario_id).first()
        return self._to_practicante_domain(model)

    def find_empresa_by_user_id(self, usuario_id):
        pass

    def _to_practicante_domain(self, model):
        if model is None:
            return None

        return Practicante(
            id=model.id,
            usuario_id=model.usuario_id,
            nombres=model.nombres,
            apellidos=model.apellidos,
            dni=model.dni,
            carnet_universitario=model.carnet_universitario,
            habilidades=self._load_list(model.habilidades),
            formacion_educativa=self._load_list(model.formacion_educativa),
            score_reputacion=model.score_reputacion,
            identidad_verificada=model.identidad_verificada,
        )

    def _dump_list(self, values):
        return json.dumps(values or [], ensure_ascii=False)

    def _load_list(self, value):
        if not value:
            return []

        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return []

        if not isinstance(parsed, list):
            return []

        return parsed
