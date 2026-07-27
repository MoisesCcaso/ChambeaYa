# domain/perfil/practicante.py
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Practicante:
    """
    ESTILO THINGS/OBJECTS: El objeto encapsula estado y comportamiento.
    No es solo un contenedor de datos, tiene métodos que actúan sobre sí mismo.
    """
    id: Optional[int]
    usuario_id: int
    habilidades: List[str]
    formacion_educativa: List[str]
    carnet_universitario: str
    dni: str

    def agregar_habilidad(self, habilidad: str) -> bool:
        """
        Comportamiento: El objeto modifica su propio estado.
        """
        if habilidad not in self.habilidades:
            self.habilidades.append(habilidad)
            return True
        return False

    def eliminar_habilidad(self, habilidad: str) -> bool:
        """
        Comportamiento: El objeto modifica su propio estado.
        """
        if habilidad in self.habilidades:
            self.habilidades.remove(habilidad)
            return True
        return False

    def tiene_habilidad(self, habilidad: str) -> bool:
        """
        Comportamiento: El objeto responde preguntas sobre sí mismo.
        """
        return habilidad in self.habilidades

    def calcular_match(self, habilidades_convocatoria: List[str]) -> float:
        """
        Comportamiento: El objeto calcula algo basado en su estado.
        """
        if not self.habilidades or not habilidades_convocatoria:
            return 0.0
        interseccion = set(self.habilidades) & set(habilidades_convocatoria)
        union = set(self.habilidades) | set(habilidades_convocatoria)
        return len(interseccion) / len(union) if union else 0.0