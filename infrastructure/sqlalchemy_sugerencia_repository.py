# infrastructure/sqlalchemy_sugerencia_repository.py
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from domain.matching.sugerencia import Sugerencia
from domain.matching.i_sugerencia_repository import ISugerenciaRepository
from frameworks.sqlalchemy_orm.models.sugerencia_model import SugerenciaModel

class SQLAlchemySugerenciaRepository(ISugerenciaRepository):
    """Implementación SQLAlchemy del repositorio de sugerencias."""

    def __init__(self, session: Session):
        self.session = session

    def _to_model(self, sugerencia: Sugerencia) -> SugerenciaModel:
        return SugerenciaModel(
            id=sugerencia.id,
            convocatoria_id=sugerencia.convocatoria_id,
            practicante_id=sugerencia.practicante_id,
            score_match=sugerencia.score_match,
            habilidades_match=sugerencia.habilidades_match,
            fecha_generacion=sugerencia.fecha_generacion
        )

    def _to_entity(self, model: SugerenciaModel) -> Sugerencia:
        return Sugerencia(
            id=model.id,
            convocatoria_id=model.convocatoria_id,
            practicante_id=model.practicante_id,
            score_match=model.score_match,
            habilidades_match=model.habilidades_match or [],
            fecha_generacion=model.fecha_generacion
        )

    def guardar(self, sugerencia: Sugerencia) -> Sugerencia:
        try:
            model = self._to_model(sugerencia)
            self.session.add(model)
            self.session.commit()
            self.session.refresh(model)
            return self._to_entity(model)
        except SQLAlchemyError as e:
            self.session.rollback()
            raise RuntimeError(f"Error al guardar sugerencia: {str(e)}")

    def guardar_multiples(self, sugerencias: List[Sugerencia]) -> List[Sugerencia]:
        try:
            models = [self._to_model(s) for s in sugerencias]
            self.session.add_all(models)
            self.session.commit()
            return [self._to_entity(m) for m in models]
        except SQLAlchemyError as e:
            self.session.rollback()
            raise RuntimeError(f"Error al guardar sugerencias: {str(e)}")

    def obtener_por_practicante(self, practicante_id: int) -> List[Sugerencia]:
        try:
            models = self.session.query(SugerenciaModel).filter(
                SugerenciaModel.practicante_id == practicante_id
            ).order_by(SugerenciaModel.score_match.desc()).all()
            return [self._to_entity(m) for m in models]
        except SQLAlchemyError as e:
            raise RuntimeError(f"Error al obtener sugerencias: {str(e)}")

    def obtener_por_convocatoria(self, convocatoria_id: int) -> List[Sugerencia]:
        try:
            models = self.session.query(SugerenciaModel).filter(
                SugerenciaModel.convocatoria_id == convocatoria_id
            ).order_by(SugerenciaModel.score_match.desc()).all()
            return [self._to_entity(m) for m in models]
        except SQLAlchemyError as e:
            raise RuntimeError(f"Error al obtener sugerencias: {str(e)}")

    def eliminar_por_practicante(self, practicante_id: int) -> int:
        try:
            deleted = self.session.query(SugerenciaModel).filter(
                SugerenciaModel.practicante_id == practicante_id
            ).delete()
            self.session.commit()
            return deleted
        except SQLAlchemyError as e:
            self.session.rollback()
            raise RuntimeError(f"Error al eliminar sugerencias: {str(e)}")

    def limpiar_antiguas(self, dias: int) -> int:
        try:
            fecha_limite = datetime.utcnow() - timedelta(days=dias)
            deleted = self.session.query(SugerenciaModel).filter(
                SugerenciaModel.fecha_generacion < fecha_limite
            ).delete()
            self.session.commit()
            return deleted
        except SQLAlchemyError as e:
            self.session.rollback()
            raise RuntimeError(f"Error al limpiar sugerencias antiguas: {str(e)}")