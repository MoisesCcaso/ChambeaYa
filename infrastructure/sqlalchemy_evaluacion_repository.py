# infrastructure/sqlalchemy_evaluacion_repository.py
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from domain.practica_evaluacion.evaluacion import Evaluacion
from frameworks.sqlalchemy_orm.models.evaluacion_model import EvaluacionModel
from frameworks.sqlalchemy_orm.models.entregable_model import EntregableModel
from frameworks.sqlalchemy_orm.models.practica_model import PracticaModel
from frameworks.sqlalchemy_orm.models.postulacion_model import PostulacionModel


class SQLAlchemyEvaluacionRepository:
    """Repositorio para gestionar evaluaciones."""

    def __init__(self, session: Session):
        self.session = session

    def _to_entity(self, model: EvaluacionModel) -> Evaluacion:
        """Convierte un modelo a entidad Evaluacion."""
        return Evaluacion(
            id=model.id,
            entregable_id=model.entregable_id,
            puntaje=model.puntaje,
            comentario=model.comentario,
            criterios_evaluacion=model.criterios_evaluacion or [],
            fecha_evaluacion=model.fecha_evaluacion
        )

    def guardar(self, evaluacion: Evaluacion) -> Evaluacion:
        """Guarda una nueva evaluación."""
        try:
            model = EvaluacionModel(
                entregable_id=evaluacion.entregable_id,
                puntaje=evaluacion.puntaje,
                comentario=evaluacion.comentario,
                criterios_evaluacion=evaluacion.criterios_evaluacion,
                fecha_evaluacion=evaluacion.fecha_evaluacion
            )
            self.session.add(model)
            self.session.commit()
            self.session.refresh(model)
            return self._to_entity(model)
        except SQLAlchemyError as e:
            self.session.rollback()
            raise RuntimeError(f"Error al guardar evaluación: {str(e)}")

    def obtener_por_entregable(self, entregable_id: int) -> Optional[Evaluacion]:
        """Obtiene la evaluación de un entregable."""
        try:
            model = self.session.query(EvaluacionModel).filter(
                EvaluacionModel.entregable_id == entregable_id
            ).first()
            return self._to_entity(model) if model else None
        except SQLAlchemyError as e:
            raise RuntimeError(f"Error al obtener evaluación: {str(e)}")

    def obtener_por_practicante(self, practicante_id: int) -> List[Evaluacion]:
        """Obtiene todas las evaluaciones de un practicante."""
        try:
            models = self.session.query(EvaluacionModel).join(
                EntregableModel, EvaluacionModel.entregable_id == EntregableModel.id
            ).join(
                PracticaModel, EntregableModel.practica_id == PracticaModel.id
            ).join(
                PostulacionModel, PracticaModel.postulacion_id == PostulacionModel.id
            ).filter(
                PostulacionModel.practicante_id == practicante_id
            ).all()
            return [self._to_entity(m) for m in models]
        except SQLAlchemyError as e:
            raise RuntimeError(f"Error al obtener evaluaciones: {str(e)}")

    def obtener_todas(self) -> List[Evaluacion]:
        """Obtiene todas las evaluaciones."""
        try:
            models = self.session.query(EvaluacionModel).all()
            return [self._to_entity(m) for m in models]
        except SQLAlchemyError as e:
            raise RuntimeError(f"Error al obtener evaluaciones: {str(e)}")