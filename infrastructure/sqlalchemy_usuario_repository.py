# infrastructure/sqlalchemy_usuario_repository.py
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from domain.auth.usuario import Usuario
from frameworks.sqlalchemy_orm.models.usuario_model import UsuarioModel


class SQLAlchemyUsuarioRepository:
    """Repositorio para gestionar usuarios."""

    def __init__(self, session: Session):
        self.session = session

    def _to_entity(self, model: UsuarioModel) -> Usuario:
        """Convierte un modelo a entidad Usuario."""
        return Usuario(
            id=model.id,
            email=model.email,
            password_hash=model.password_hash,
            nombre=model.nombre,
            apellido=model.apellido,
            rol=model.rol,
            activo=model.activo,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    def _to_model(self, usuario: Usuario) -> UsuarioModel:
        """Convierte una entidad a modelo UsuarioModel."""
        return UsuarioModel(
            id=usuario.id,
            email=usuario.email,
            password_hash=usuario.password_hash,
            nombre=usuario.nombre,
            apellido=usuario.apellido,
            rol=usuario.rol,
            activo=usuario.activo
        )

    def guardar(self, usuario: Usuario) -> Usuario:
        """Guarda un nuevo usuario."""
        try:
            model = self._to_model(usuario)
            self.session.add(model)
            self.session.commit()
            self.session.refresh(model)
            return self._to_entity(model)
        except SQLAlchemyError as e:
            self.session.rollback()
            raise RuntimeError(f"Error al guardar usuario: {str(e)}")

    def obtener_por_id(self, usuario_id: int) -> Optional[Usuario]:
        """Obtiene un usuario por su ID."""
        try:
            model = self.session.query(UsuarioModel).get(usuario_id)
            return self._to_entity(model) if model else None
        except SQLAlchemyError as e:
            raise RuntimeError(f"Error al obtener usuario: {str(e)}")

    def obtener_por_email(self, email: str) -> Optional[Usuario]:
        """Obtiene un usuario por su email."""
        try:
            model = self.session.query(UsuarioModel).filter(
                UsuarioModel.email == email
            ).first()
            return self._to_entity(model) if model else None
        except SQLAlchemyError as e:
            raise RuntimeError(f"Error al obtener usuario por email: {str(e)}")

    def obtener_por_rol(self, rol: str) -> List[Usuario]:
        """Obtiene todos los usuarios con un rol específico."""
        try:
            models = self.session.query(UsuarioModel).filter(
                UsuarioModel.rol == rol
            ).all()
            return [self._to_entity(m) for m in models]
        except SQLAlchemyError as e:
            raise RuntimeError(f"Error al obtener usuarios por rol: {str(e)}")

    def obtener_todos(self) -> List[Usuario]:
        """Obtiene todos los usuarios."""
        try:
            models = self.session.query(UsuarioModel).all()
            return [self._to_entity(m) for m in models]
        except SQLAlchemyError as e:
            raise RuntimeError(f"Error al obtener todos los usuarios: {str(e)}")

    def actualizar(self, usuario: Usuario) -> Usuario:
        """Actualiza un usuario existente."""
        try:
            model = self.session.query(UsuarioModel).get(usuario.id)
            if not model:
                raise ValueError(f"Usuario {usuario.id} no encontrado")
            
            model.email = usuario.email
            model.nombre = usuario.nombre
            model.apellido = usuario.apellido
            model.rol = usuario.rol
            model.activo = usuario.activo
            
            if usuario.password_hash:
                model.password_hash = usuario.password_hash
            
            self.session.commit()
            self.session.refresh(model)
            return self._to_entity(model)
        except SQLAlchemyError as e:
            self.session.rollback()
            raise RuntimeError(f"Error al actualizar usuario: {str(e)}")

    def eliminar(self, usuario_id: int) -> bool:
        """Elimina un usuario."""
        try:
            model = self.session.query(UsuarioModel).get(usuario_id)
            if not model:
                return False
            self.session.delete(model)
            self.session.commit()
            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            raise RuntimeError(f"Error al eliminar usuario: {str(e)}")

    def activar(self, usuario_id: int) -> Usuario:
        """Activa un usuario."""
        try:
            model = self.session.query(UsuarioModel).get(usuario_id)
            if not model:
                raise ValueError(f"Usuario {usuario_id} no encontrado")
            model.activo = True
            self.session.commit()
            self.session.refresh(model)
            return self._to_entity(model)
        except SQLAlchemyError as e:
            self.session.rollback()
            raise RuntimeError(f"Error al activar usuario: {str(e)}")

    def desactivar(self, usuario_id: int) -> Usuario:
        """Desactiva un usuario."""
        try:
            model = self.session.query(UsuarioModel).get(usuario_id)
            if not model:
                raise ValueError(f"Usuario {usuario_id} no encontrado")
            model.activo = False
            self.session.commit()
            self.session.refresh(model)
            return self._to_entity(model)
        except SQLAlchemyError as e:
            self.session.rollback()
            raise RuntimeError(f"Error al desactivar usuario: {str(e)}")