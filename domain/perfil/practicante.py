# domain/perfil/practicante.py
# LAB 12 - SOLID: L (Sustitución de Liskov)
# Esta subclase puede sustituir a la clase padre sin alterar el comportamiento esperado.

from dataclasses import dataclass
from typing import Optional, List
from domain.perfil.usuario_base import UsuarioBase  # Suponiendo una clase padre


@dataclass
class Practicante(UsuarioBase):
    """
    Subclase que cumple con LSP: puede sustituir a UsuarioBase sin problemas.
    """
    habilidades: List[str]
    formacion_educativa: List[str]
    carnet_universitario: str
    dni: str

    def obtener_rol(self) -> str:
        """Sobrescribe el método de la clase padre."""
        return "practicante"

    def esta_verificado(self) -> bool:
        """Implementa un comportamiento específico pero consistente con la interfaz."""
        return bool(self.dni) and bool(self.carnet_universitario)

    def obtener_identificador(self) -> str:
        """Retorna el identificador del usuario (dni)."""
        return self.dni