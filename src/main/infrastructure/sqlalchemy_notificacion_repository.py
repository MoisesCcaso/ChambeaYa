#!/usr/bin/python
# -*- coding: utf-8 -*-
import json

from domain.notificaciones.notificacion import Notificacion
from domain.notificaciones.i_notificacion_writer import INotificacionWriter
from domain.notificaciones.i_notificacion_reader import INotificacionReader
from frameworks.sqlalchemy_orm.database import db
from frameworks.sqlalchemy_orm.models.notificacion_model import NotificacionModel


class SqlAlchemyNotificacionRepository(INotificacionWriter, INotificacionReader):
    def save(self, notificacion):
        model = None
        if notificacion.id is not None:
            model = db.session.get(NotificacionModel, notificacion.id)

        if model is None:
            model = NotificacionModel(
                usuario_destino_id=notificacion.usuario_destino_id,
                tipo=notificacion.tipo,
                mensaje=notificacion.mensaje,
            )
            db.session.add(model)

        model.leida = notificacion.leida
        model.metadata_json = self._dump_json(notificacion.metadata)

        db.session.commit()
        return self._to_domain(model)

    def mark_as_read(self, usuario_id, notificacion_id):
        model = NotificacionModel.query.filter_by(
            id=notificacion_id,
            usuario_destino_id=usuario_id,
        ).first()
        if model is None:
            raise ValueError("Notificación no encontrada")
        model.leida = True
        db.session.commit()
        return self._to_domain(model)

    def mark_all_as_read(self, usuario_id):
        NotificacionModel.query.filter_by(
            usuario_destino_id=usuario_id, leida=False
        ).update({"leida": True})
        db.session.commit()

    def find_by_usuario_id(self, usuario_id):
        models = (
            NotificacionModel.query
            .filter_by(usuario_destino_id=usuario_id)
            .order_by(NotificacionModel.created_at.desc())
            .all()
        )
        return [self._to_domain(m) for m in models]

    def find_unread_by_usuario_id(self, usuario_id):
        models = (
            NotificacionModel.query
            .filter_by(usuario_destino_id=usuario_id, leida=False)
            .order_by(NotificacionModel.created_at.desc())
            .all()
        )
        return [self._to_domain(m) for m in models]

    def count_unread(self, usuario_id):
        return NotificacionModel.query.filter_by(
            usuario_destino_id=usuario_id, leida=False
        ).count()

    def _to_domain(self, model):
        if model is None:
            return None
        return Notificacion(
            id=model.id,
            usuario_destino_id=model.usuario_destino_id,
            tipo=model.tipo,
            mensaje=model.mensaje,
            metadata=self._load_json(model.metadata_json),
            leida=model.leida,
            created_at=model.created_at,
        )

    def _dump_json(self, value):
        if not value:
            return "{}"
        return json.dumps(value, ensure_ascii=False)

    def _load_json(self, value):
        if not value:
            return {}
        try:
            parsed = json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return {}
        if not isinstance(parsed, dict):
            return {}
        return parsed
