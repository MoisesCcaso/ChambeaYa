# frameworks/sqlalchemy_orm/models/convocatoria_model.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from frameworks.sqlalchemy_orm.database import Base
from .mixins import TimestampMixin

class ConvocatoriaModel(Base, TimestampMixin):
    __tablename__ = 'convocatorias'

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(200), nullable=False)
    descripcion = Column(String(500), nullable=True)
    empresa_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    habilidades_requeridas = Column(JSON, default=[])
    estado = Column(String(20), default='activa')
    fecha_publicacion = Column(DateTime, default=datetime.utcnow)
    fecha_limite_postulacion = Column(DateTime, nullable=False)
    ubicacion = Column(String(200), nullable=True)
    modalidad = Column(String(20), default='presencial')
    num_vacantes = Column(Integer, default=1)
    duracion_meses = Column(Integer, default=3)
    requiere_carnet = Column(Boolean, default=False)

    # Relaciones
    empresa = relationship("UsuarioModel", back_populates="convocatorias", foreign_keys=[empresa_id])
    postulaciones = relationship("PostulacionModel", back_populates="convocatoria", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "titulo": self.titulo,
            "descripcion": self.descripcion,
            "empresa_id": self.empresa_id,
            "habilidades_requeridas": self.habilidades_requeridas or [],
            "estado": self.estado,
            "fecha_publicacion": self.fecha_publicacion.isoformat() if self.fecha_publicacion else None,
            "fecha_limite_postulacion": self.fecha_limite_postulacion.isoformat() if self.fecha_limite_postulacion else None,
            "ubicacion": self.ubicacion,
            "modalidad": self.modalidad,
            "num_vacantes": self.num_vacantes,
            "duracion_meses": self.duracion_meses,
            "requiere_carnet": self.requiere_carnet
        }