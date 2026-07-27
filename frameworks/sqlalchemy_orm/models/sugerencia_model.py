# frameworks/sqlalchemy_orm/models/sugerencia_model.py
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from frameworks.sqlalchemy_orm.database import Base

class SugerenciaModel(Base):
    __tablename__ = 'sugerencias'

    id = Column(Integer, primary_key=True, index=True)
    convocatoria_id = Column(Integer, ForeignKey('convocatorias.id'), nullable=False)
    practicante_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    score_match = Column(Float, nullable=False)
    habilidades_match = Column(JSON, default=[])
    fecha_generacion = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    convocatoria = relationship("ConvocatoriaModel")
    practicante = relationship("UsuarioModel", foreign_keys=[practicante_id])

    def to_dict(self):
        return {
            "id": self.id,
            "convocatoria_id": self.convocatoria_id,
            "practicante_id": self.practicante_id,
            "score_match": self.score_match,
            "habilidades_match": self.habilidades_match or [],
            "fecha_generacion": self.fecha_generacion.isoformat() if self.fecha_generacion else None
        }