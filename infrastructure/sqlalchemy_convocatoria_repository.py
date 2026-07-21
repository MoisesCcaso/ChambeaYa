#!/usr/bin/python
# -*- coding: utf-8 -*-

import json

from domain.convocatorias.i_convocatoria_repository import IConvocatoriaRepository
from domain.convocatorias.convocatoria import Convocatoria
from frameworks.sqlalchemy_orm.database import db
from frameworks.sqlalchemy_orm.models.convocatoria_model import ConvocatoriaModel


class SqlAlchemyConvocatoriaRepository(IConvocatoriaRepository):
    def __init__(self):
        pass

    def save(self, convocatoria):
        model = None
        if convocatoria.id is not None:
            model = db.session.get(ConvocatoriaModel, convocatoria.id)

        if model is None:
            model = ConvocatoriaModel(empresa_id=convocatoria.empresa_id)
            db.session.add(model)

        model.titulo = convocatoria.titulo
        model.estado = convocatoria.estado
        model.habilidades_requeridas = self._dump_list(convocatoria.habilidades_requeridas)

        db.session.commit()
        return self._to_convocatoria_domain(model)

    def find_by_id(self, convocatoria_id):
        model = db.session.get(ConvocatoriaModel, convocatoria_id)
        return self._to_convocatoria_domain(model)


    def search(self):
        pass

    def _to_convocatoria_domain(self, model):
        if model is None:
            return None

        convocatoria = Convocatoria()
        convocatoria.id = model.id
        convocatoria.empresa_id = model.empresa_id
        convocatoria.titulo = model.titulo
        convocatoria.estado = model.estado
        convocatoria.habilidades_requeridas = self._load_list(model.habilidades_requeridas)

        return convocatoria
    
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