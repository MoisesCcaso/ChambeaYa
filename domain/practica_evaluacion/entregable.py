# domain/practica_evaluacion/entregable.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum

class EstadoEntregable(str, Enum):
    PENDIENTE = "pendiente"
    ENTREGADO = "entregado"
    REVISADO = "revisado"
    APROBADO = "aprobado"
    RECHAZADO = "rechazado"

@dataclass
class Entregable:
    """Entidad que representa un entregable de práctica."""
    id: Optional[int]
    practica_id: int
    titulo: str
    descripcion: str
    fecha_limite_entrega: datetime
    fecha_entrega: Optional[datetime] = None
    archivo_url: Optional[str] = None
    estado: EstadoEntregable = EstadoEntregable.PENDIENTE
    comentario_empresa: Optional[str] = None
    fecha_evaluacion: Optional[datetime] = None

    def entregar(self, archivo_url: str) -> None:
        """Realiza la entrega del documento."""
        if self.estado not in [EstadoEntregable.PENDIENTE, EstadoEntregable.RECHAZADO]:
            raise ValueError(f"No se puede entregar un entregable en estado '{self.estado.value}'")
        if datetime.utcnow() > self.fecha_limite_entrega:
            raise ValueError("El plazo de entrega ha expirado")
        self.archivo_url = archivo_url
        self.fecha_entrega = datetime.utcnow()
        self.estado = EstadoEntregable.ENTREGADO

    def evaluar(self, puntaje: float, comentario: str = "") -> None:
        """Evalúa el entregable."""
        if self.estado != EstadoEntregable.ENTREGADO:
            raise ValueError("Solo se pueden evaluar entregables que han sido entregados")
        if not 1.0 <= puntaje <= 5.0:
            raise ValueError("El puntaje debe estar entre 1.0 y 5.0")
        self.comentario_empresa = comentario
        self.fecha_evaluacion = datetime.utcnow()
        if puntaje >= 4.0:
            self.estado = EstadoEntregable.APROBADO
        elif puntaje >= 2.5:
            self.estado = EstadoEntregable.REVISADO
        else:
            self.estado = EstadoEntregable.RECHAZADO

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "practica_id": self.practica_id,
            "titulo": self.titulo,
            "descripcion": self.descripcion,
            "fecha_limite_entrega": self.fecha_limite_entrega.isoformat() if self.fecha_limite_entrega else None,
            "fecha_entrega": self.fecha_entrega.isoformat() if self.fecha_entrega else None,
            "archivo_url": self.archivo_url,
            "estado": self.estado.value,
            "comentario_empresa": self.comentario_empresa,
            "fecha_evaluacion": self.fecha_evaluacion.isoformat() if self.fecha_evaluacion else None
        }