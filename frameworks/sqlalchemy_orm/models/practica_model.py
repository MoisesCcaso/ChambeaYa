# frameworks/sqlalchemy_orm/models/practica_model.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from frameworks.sqlalchemy_orm.database import Base

class EstadoPracticaDB(str, enum.Enum):
    EN_PROGRESO = "en_progreso"
    COMPLETADA = "completada"
    CANCELADA = "cancelada"

class PracticaModel(Base):
    __tablename__ = 'practicas'

    id = Column(Integer, primary_key=True, index=True)
    postulacion_id = Column(Integer, ForeignKey('postulaciones.id'), nullable=False, unique=True)
    fecha_inicio = Column(DateTime, nullable=False)
    fecha_fin = Column(DateTime, nullable=True)
    estado = Column(Enum(EstadoPracticaDB), default=EstadoPracticaDB.EN_PROGRESO)
    horario_trabajo = Column(Text, nullable=True)
    supervisor_nombre = Column(String(100), nullable=True)
    supervisor_contacto = Column(String(100), nullable=True)
    acta_inicio_url = Column(String(255), nullable=True)
    acta_termino_url = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    postulacion = relationship("PostulacionModel", foreign_keys=[postulacion_id])
    entregables = relationship("EntregableModel", back_populates="practica", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "postulacion_id": self.postulacion_id,
            "fecha_inicio": self.fecha_inicio.isoformat() if self.fecha_inicio else None,
            "fecha_fin": self.fecha_fin.isoformat() if self.fecha_fin else None,
            "estado": self.estado.value if self.estado else None,
            "horario_trabajo": self.horario_trabajo,
            "supervisor_nombre": self.supervisor_nombre,
            "supervisor_contacto": self.supervisor_contacto,
            "acta_inicio_url": self.acta_inicio_url,
            "acta_termino_url": self.acta_termino_url
        }