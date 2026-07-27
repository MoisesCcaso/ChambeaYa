# domain/convocatorias/postulacion.py
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

@dataclass
class Postulacion:
    """Entidad que representa una postulación a una convocatoria."""
    id: Optional[int]
    convocatoria_id: int
    practicante_id: int
    fecha_postulacion: datetime
    estado: str  # pendiente, aceptada, rechazada, completada
    mensaje_postulacion: Optional[str] = None
    archivos_adjuntos: List[str] = None

    def __post_init__(self):
        if self.archivos_adjuntos is None:
            self.archivos_adjuntos = []
        if self.fecha_postulacion is None:
            self.fecha_postulacion = datetime.utcnow()

    def aceptar(self) -> None:
        """Cambia el estado a aceptada."""
        if self.estado != 'pendiente':
            raise ValueError(f"No se puede aceptar una postulación en estado '{self.estado}'")
        self.estado = 'aceptada'

    def rechazar(self) -> None:
        """Cambia el estado a rechazada."""
        if self.estado != 'pendiente':
            raise ValueError(f"No se puede rechazar una postulación en estado '{self.estado}'")
        self.estado = 'rechazada'

    def completar(self) -> None:
        """Cambia el estado a completada."""
        if self.estado != 'aceptada':
            raise ValueError(f"No se puede completar una postulación en estado '{self.estado}'")
        self.estado = 'completada'

    def esta_activa(self) -> bool:
        """Verifica si la postulación está activa (pendiente o aceptada)."""
        return self.estado in ['pendiente', 'aceptada']

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "convocatoria_id": self.convocatoria_id,
            "practicante_id": self.practicante_id,
            "fecha_postulacion": self.fecha_postulacion.isoformat() if self.fecha_postulacion else None,
            "estado": self.estado,
            "mensaje_postulacion": self.mensaje_postulacion,
            "archivos_adjuntos": self.archivos_adjuntos
        }