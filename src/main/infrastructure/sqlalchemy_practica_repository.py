#!/usr/bin/python
# -*- coding: utf-8 -*-

from domain.practica_evaluacion.i_practica_repository import IPracticaRepository
from domain.practica_evaluacion.practica import Practica
from domain.practica_evaluacion.entregable import Entregable
from domain.practica_evaluacion.evaluacion import Evaluacion
from frameworks.sqlalchemy_orm.database import db
from frameworks.sqlalchemy_orm.models.practica_model import PracticaModel
from frameworks.sqlalchemy_orm.models.entregable_model import EntregableModel
from frameworks.sqlalchemy_orm.models.evaluacion_model import EvaluacionModel


class SqlAlchemyPracticaRepository(IPracticaRepository):
    def save(self, practica):
        model = None
        if practica.id is not None:
            model = db.session.get(PracticaModel, practica.id)

        if model is None:
            model = PracticaModel(
                postulacion_id=practica.postulacion_id,
                practicante_id=practica.practicante_id,
            )
            db.session.add(model)

        model.estado = practica.estado

        self._sync_collection(
            model.entregables,
            practica.entregables,
            lambda entregable: EntregableModel(
                archivo=entregable.archivo,
                fecha_subida=entregable.fecha_subida,
            ),
        )
        self._sync_collection(
            model.evaluaciones,
            practica.evaluaciones,
            lambda evaluacion: EvaluacionModel(
                puntaje=evaluacion.puntaje,
                fecha_evaluacion=evaluacion.fecha_evaluacion,
            ),
        )

        db.session.commit()
        return self._to_practica_domain(model)

    def _sync_collection(self, model_collection, domain_collection, mapper_func):
        ids_actuales = {
            item.id for item in domain_collection if item.id is not None
        }
        for item_model in list(model_collection):
            if item_model.id not in ids_actuales:
                model_collection.remove(item_model)

        ids_existentes = {item_model.id for item_model in model_collection}
        for item in domain_collection:
            if item.id in ids_existentes:
                continue
            model_collection.append(mapper_func(item))

    def find_by_id(self, practica_id):
        model = db.session.get(PracticaModel, practica_id)
        return self._to_practica_domain(model)

    def find_by_practicante_id(self, practicante_id):
        models = PracticaModel.query.filter_by(practicante_id=practicante_id).all()
        return [self._to_practica_domain(model) for model in models]

    def find_by_postulacion_id(self, postulacion_id):
        model = PracticaModel.query.filter_by(postulacion_id=postulacion_id).first()
        return self._to_practica_domain(model)

    def find_by_empresa_id(self, empresa_id):
        from frameworks.sqlalchemy_orm.models.convocatoria_model import ConvocatoriaModel
        from frameworks.sqlalchemy_orm.models.postulacion_model import PostulacionModel

        models = (
            PracticaModel.query
            .join(PostulacionModel, PracticaModel.postulacion_id == PostulacionModel.id)
            .join(ConvocatoriaModel, PostulacionModel.convocatoria_id == ConvocatoriaModel.id)
            .filter(ConvocatoriaModel.empresa_id == empresa_id)
            .all()
        )
        return [self._to_practica_domain(model) for model in models]

    def _to_practica_domain(self, model):
        if model is None:
            return None

        entregables = [
            Entregable(id=e.id, practica_id=model.id, archivo=e.archivo, fecha_subida=e.fecha_subida)
            for e in model.entregables
        ]
        evaluaciones = [
            Evaluacion(id=ev.id, practica_id=model.id, puntaje=ev.puntaje, fecha_evaluacion=ev.fecha_evaluacion)
            for ev in model.evaluaciones
        ]

        return Practica(
            id=model.id,
            postulacion_id=model.postulacion_id,
            practicante_id=model.practicante_id,
            estado=model.estado,
            entregables=entregables,
            evaluaciones=evaluaciones,
        )
