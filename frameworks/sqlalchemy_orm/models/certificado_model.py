# frameworks/sqlalchemy_orm/models/certificado_model.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from frameworks.sqlalchemy_orm.database import Base
from .mixins import TimestampMixin

class CertificadoModel(Base, TimestampMixin):
    __tablename__ = 'certificados'

    id = Column(Integer, primary_key=True, index=True)
    practica_id = Column(Integer, ForeignKey('practicas.id'), nullable=False, unique=True)
    codigo_unico = Column(String(16), nullable=False, unique=True, index=True)
    fecha_emision = Column(DateTime, default=datetime.utcnow)
    fecha_expiracion = Column(DateTime, nullable=True)
    estado = Column(String(20), default='emitido')
    meta_data = Column(JSON, default={})  # <-- CAMBIADO: metadata -> meta_data
    url_verificacion = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    practica = relationship("PracticaModel", foreign_keys=[practica_id])

    def to_dict(self):
        return {
            "id": self.id,
            "practica_id": self.practica_id,
            "codigo_unico": self.codigo_unico,
            "fecha_emision": self.fecha_emision.isoformat() if self.fecha_emision else None,
            "fecha_expiracion": self.fecha_expiracion.isoformat() if self.fecha_expiracion else None,
            "estado": self.estado,
            "meta_data": self.meta_data or {},  # <-- CAMBIADO
            "url_verificacion": self.url_verificacion
        }