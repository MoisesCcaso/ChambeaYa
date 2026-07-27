# frameworks/sqlalchemy_orm/models/usuario_model.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from frameworks.sqlalchemy_orm.database import Base
from .mixins import TimestampMixin

class UsuarioModel(Base, TimestampMixin):
    __tablename__ = 'usuarios'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), nullable=False, unique=True, index=True)
    password_hash = Column(String(200), nullable=False)
    nombre = Column(String(50), nullable=False)
    apellido = Column(String(50), nullable=False)
    rol = Column(String(20), nullable=False)  # practicante, empresa, admin
    activo = Column(Boolean, default=True)
    activation_token = Column(String(100), nullable=True, index=True)
    password_reset_token = Column(String(100), nullable=True, index=True)

    # Relaciones
    practicante = relationship("PracticanteModel", back_populates="usuario", uselist=False, cascade="all, delete-orphan")
    empresa = relationship("EmpresaModel", back_populates="usuario", uselist=False, cascade="all, delete-orphan")
    convocatorias = relationship("ConvocatoriaModel", back_populates="empresa", cascade="all, delete-orphan")
    postulaciones = relationship("PostulacionModel", foreign_keys="PostulacionModel.practicante_id", cascade="all, delete-orphan")
    notificaciones = relationship("NotificacionModel", back_populates="usuario", cascade="all, delete-orphan")
    reputacion = relationship("ReputacionModel", back_populates="usuario", uselist=False, cascade="all, delete-orphan")