# infrastructure/sqlalchemy_practica_repository.py
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from domain.practica_evaluacion.practica import Practica
from domain.practica_evaluacion.i_practica_repository import IPracticaRepository
from frameworks.sqlalchemy_orm.models.practica_model import PracticaModel
from frameworks.sqlalchemy_orm.models.postulacion_model import PostulacionModel

class SQLAlchemyPracticaRepository(IPracticaRepository):
    """Implementación SQLAlchemy del repositorio de prácticas."""

    def __init__(self, session: Session):
        self.session = session

    def _to_model(self, practica: Practica) -> PracticaModel:
        return PracticaModel(
            id=practica.id,
            postulacion_id=practica.postulacion_id,
            fecha_inicio=practica.fecha_inicio,
            fecha_fin=practica.fecha_fin,
            estado=practica.estado,
            horario_trabajo=practica.horario_trabajo,
            supervisor_nombre=practica.supervisor_nombre,
            supervisor_contacto=practica.supervisor_contacto,
            acta_inicio_url=practica.acta_inicio_url,
            acta_termino_url=practica.acta_termino_url
        )

    def _to_entity(self, model: PracticaModel) -> Practica:
        return Practica(
            id=model.id,
            postulacion_id=model.postulacion_id,
            fecha_inicio=model.fecha_inicio,
            fecha_fin=model.fecha_fin,
            estado=model.estado,
            horario_trabajo=model.horario_trabajo,
            supervisor_nombre=model.supervisor_nombre,
            supervisor_contacto=model.supervisor_contacto,
            acta_inicio_url=model.acta_inicio_url,
            acta_termino_url=model.acta_termino_url
        )

    def guardar(self, practica: Practica) -> Practica:
        try:
            model = self._to_model(practica)
            self.session.add(model)
            self.session.commit()
            self.session.refresh(model)
            return self._to_entity(model)
        except SQLAlchemyError as e:
            self.session.rollback()
            raise RuntimeError(f"Error al guardar práctica: {str(e)}")

    def obtener_por_id(self, practica_id: int) -> Optional[Practica]:
        try:
            model = self.session.query(PracticaModel).get(practica_id)
            return self._to_entity(model) if model else None
        except SQLAlchemyError as e:
            raise RuntimeError(f"Error al obtener práctica: {str(e)}")

    def obtener_por_postulacion(self, postulacion_id: int) -> Optional[Practica]:
        try:
            model = self.session.query(PracticaModel).filter(
                PracticaModel.postulacion_id == postulacion_id
            ).first()
            return self._to_entity(model) if model else None
        except SQLAlchemyError as e:
            raise RuntimeError(f"Error al obtener práctica: {str(e)}")

    def obtener_por_practicante(self, practicante_id: int) -> List[Practica]:
        try:
            models = self.session.query(PracticaModel).join(
                PostulacionModel, PracticaModel.postulacion_id == PostulacionModel.id
            ).filter(
                PostulacionModel.practicante_id == practicante_id
            ).order_by(PracticaModel.fecha_inicio.desc()).all()
            return [self._to_entity(m) for m in models]
        except SQLAlchemyError as e:
            raise RuntimeError(f"Error al obtener prácticas: {str(e)}")

    def obtener_por_empresa(self, empresa_id: int) -> List[Practica]:
        try:
            # Asumiendo que ConvocatoriaModel tiene relación con EmpresaModel
            models = self.session.query(PracticaModel).join(
                PostulacionModel, PracticaModel.postulacion_id == PostulacionModel.id
            ).join(
                ConvocatoriaModel, PostulacionModel.convocatoria_id == ConvocatoriaModel.id
            ).filter(
                ConvocatoriaModel.empresa_id == empresa_id
            ).order_by(PracticaModel.fecha_inicio.desc()).all()
            return [self._to_entity(m) for m in models]
        except SQLAlchemyError as e:
            raise RuntimeError(f"Error al obtener prácticas: {str(e)}")

    def actualizar(self, practica: Practica) -> Practica:
        try:
            model = self.session.query(PracticaModel).get(practica.id)
            if not model:
                raise ValueError(f"Práctica {practica.id} no encontrada")
            model.fecha_fin = practica.fecha_fin
            model.estado = practica.estado
            model.horario_trabajo = practica.horario_trabajo
            model.supervisor_nombre = practica.supervisor_nombre
            model.supervisor_contacto = practica.supervisor_contacto
            model.acta_inicio_url = practica.acta_inicio_url
            model.acta_termino_url = practica.acta_termino_url
            self.session.commit()
            self.session.refresh(model)
            return self._to_entity(model)
        except SQLAlchemyError as e:
            self.session.rollback()
            raise RuntimeError(f"Error al actualizar práctica: {str(e)}")