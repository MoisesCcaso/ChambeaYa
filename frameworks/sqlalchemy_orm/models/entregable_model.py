# frameworks/sqlalchemy_orm/models/entregable_model.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .mixins import TimestampMixin
from frameworks.sqlalchemy_orm.database import Base

class EstadoEntregableDB(str, enum.Enum):
    PENDIENTE = "pendiente"
    ENTREGADO = "entregado"
    REVISADO = "revisado"
    APROBADO = "aprobado"
    RECHAZADO = "rechazado"

class EntregableModel(Base, TimestampMixin):
    __tablename__ = 'entregables'

    id = Column(Integer, primary_key=True, index=True)
    practica_id = Column(Integer, ForeignKey('practicas.id'), nullable=False)
    titulo = Column(String(200), nullable=False)
    descripcion = Column(Text, nullable=True)
    fecha_limite_entrega = Column(DateTime, nullable=False)
    fecha_entrega = Column(DateTime, nullable=True)
    archivo_url = Column(String(255), nullable=True)
    estado = Column(Enum(EstadoEntregableDB), default=EstadoEntregableDB.PENDIENTE)
    comentario_empresa = Column(Text, nullable=True)
    fecha_evaluacion = Column(DateTime, nullable=True)

    # Relaciones
    practica = relationship("PracticaModel", back_populates="entregables")
    evaluaciones = relationship("EvaluacionModel", back_populates="entregable", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "practica_id": self.practica_id,
            "titulo": self.titulo,
            "descripcion": self.descripcion,
            "fecha_limite_entrega": self.fecha_limite_entrega.isoformat() if self.fecha_limite_entrega else None,
            "fecha_entrega": self.fecha_entrega.isoformat() if self.fecha_entrega else None,
            "archivo_url": self.archivo_url,
            "estado": self.estado.value if self.estado else None,
            "comentario_empresa": self.comentario_empresa,
            "fecha_evaluacion": self.fecha_evaluacion.isoformat() if self.fecha_evaluacion else None
        }