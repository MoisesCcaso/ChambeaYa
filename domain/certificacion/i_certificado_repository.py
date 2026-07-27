# domain/certificacion/i_certificado_repository.py
from abc import ABC, abstractmethod
from typing import List, Optional
from .certificado import Certificado
from .reputacion import Reputacion

class ICertificadoRepository(ABC):
    """Interfaz para el repositorio de certificados."""

    @abstractmethod
    def guardar(self, certificado: Certificado) -> Certificado:
        pass

    @abstractmethod
    def obtener_por_id(self, certificado_id: int) -> Optional[Certificado]:
        pass

    @abstractmethod
    def obtener_por_codigo(self, codigo_unico: str) -> Optional[Certificado]:
        pass

    @abstractmethod
    def obtener_por_practica(self, practica_id: int) -> Optional[Certificado]:
        pass

    @abstractmethod
    def obtener_por_practicante(self, practicante_id: int) -> List[Certificado]:
        pass

    @abstractmethod
    def actualizar(self, certificado: Certificado) -> Certificado:
        pass

class IReputacionRepository(ABC):
    """Interfaz para el repositorio de reputación."""

    @abstractmethod
    def guardar(self, reputacion: Reputacion) -> Reputacion:
        pass

    @abstractmethod
    def obtener_por_usuario(self, usuario_id: int) -> Optional[Reputacion]:
        pass

    @abstractmethod
    def actualizar(self, reputacion: Reputacion) -> Reputacion:
        pass

    @abstractmethod
    def obtener_top_practicantes(self, limit: int = 10) -> List[Reputacion]:
        pass