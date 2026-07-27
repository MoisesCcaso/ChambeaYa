# frameworks/sqlalchemy_orm/models/postulacion_model.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from frameworks.sqlalchemy_orm.database import Base
from .mixins import TimestampMixin

class PostulacionModel(Base, TimestampMixin):
    __tablename__ = 'postulaciones'

    id = Column(Integer, primary_key=True, index=True)
    convocatoria_id = Column(Integer, ForeignKey('convocatorias.id'), nullable=False)
    practicante_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    fecha_postulacion = Column(DateTime, default=datetime.utcnow)
    estado = Column(String(20), default='pendiente')
    mensaje_postulacion = Column(Text, nullable=True)
    archivos_adjuntos = Column(JSON, default=[])

    # Relaciones
    convocatoria = relationship("ConvocatoriaModel", back_populates="postulaciones")
    practicante = relationship("UsuarioModel", foreign_keys=[practicante_id])

    def to_dict(self):
        return {
            "id": self.id,
            "convocatoria_id": self.convocatoria_id,
            "practicante_id": self.practicante_id,
            "fecha_postulacion": self.fecha_postulacion.isoformat() if self.fecha_postulacion else None,
            "estado": self.estado,
            "mensaje_postulacion": self.mensaje_postulacion,
            "archivos_adjuntos": self.archivos_adjuntos or []
        }