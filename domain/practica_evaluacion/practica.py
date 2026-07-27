# domain/practica_evaluacion/practica.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum

class EstadoPractica(str, Enum):
    EN_PROGRESO = "en_progreso"
    COMPLETADA = "completada"
    CANCELADA = "cancelada"

@dataclass
class Practica:
    """Entidad que representa una práctica preprofesional."""
    id: Optional[int]
    postulacion_id: int
    fecha_inicio: datetime
    fecha_fin: Optional[datetime] = None
    estado: EstadoPractica = EstadoPractica.EN_PROGRESO
    horario_trabajo: Optional[str] = None
    supervisor_nombre: Optional[str] = None
    supervisor_contacto: Optional[str] = None
    acta_inicio_url: Optional[str] = None
    acta_termino_url: Optional[str] = None

    def __post_init__(self):
        if self.fecha_inicio is None:
            self.fecha_inicio = datetime.utcnow()

    def finalizar(self, acta_termino_url: str) -> None:
        """Finaliza la práctica."""
        if self.estado != EstadoPractica.EN_PROGRESO:
            raise ValueError(f"No se puede finalizar una práctica en estado '{self.estado.value}'")
        self.estado = EstadoPractica.COMPLETADA
        self.fecha_fin = datetime.utcnow()
        self.acta_termino_url = acta_termino_url

    def cancelar(self) -> None:
        """Cancela la práctica."""
        if self.estado == EstadoPractica.COMPLETADA:
            raise ValueError("No se puede cancelar una práctica ya completada")
        self.estado = EstadoPractica.CANCELADA
        self.fecha_fin = datetime.utcnow()

    def esta_activa(self) -> bool:
        """Verifica si la práctica está activa."""
        return self.estado == EstadoPractica.EN_PROGRESO

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "postulacion_id": self.postulacion_id,
            "fecha_inicio": self.fecha_inicio.isoformat() if self.fecha_inicio else None,
            "fecha_fin": self.fecha_fin.isoformat() if self.fecha_fin else None,
            "estado": self.estado.value,
            "horario_trabajo": self.horario_trabajo,
            "supervisor_nombre": self.supervisor_nombre,
            "supervisor_contacto": self.supervisor_contacto,
            "acta_inicio_url": self.acta_inicio_url,
            "acta_termino_url": self.acta_termino_url
        }