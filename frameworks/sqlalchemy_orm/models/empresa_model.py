# frameworks/sqlalchemy_orm/models/empresa_model.py
from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from frameworks.sqlalchemy_orm.database import Base
from .mixins import TimestampMixin

class EmpresaModel(Base, TimestampMixin):
    __tablename__ = 'empresas'

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False, unique=True)
    razon_social = Column(String(200), nullable=False)
    ruc = Column(String(11), nullable=False, unique=True)
    descripcion = Column(Text, nullable=True)
    ubicacion = Column(String(200), nullable=True)

    # Relaciones
    usuario = relationship("UsuarioModel", foreign_keys=[usuario_id])
    # NOTA: La relación con convocatorias se define en ConvocatoriaModel