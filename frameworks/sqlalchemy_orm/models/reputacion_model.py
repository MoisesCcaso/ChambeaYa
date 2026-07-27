# frameworks/sqlalchemy_orm/models/reputacion_model.py
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .mixins import TimestampMixin
from frameworks.sqlalchemy_orm.database import Base

class ReputacionModel(Base, TimestampMixin):
    __tablename__ = 'reputaciones'

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False, unique=True)
    score_total = Column(Float, default=0.0)
    evaluaciones_count = Column(Integer, default=0)
    practicas_completadas = Column(Integer, default=0)
    promedio_puntaje = Column(Float, default=0.0)
    ultima_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    usuario = relationship("UsuarioModel", foreign_keys=[usuario_id])

    def to_dict(self):
        return {
            "id": self.id,
            "usuario_id": self.usuario_id,
            "score_total": self.score_total,
            "evaluaciones_count": self.evaluaciones_count,
            "practicas_completadas": self.practicas_completadas,
            "promedio_puntaje": self.promedio_puntaje,
            "ultima_actualizacion": self.ultima_actualizacion.isoformat() if self.ultima_actualizacion else None
        }