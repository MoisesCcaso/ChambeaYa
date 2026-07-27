# frameworks/sqlalchemy_orm/models/notificacion_model.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from frameworks.sqlalchemy_orm.database import Base
from .mixins import TimestampMixin

class NotificacionModel(Base, TimestampMixin):
    __tablename__ = 'notificaciones'

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    tipo = Column(String(20), default='email')
    canal = Column(String(30), nullable=False)
    asunto = Column(String(200), nullable=False)
    mensaje = Column(Text, nullable=False)
    mensaje_html = Column(Text, nullable=True)
    leida = Column(Boolean, default=False)
    fecha_envio = Column(DateTime, default=datetime.utcnow)
    fecha_lectura = Column(DateTime, nullable=True)
    meta_data = Column(JSON, default={})  # <-- CAMBIADO: metadata -> meta_data
    created_at = Column(DateTime, default=datetime.utcnow)

    usuario = relationship("UsuarioModel", foreign_keys=[usuario_id])

    def to_dict(self):
        return {
            "id": self.id,
            "usuario_id": self.usuario_id,
            "tipo": self.tipo,
            "canal": self.canal,
            "asunto": self.asunto,
            "mensaje": self.mensaje,
            "mensaje_html": self.mensaje_html,
            "leida": self.leida,
            "fecha_envio": self.fecha_envio.isoformat() if self.fecha_envio else None,
            "fecha_lectura": self.fecha_lectura.isoformat() if self.fecha_lectura else None,
            "meta_data": self.meta_data or {}  # <-- CAMBIADO
        }