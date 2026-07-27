# infrastructure/sqlalchemy_convocatoria_repository.py
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from domain.convocatorias.convocatoria import Convocatoria
from frameworks.sqlalchemy_orm.models.convocatoria_model import ConvocatoriaModel


class SQLAlchemyConvocatoriaRepository:
    """Repositorio para gestionar convocatorias."""

    def __init__(self, session: Session):
        self.session = session

    def _to_entity(self, model: ConvocatoriaModel) -> Convocatoria:
        """Convierte un modelo a entidad Convocatoria."""
        return Convocatoria(
            id=model.id,
            titulo=model.titulo,
            descripcion=model.descripcion,
            empresa_id=model.empresa_id,
            habilidades_requeridas=model.habilidades_requeridas or [],
            estado=model.estado,
            fecha_publicacion=model.fecha_publicacion,
            fecha_limite_postulacion=model.fecha_limite_postulacion,
            ubicacion=model.ubicacion,
            modalidad=model.modalidad,
            num_vacantes=model.num_vacantes,
            duracion_meses=model.duracion_meses,
            requiere_carnet=model.requiere_carnet
        )

    def _to_model(self, convocatoria: Convocatoria) -> ConvocatoriaModel:
        """Convierte una entidad a modelo ConvocatoriaModel."""
        return ConvocatoriaModel(
            id=convocatoria.id,
            titulo=convocatoria.titulo,
            descripcion=convocatoria.descripcion,
            empresa_id=convocatoria.empresa_id,
            habilidades_requeridas=convocatoria.habilidades_requeridas,
            estado=convocatoria.estado,
            fecha_publicacion=convocatoria.fecha_publicacion,
            fecha_limite_postulacion=convocatoria.fecha_limite_postulacion,
            ubicacion=convocatoria.ubicacion,
            modalidad=convocatoria.modalidad,
            num_vacantes=convocatoria.num_vacantes,
            duracion_meses=convocatoria.duracion_meses,
            requiere_carnet=convocatoria.requiere_carnet
        )

    def guardar(self, convocatoria: Convocatoria) -> Convocatoria:
        """Guarda una nueva convocatoria."""
        try:
            model = self._to_model(convocatoria)
            self.session.add(model)
            self.session.commit()
            self.session.refresh(model)
            return self._to_entity(model)
        except SQLAlchemyError as e:
            self.session.rollback()
            raise RuntimeError(f"Error al guardar convocatoria: {str(e)}")

    def obtener_por_id(self, convocatoria_id: int) -> Optional[Convocatoria]:
        """Obtiene una convocatoria por su ID."""
        try:
            model = self.session.query(ConvocatoriaModel).get(convocatoria_id)
            return self._to_entity(model) if model else None
        except SQLAlchemyError as e:
            raise RuntimeError(f"Error al obtener convocatoria: {str(e)}")

    def listar_activas(self) -> List[Convocatoria]:
        """Lista todas las convocatorias activas."""
        try:
            models = self.session.query(ConvocatoriaModel).filter(
                ConvocatoriaModel.estado == 'activa',
                ConvocatoriaModel.fecha_limite_postulacion >= datetime.now().date()
            ).order_by(ConvocatoriaModel.fecha_publicacion.desc()).all()
            return [self._to_entity(m) for m in models]
        except SQLAlchemyError as e:
            raise RuntimeError(f"Error al listar convocatorias activas: {str(e)}")

    def listar_todas(self) -> List[Convocatoria]:
        """Lista todas las convocatorias."""
        try:
            models = self.session.query(ConvocatoriaModel).order_by(
                ConvocatoriaModel.fecha_publicacion.desc()
            ).all()
            return [self._to_entity(m) for m in models]
        except SQLAlchemyError as e:
            raise RuntimeError(f"Error al listar convocatorias: {str(e)}")

    def listar_por_empresa(self, empresa_id: int) -> List[Convocatoria]:
        """Lista todas las convocatorias de una empresa."""
        try:
            models = self.session.query(ConvocatoriaModel).filter(
                ConvocatoriaModel.empresa_id == empresa_id
            ).order_by(ConvocatoriaModel.fecha_publicacion.desc()).all()
            return [self._to_entity(m) for m in models]
        except SQLAlchemyError as e:
            raise RuntimeError(f"Error al listar convocatorias por empresa: {str(e)}")

    def actualizar(self, convocatoria: Convocatoria) -> Convocatoria:
        """Actualiza una convocatoria existente."""
        try:
            model = self.session.query(ConvocatoriaModel).get(convocatoria.id)
            if not model:
                raise ValueError(f"Convocatoria {convocatoria.id} no encontrada")
            
            model.titulo = convocatoria.titulo
            model.descripcion = convocatoria.descripcion
            model.habilidades_requeridas = convocatoria.habilidades_requeridas
            model.estado = convocatoria.estado
            model.fecha_limite_postulacion = convocatoria.fecha_limite_postulacion
            model.ubicacion = convocatoria.ubicacion
            model.modalidad = convocatoria.modalidad
            model.num_vacantes = convocatoria.num_vacantes
            model.duracion_meses = convocatoria.duracion_meses
            model.requiere_carnet = convocatoria.requiere_carnet
            
            self.session.commit()
            self.session.refresh(model)
            return self._to_entity(model)
        except SQLAlchemyError as e:
            self.session.rollback()
            raise RuntimeError(f"Error al actualizar convocatoria: {str(e)}")

    def eliminar(self, convocatoria_id: int) -> bool:
        """Elimina una convocatoria."""
        try:
            model = self.session.query(ConvocatoriaModel).get(convocatoria_id)
            if not model:
                return False
            self.session.delete(model)
            self.session.commit()
            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            raise RuntimeError(f"Error al eliminar convocatoria: {str(e)}")

    def cerrar(self, convocatoria_id: int) -> Convocatoria:
        """Cierra una convocatoria (cambia estado a 'cerrada')."""
        try:
            model = self.session.query(ConvocatoriaModel).get(convocatoria_id)
            if not model:
                raise ValueError(f"Convocatoria {convocatoria_id} no encontrada")
            model.estado = 'cerrada'
            self.session.commit()
            self.session.refresh(model)
            return self._to_entity(model)
        except SQLAlchemyError as e:
            self.session.rollback()
            raise RuntimeError(f"Error al cerrar convocatoria: {str(e)}")

    def obtener_todos(self) -> List[Convocatoria]:
        """Alias para listar_todas()."""
        return self.listar_todas()