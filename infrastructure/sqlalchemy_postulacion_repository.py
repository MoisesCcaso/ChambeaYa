# infrastructure/sqlalchemy_postulacion_repository.py
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from domain.convocatorias.postulacion import Postulacion
from domain.convocatorias.i_postulacion_repository import IPostulacionRepository
from frameworks.sqlalchemy_orm.models.postulacion_model import PostulacionModel

class SQLAlchemyPostulacionRepository(IPostulacionRepository):
    """Implementación SQLAlchemy del repositorio de postulaciones."""

    def __init__(self, session: Session):
        self.session = session

    def _to_model(self, postulacion: Postulacion) -> PostulacionModel:
        return PostulacionModel(
            id=postulacion.id,
            convocatoria_id=postulacion.convocatoria_id,
            practicante_id=postulacion.practicante_id,
            fecha_postulacion=postulacion.fecha_postulacion,
            estado=postulacion.estado,
            mensaje_postulacion=postulacion.mensaje_postulacion,
            archivos_adjuntos=postulacion.archivos_adjuntos
        )

    def _to_entity(self, model: PostulacionModel) -> Postulacion:
        return Postulacion(
            id=model.id,
            convocatoria_id=model.convocatoria_id,
            practicante_id=model.practicante_id,
            fecha_postulacion=model.fecha_postulacion,
            estado=model.estado,
            mensaje_postulacion=model.mensaje_postulacion,
            archivos_adjuntos=model.archivos_adjuntos or []
        )

    def guardar(self, postulacion: Postulacion) -> Postulacion:
        try:
            model = self._to_model(postulacion)
            self.session.add(model)
            self.session.commit()
            self.session.refresh(model)
            return self._to_entity(model)
        except SQLAlchemyError as e:
            self.session.rollback()
            raise RuntimeError(f"Error al guardar postulación: {str(e)}")

    def obtener_por_id(self, postulacion_id: int) -> Optional[Postulacion]:
        try:
            model = self.session.query(PostulacionModel).get(postulacion_id)
            return self._to_entity(model) if model else None
        except SQLAlchemyError as e:
            raise RuntimeError(f"Error al obtener postulación: {str(e)}")

    def obtener_por_practicante(self, practicante_id: int) -> List[Postulacion]:
        try:
            models = self.session.query(PostulacionModel).filter(
                PostulacionModel.practicante_id == practicante_id
            ).order_by(PostulacionModel.fecha_postulacion.desc()).all()
            return [self._to_entity(m) for m in models]
        except SQLAlchemyError as e:
            raise RuntimeError(f"Error al obtener postulaciones: {str(e)}")

    def obtener_por_convocatoria(self, convocatoria_id: int) -> List[Postulacion]:
        try:
            models = self.session.query(PostulacionModel).filter(
                PostulacionModel.convocatoria_id == convocatoria_id
            ).order_by(PostulacionModel.fecha_postulacion.desc()).all()
            return [self._to_entity(m) for m in models]
        except SQLAlchemyError as e:
            raise RuntimeError(f"Error al obtener postulaciones: {str(e)}")

    def obtener_por_practicante_y_convocatoria(self, practicante_id: int, convocatoria_id: int) -> Optional[Postulacion]:
        try:
            model = self.session.query(PostulacionModel).filter(
                PostulacionModel.practicante_id == practicante_id,
                PostulacionModel.convocatoria_id == convocatoria_id
            ).first()
            return self._to_entity(model) if model else None
        except SQLAlchemyError as e:
            raise RuntimeError(f"Error al obtener postulación: {str(e)}")

    def actualizar_estado(self, postulacion_id: int, nuevo_estado: str) -> Postulacion:
        try:
            model = self.session.query(PostulacionModel).get(postulacion_id)
            if not model:
                raise ValueError(f"Postulación {postulacion_id} no encontrada")
            model.estado = nuevo_estado
            self.session.commit()
            self.session.refresh(model)
            return self._to_entity(model)
        except SQLAlchemyError as e:
            self.session.rollback()
            raise RuntimeError(f"Error al actualizar estado: {str(e)}")

    def eliminar(self, postulacion_id: int) -> bool:
        try:
            model = self.session.query(PostulacionModel).get(postulacion_id)
            if not model:
                return False
            self.session.delete(model)
            self.session.commit()
            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            raise RuntimeError(f"Error al eliminar postulación: {str(e)}")