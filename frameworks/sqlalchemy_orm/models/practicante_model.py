# frameworks/sqlalchemy_orm/models/practicante_model.py
from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship
from frameworks.sqlalchemy_orm.database import Base
from .mixins import TimestampMixin

class PracticanteModel(Base, TimestampMixin):
    __tablename__ = 'practicantes'

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False, unique=True)
    habilidades = Column(JSON, default=[])
    formacion_educativa = Column(JSON, default=[])
    carnet_universitario = Column(String(20), nullable=True)
    dni = Column(String(8), nullable=True)

    # Relaciones
    usuario = relationship("UsuarioModel", foreign_keys=[usuario_id])