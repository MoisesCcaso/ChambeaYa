# infrastructure/sqlalchemy_perfil_repository.py
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from domain.perfil.practicante import Practicante
from domain.perfil.empresa import Empresa
from frameworks.sqlalchemy_orm.models.practicante_model import PracticanteModel
from frameworks.sqlalchemy_orm.models.empresa_model import EmpresaModel
from frameworks.sqlalchemy_orm.models.usuario_model import UsuarioModel

class SQLAlchemyPerfilRepository:
    """Repositorio para gestionar perfiles de practicantes y empresas."""

    def __init__(self, session: Session):
        self.session = session

    # ==================== MÉTODOS PARA PRACTICANTE ====================

    def obtener_practicante_por_usuario_id(self, usuario_id: int) -> Optional[Practicante]:
        """Obtiene el perfil de un practicante por su ID de usuario."""
        try:
            model = self.session.query(PracticanteModel).filter(
                PracticanteModel.usuario_id == usuario_id
            ).first()
            return self._to_entity_practicante(model) if model else None
        except SQLAlchemyError as e:
            raise RuntimeError(f"Error al obtener practicante: {str(e)}")

    def guardar_practicante(self, practicante: Practicante) -> Practicante:
        """Guarda o actualiza un perfil de practicante."""
        try:
            model = self.session.query(PracticanteModel).filter(
                PracticanteModel.usuario_id == practicante.usuario_id
            ).first()
            
            if model:
                # Actualizar existente
                model.habilidades = practicante.habilidades
                model.formacion_educativa = practicante.formacion_educativa
                model.carnet_universitario = practicante.carnet_universitario
                model.dni = practicante.dni
            else:
                # Crear nuevo
                model = PracticanteModel(
                    usuario_id=practicante.usuario_id,
                    habilidades=practicante.habilidades,
                    formacion_educativa=practicante.formacion_educativa,
                    carnet_universitario=practicante.carnet_universitario,
                    dni=practicante.dni
                )
                self.session.add(model)
            
            self.session.commit()
            self.session.refresh(model)
            return self._to_entity_practicante(model)
        except SQLAlchemyError as e:
            self.session.rollback()
            raise RuntimeError(f"Error al guardar practicante: {str(e)}")

    def _to_entity_practicante(self, model: PracticanteModel) -> Practicante:
        """Convierte un modelo a entidad Practicante."""
        return Practicante(
            id=model.id,
            usuario_id=model.usuario_id,
            habilidades=model.habilidades or [],
            formacion_educativa=model.formacion_educativa or [],
            carnet_universitario=model.carnet_universitario,
            dni=model.dni
        )

    # ==================== MÉTODOS PARA EMPRESA ====================

    def obtener_empresa_por_usuario_id(self, usuario_id: int) -> Optional[Empresa]:
        """Obtiene el perfil de una empresa por su ID de usuario."""
        try:
            model = self.session.query(EmpresaModel).filter(
                EmpresaModel.usuario_id == usuario_id
            ).first()
            return self._to_entity_empresa(model) if model else None
        except SQLAlchemyError as e:
            raise RuntimeError(f"Error al obtener empresa: {str(e)}")

    def guardar_empresa(self, empresa: Empresa) -> Empresa:
        """Guarda o actualiza un perfil de empresa."""
        try:
            model = self.session.query(EmpresaModel).filter(
                EmpresaModel.usuario_id == empresa.usuario_id
            ).first()
            
            if model:
                model.razon_social = empresa.razon_social
                model.ruc = empresa.ruc
                model.descripcion = empresa.descripcion
                model.ubicacion = empresa.ubicacion
            else:
                model = EmpresaModel(
                    usuario_id=empresa.usuario_id,
                    razon_social=empresa.razon_social,
                    ruc=empresa.ruc,
                    descripcion=empresa.descripcion,
                    ubicacion=empresa.ubicacion
                )
                self.session.add(model)
            
            self.session.commit()
            self.session.refresh(model)
            return self._to_entity_empresa(model)
        except SQLAlchemyError as e:
            self.session.rollback()
            raise RuntimeError(f"Error al guardar empresa: {str(e)}")

    def _to_entity_empresa(self, model: EmpresaModel) -> Empresa:
        """Convierte un modelo a entidad Empresa."""
        return Empresa(
            id=model.id,
            usuario_id=model.usuario_id,
            razon_social=model.razon_social,
            ruc=model.ruc,
            descripcion=model.descripcion,
            ubicacion=model.ubicacion
        )

    # ==================== MÉTODOS GENÉRICOS ====================

    def obtener_por_usuario_id(self, usuario_id: int):
        """Obtiene el perfil (practicante o empresa) por ID de usuario."""
        # Primero buscar como practicante
        practicante = self.obtener_practicante_por_usuario_id(usuario_id)
        if practicante:
            return practicante
        
        # Si no, buscar como empresa
        return self.obtener_empresa_por_usuario_id(usuario_id)

    def obtener_todos_practicantes(self) -> List[Practicante]:
        """Obtiene todos los perfiles de practicantes."""
        try:
            models = self.session.query(PracticanteModel).all()
            return [self._to_entity_practicante(m) for m in models]
        except SQLAlchemyError as e:
            raise RuntimeError(f"Error al obtener practicantes: {str(e)}")

    def obtener_todos_empresas(self) -> List[Empresa]:
        """Obtiene todos los perfiles de empresas."""
        try:
            models = self.session.query(EmpresaModel).all()
            return [self._to_entity_empresa(m) for m in models]
        except SQLAlchemyError as e:
            raise RuntimeError(f"Error al obtener empresas: {str(e)}")