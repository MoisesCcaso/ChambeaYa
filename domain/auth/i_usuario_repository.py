# domain/auth/i_usuario_repository.py
# LAB 12 - SOLID: I (Segregación de Interfaces)

from abc import ABC, abstractmethod
from typing import List, Optional
from domain.auth.usuario import Usuario


class IUsuarioRepositoryLectura(ABC):
    """Interfaz específica para operaciones de lectura de usuarios."""
    
    @abstractmethod
    def obtener_por_id(self, usuario_id: int) -> Optional[Usuario]:
        pass

    @abstractmethod
    def obtener_por_email(self, email: str) -> Optional[Usuario]:
        pass

    @abstractmethod
    def obtener_por_rol(self, rol: str) -> List[Usuario]:
        pass


class IUsuarioRepositoryEscritura(ABC):
    """Interfaz específica para operaciones de escritura de usuarios."""
    
    @abstractmethod
    def guardar(self, usuario: Usuario) -> Usuario:
        pass

    @abstractmethod
    def actualizar(self, usuario: Usuario) -> Usuario:
        pass

    @abstractmethod
    def activar(self, usuario_id: int) -> Usuario:
        pass

    @abstractmethod
    def desactivar(self, usuario_id: int) -> Usuario:
        pass


class IUsuarioRepository(IUsuarioRepositoryLectura, IUsuarioRepositoryEscritura):
    """
    Interfaz completa que hereda de las interfaces segregadas.
    """
    pass