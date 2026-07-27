# infrastructure/sqlalchemy_notificacion_repository.py
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from domain.notificacion.i_notificacion_repository import Notificacion, INotificacionRepository
from frameworks.sqlalchemy_orm.models.notificacion_model import NotificacionModel

class SQLAlchemyNotificacionRepository(INotificacionRepository):
    """Implementación SQLAlchemy del repositorio de notificaciones."""

    def __init__(self, session: Session):
        self.session = session

    def _to_model(self, notificacion: Notificacion) -> NotificacionModel:
        return NotificacionModel(
            id=notificacion.id,
            usuario_id=notificacion.usuario_id,
            tipo=notificacion.tipo,
            canal=notificacion.canal,
            asunto=notificacion.asunto,
            mensaje=notificacion.mensaje,
            mensaje_html=notificacion.mensaje_html,
            leida=notificacion.leida,
            fecha_envio=notificacion.fecha_envio,
            fecha_lectura=notificacion.fecha_lectura,
            metadata=notificacion.metadata
        )

    def _to_entity(self, model: NotificacionModel) -> Notificacion:
        return Notificacion(
            id=model.id,
            usuario_id=model.usuario_id,
            tipo=model.tipo,
            canal=model.canal,
            asunto=model.asunto,
            mensaje=model.mensaje,
            mensaje_html=model.mensaje_html,
            leida=model.leida,
            fecha_envio=model.fecha_envio,
            fecha_lectura=model.fecha_lectura,
            metadata=model.metadata or {}
        )

    def guardar(self, notificacion: Notificacion) -> Notificacion:
        try:
            model = self._to_model(notificacion)
            self.session.add(model)
            self.session.commit()
            self.session.refresh(model)
            return self._to_entity(model)
        except SQLAlchemyError as e:
            self.session.rollback()
            raise RuntimeError(f"Error al guardar notificación: {str(e)}")

    def obtener_por_usuario(self, usuario_id: int, limit: int = 50) -> List[Notificacion]:
        try:
            models = self.session.query(NotificacionModel).filter(
                NotificacionModel.usuario_id == usuario_id
            ).order_by(NotificacionModel.fecha_envio.desc()).limit(limit).all()
            return [self._to_entity(m) for m in models]
        except SQLAlchemyError as e:
            raise RuntimeError(f"Error al obtener notificaciones: {str(e)}")

    def obtener_no_leidas(self, usuario_id: int) -> List[Notificacion]:
        try:
            models = self.session.query(NotificacionModel).filter(
                NotificacionModel.usuario_id == usuario_id,
                NotificacionModel.leida == False
            ).order_by(NotificacionModel.fecha_envio.desc()).all()
            return [self._to_entity(m) for m in models]
        except SQLAlchemyError as e:
            raise RuntimeError(f"Error al obtener notificaciones no leídas: {str(e)}")

    def marcar_como_leida(self, notificacion_id: int) -> Optional[Notificacion]:
        try:
            model = self.session.query(NotificacionModel).get(notificacion_id)
            if not model:
                return None
            model.leida = True
            model.fecha_lectura = datetime.utcnow()
            self.session.commit()
            self.session.refresh(model)
            return self._to_entity(model)
        except SQLAlchemyError as e:
            self.session.rollback()
            raise RuntimeError(f"Error al marcar notificación como leída: {str(e)}")

    def marcar_todas_como_leidas(self, usuario_id: int) -> int:
        try:
            now = datetime.utcnow()
            result = self.session.query(NotificacionModel).filter(
                NotificacionModel.usuario_id == usuario_id,
                NotificacionModel.leida == False
            ).update({"leida": True, "fecha_lectura": now})
            self.session.commit()
            return result
        except SQLAlchemyError as e:
            self.session.rollback()
            raise RuntimeError(f"Error al marcar todas como leídas: {str(e)}")

    def eliminar_antiguas(self, dias: int) -> int:
        try:
            fecha_limite = datetime.utcnow() - timedelta(days=dias)
            result = self.session.query(NotificacionModel).filter(
                NotificacionModel.fecha_envio < fecha_limite
            ).delete()
            self.session.commit()
            return result
        except SQLAlchemyError as e:
            self.session.rollback()
            raise RuntimeError(f"Error al eliminar notificaciones antiguas: {str(e)}")