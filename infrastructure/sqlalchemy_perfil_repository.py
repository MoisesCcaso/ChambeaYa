#!/usr/bin/python
# -*- coding: utf-8 -*-

import json

from domain.perfil.i_perfil_repository import IPerfilRepository
from domain.perfil.practicante import Practicante
from domain.perfil.empresa import Empresa
from domain.perfil.ruc import RUC
from frameworks.sqlalchemy_orm.database import db
from frameworks.sqlalchemy_orm.models.practicante_model import PracticanteModel
from frameworks.sqlalchemy_orm.models.empresa_model import EmpresaModel


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
        model = None
        if empresa.id is not None:
            model = db.session.get(EmpresaModel, empresa.id)

        if model is None:
            model = EmpresaModel.query.filter_by(usuario_id=empresa.usuario_id).first()

        if model is None:
            model = EmpresaModel(usuario_id=empresa.usuario_id)
            db.session.add(model)

        model.ruc = empresa.ruc.numero if empresa.ruc else None
        model.verificada = empresa.verificada

        db.session.commit()
        return self._to_empresa_domain(model)

    def find_practicante_by_user_id(self, usuario_id):
        model = PracticanteModel.query.filter_by(usuario_id=usuario_id).first()
        return self._to_practicante_domain(model)
    
    def find_practicante_by_id(self, practicante_id):
        model = db.session.get(PracticanteModel, practicante_id)
        return self._to_practicante_domain(model)
    
    def find_empresa_by_user_id(self, usuario_id):
        model = EmpresaModel.query.filter_by(usuario_id=usuario_id).first()
        return self._to_empresa_domain(model)

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
    
    def _to_empresa_domain(self, model):
            if model is None:
                return None

            return Empresa(
                id=model.id,
                usuario_id=model.usuario_id,
                ruc=RUC(numero=model.ruc) if model.ruc else None,
                verificada=model.verificada,
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
