#!/usr/bin/python
# -*- coding: utf-8 -*-

import json

from domain.convocatorias.i_convocatoria_repository import IConvocatoriaRepository
from domain.convocatorias.convocatoria import Convocatoria
from frameworks.sqlalchemy_orm.database import db
from frameworks.sqlalchemy_orm.models.convocatoria_model import ConvocatoriaModel


class SqlAlchemyConvocatoriaRepository(IConvocatoriaRepository):
    def save(self, convocatoria):
        model = None
        if convocatoria.id is not None:
            model = db.session.get(ConvocatoriaModel, convocatoria.id)

        if model is None:
            model = ConvocatoriaModel(empresa_id=convocatoria.empresa_id)
            db.session.add(model)

        model.titulo = convocatoria.titulo
        model.descripcion = convocatoria.descripcion
        model.estado = convocatoria.estado
        model.habilidades_requeridas = self._dump_list(convocatoria.habilidades_requeridas)
        model.beneficios = self._dump_list(convocatoria.beneficios)
        model.fecha_publicacion = convocatoria.fecha_publicacion
        model.fecha_cierre = convocatoria.fecha_cierre
        db.session.commit()
        return self._to_convocatoria_domain(model)

    def find_by_id(self, convocatoria_id):
        model = db.session.get(ConvocatoriaModel, convocatoria_id)
        return self._to_convocatoria_domain(model)


    def find_all(self):
        models = ConvocatoriaModel.query.all()
        return [self._to_convocatoria_domain(model) for model in models]

    def find_by_empresa_id(self, empresa_id):
        models = ConvocatoriaModel.query.filter_by(empresa_id=empresa_id).all()
        return [self._to_convocatoria_domain(model) for model in models]

    def delete(self, convocatoria_id):
        model = db.session.get(ConvocatoriaModel, convocatoria_id)
        if model is None:
            return False
        db.session.delete(model)
        db.session.commit()
        return True

    def search(self, query=None, estado=None):
        statement = ConvocatoriaModel.query
        if estado:
            statement = statement.filter_by(estado=estado)
        if query:
            pattern = f"%{str(query).strip()}%"
            statement = statement.filter(
                db.or_(
                    ConvocatoriaModel.titulo.ilike(pattern),
                    ConvocatoriaModel.descripcion.ilike(pattern),
                    ConvocatoriaModel.habilidades_requeridas.ilike(pattern),
                )
            )
        models = statement.order_by(ConvocatoriaModel.created_at.desc()).all()
        return [self._to_convocatoria_domain(model) for model in models]

    def _to_convocatoria_domain(self, model):
        if model is None:
            return None

        convocatoria = Convocatoria()
        convocatoria.id = model.id
        convocatoria.empresa_id = model.empresa_id
        convocatoria.titulo = model.titulo
        convocatoria.estado = model.estado
        convocatoria.habilidades_requeridas = self._load_list(model.habilidades_requeridas)
        convocatoria.descripcion = model.descripcion
        convocatoria.beneficios = self._load_list(model.beneficios)
        convocatoria.fecha_publicacion = model.fecha_publicacion
        convocatoria.fecha_cierre = model.fecha_cierre
        
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
