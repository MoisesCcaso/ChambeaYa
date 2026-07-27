# frameworks/sqlalchemy_orm/models/evaluacion_model.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from frameworks.sqlalchemy_orm.database import Base
from .mixins import TimestampMixin

class EvaluacionModel(Base, TimestampMixin):
    __tablename__ = 'evaluaciones'

    id = Column(Integer, primary_key=True, index=True)
    entregable_id = Column(Integer, ForeignKey('entregables.id'), nullable=False)
    puntaje = Column(Float, nullable=False)
    comentario = Column(Text, nullable=True)
    criterios_evaluacion = Column(JSON, default=[])  # <-- Sin conflicto, este es seguro
    fecha_evaluacion = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    entregable = relationship("EntregableModel", back_populates="evaluaciones")

    def to_dict(self):
        return {
            "id": self.id,
            "entregable_id": self.entregable_id,
            "puntaje": self.puntaje,
            "comentario": self.comentario,
            "criterios_evaluacion": self.criterios_evaluacion or [],
            "fecha_evaluacion": self.fecha_evaluacion.isoformat() if self.fecha_evaluacion else None
        }