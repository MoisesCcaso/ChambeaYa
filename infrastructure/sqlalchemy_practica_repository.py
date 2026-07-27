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

        ids_existentes = {e.id for e in model.entregables}
        for entregable in practica.entregables:
            if entregable.id in ids_existentes:
                continue
            model.entregables.append(EntregableModel(
                archivo=entregable.archivo,
                fecha_subida=entregable.fecha_subida,
            ))

        ids_evaluaciones_existentes = {e.id for e in model.evaluaciones}
        for evaluacion in practica.evaluaciones:
            if evaluacion.id in ids_evaluaciones_existentes:
                continue
            model.evaluaciones.append(EvaluacionModel(
                puntaje=evaluacion.puntaje,
                fecha_evaluacion=evaluacion.fecha_evaluacion,
            ))

        db.session.commit()
        return self._to_practica_domain(model)

    def find_by_id(self, practica_id):
        model = db.session.get(PracticaModel, practica_id)
        return self._to_practica_domain(model)

    def find_by_practicante_id(self, practicante_id):
        models = PracticaModel.query.filter_by(practicante_id=practicante_id).all()
        return [self._to_practica_domain(model) for model in models]

    def find_by_postulacion_id(self, postulacion_id):
        model = PracticaModel.query.filter_by(postulacion_id=postulacion_id).first()
        return self._to_practica_domain(model)

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
