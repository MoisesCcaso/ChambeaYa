# domain/perfil/empresa.py
# LAB 12 - SOLID: L (Sustitución de Liskov)
# Esta subclase puede sustituir a la clase padre sin alterar el comportamiento esperado.

from dataclasses import dataclass
from typing import Optional
from domain.perfil.usuario_base import UsuarioBase  # Suponiendo una clase padre


@dataclass
class Empresa(UsuarioBase):
    """
    Subclase que cumple con LSP: puede sustituir a UsuarioBase sin problemas.
    """
    razon_social: str
    ruc: str
    descripcion: Optional[str] = None
    ubicacion: Optional[str] = None

    def obtener_rol(self) -> str:
        """Sobrescribe el método de la clase padre."""
        return "empresa"

    def esta_verificado(self) -> bool:
        """Implementa un comportamiento específico pero consistente con la interfaz."""
        return bool(self.ruc) and len(self.ruc) == 11

    def obtener_identificador(self) -> str:
        """Retorna el identificador de la empresa (ruc)."""
        return self.ruc