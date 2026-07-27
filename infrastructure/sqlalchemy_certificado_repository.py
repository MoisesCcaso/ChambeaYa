# infrastructure/sqlalchemy_certificado_repository.py
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from domain.certificacion.certificado import Certificado
from domain.certificacion.reputacion import Reputacion
from domain.certificacion.i_certificado_repository import ICertificadoRepository, IReputacionRepository
from frameworks.sqlalchemy_orm.models.certificado_model import CertificadoModel
from frameworks.sqlalchemy_orm.models.reputacion_model import ReputacionModel
from frameworks.sqlalchemy_orm.models.practica_model import PracticaModel
from frameworks.sqlalchemy_orm.models.postulacion_model import PostulacionModel

class SQLAlchemyCertificadoRepository(ICertificadoRepository):
    """Implementación SQLAlchemy del repositorio de certificados."""

    def __init__(self, session: Session):
        self.session = session

    def _to_model(self, certificado: Certificado) -> CertificadoModel:
        return CertificadoModel(
            id=certificado.id,
            practica_id=certificado.practica_id,
            codigo_unico=certificado.codigo_unico,
            fecha_emision=certificado.fecha_emision,
            fecha_expiracion=certificado.fecha_expiracion,
            estado=certificado.estado,
            metadatos=certificado.metadatos,
            url_verificacion=certificado.url_verificacion
        )

    def _to_entity(self, model: CertificadoModel) -> Certificado:
        return Certificado(
            id=model.id,
            practica_id=model.practica_id,
            codigo_unico=model.codigo_unico,
            fecha_emision=model.fecha_emision,
            estado=model.estado,
            metadatos=model.metadatos or {},
            url_verificacion=model.url_verificacion,
            fecha_expiracion=model.fecha_expiracion
        )

    def guardar(self, certificado: Certificado) -> Certificado:
        try:
            model = self._to_model(certificado)
            self.session.add(model)
            self.session.commit()
            self.session.refresh(model)
            return self._to_entity(model)
        except SQLAlchemyError as e:
            self.session.rollback()
            raise RuntimeError(f"Error al guardar certificado: {str(e)}")

    def obtener_por_id(self, certificado_id: int) -> Optional[Certificado]:
        try:
            model = self.session.query(CertificadoModel).get(certificado_id)
            return self._to_entity(model) if model else None
        except SQLAlchemyError as e:
            raise RuntimeError(f"Error al obtener certificado: {str(e)}")

    def obtener_por_codigo(self, codigo_unico: str) -> Optional[Certificado]:
        try:
            model = self.session.query(CertificadoModel).filter(
                CertificadoModel.codigo_unico == codigo_unico
            ).first()
            return self._to_entity(model) if model else None
        except SQLAlchemyError as e:
            raise RuntimeError(f"Error al obtener certificado: {str(e)}")

    def obtener_por_practica(self, practica_id: int) -> Optional[Certificado]:
        try:
            model = self.session.query(CertificadoModel).filter(
                CertificadoModel.practica_id == practica_id
            ).first()
            return self._to_entity(model) if model else None
        except SQLAlchemyError as e:
            raise RuntimeError(f"Error al obtener certificado: {str(e)}")

    def obtener_por_practicante(self, practicante_id: int) -> List[Certificado]:
        try:
            models = self.session.query(CertificadoModel).join(
                PracticaModel, CertificadoModel.practica_id == PracticaModel.id
            ).join(
                PostulacionModel, PracticaModel.postulacion_id == PostulacionModel.id
            ).filter(
                PostulacionModel.practicante_id == practicante_id
            ).all()
            return [self._to_entity(m) for m in models]
        except SQLAlchemyError as e:
            raise RuntimeError(f"Error al obtener certificados: {str(e)}")

    def actualizar(self, certificado: Certificado) -> Certificado:
        try:
            model = self.session.query(CertificadoModel).get(certificado.id)
            if not model:
                raise ValueError(f"Certificado {certificado.id} no encontrado")
            model.estado = certificado.estado
            model.metadatos = certificado.metadatos
            model.url_verificacion = certificado.url_verificacion
            self.session.commit()
            self.session.refresh(model)
            return self._to_entity(model)
        except SQLAlchemyError as e:
            self.session.rollback()
            raise RuntimeError(f"Error al actualizar certificado: {str(e)}")


class SQLAlchemyReputacionRepository(IReputacionRepository):
    """Implementación SQLAlchemy del repositorio de reputación."""

    def __init__(self, session: Session):
        self.session = session

    def _to_model(self, reputacion: Reputacion) -> ReputacionModel:
        return ReputacionModel(
            id=reputacion.id,
            usuario_id=reputacion.usuario_id,
            score_total=reputacion.score_total,
            evaluaciones_count=reputacion.evaluaciones_count,
            practicas_completadas=reputacion.practicas_completadas,
            promedio_puntaje=reputacion.promedio_puntaje,
            ultima_actualizacion=reputacion.ultima_actualizacion
        )

    def _to_entity(self, model: ReputacionModel) -> Reputacion:
        return Reputacion(
            id=model.id,
            usuario_id=model.usuario_id,
            score_total=model.score_total,
            evaluaciones_count=model.evaluaciones_count,
            practicas_completadas=model.practicas_completadas,
            promedio_puntaje=model.promedio_puntaje,
            ultima_actualizacion=model.ultima_actualizacion
        )

    def guardar(self, reputacion: Reputacion) -> Reputacion:
        try:
            model = self._to_model(reputacion)
            self.session.add(model)
            self.session.commit()
            self.session.refresh(model)
            return self._to_entity(model)
        except SQLAlchemyError as e:
            self.session.rollback()
            raise RuntimeError(f"Error al guardar reputación: {str(e)}")

    def obtener_por_usuario(self, usuario_id: int) -> Optional[Reputacion]:
        try:
            model = self.session.query(ReputacionModel).filter(
                ReputacionModel.usuario_id == usuario_id
            ).first()
            return self._to_entity(model) if model else None
        except SQLAlchemyError as e:
            raise RuntimeError(f"Error al obtener reputación: {str(e)}")

    def actualizar(self, reputacion: Reputacion) -> Reputacion:
        try:
            model = self.session.query(ReputacionModel).get(reputacion.id)
            if not model:
                raise ValueError(f"Reputación {reputacion.id} no encontrada")
            model.score_total = reputacion.score_total
            model.evaluaciones_count = reputacion.evaluaciones_count
            model.practicas_completadas = reputacion.practicas_completadas
            model.promedio_puntaje = reputacion.promedio_puntaje
            model.ultima_actualizacion = reputacion.ultima_actualizacion
            self.session.commit()
            self.session.refresh(model)
            return self._to_entity(model)
        except SQLAlchemyError as e:
            self.session.rollback()
            raise RuntimeError(f"Error al actualizar reputación: {str(e)}")

    def obtener_top_practicantes(self, limit: int = 10) -> List[Reputacion]:
        try:
            models = self.session.query(ReputacionModel).order_by(
                ReputacionModel.score_total.desc()
            ).limit(limit).all()
            return [self._to_entity(m) for m in models]
        except SQLAlchemyError as e:
            raise RuntimeError(f"Error al obtener top practicantes: {str(e)}")