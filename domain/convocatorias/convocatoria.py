# domain/convocatorias/convocatoria.py
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

@dataclass
class Convocatoria:
    id: Optional[int]
    titulo: str
    descripcion: str
    empresa_id: int
    habilidades_requeridas: List[str]
    estado: str
    fecha_publicacion: datetime
    fecha_limite_postulacion: datetime
    ubicacion: Optional[str] = None
    modalidad: str = "presencial"
    num_vacantes: int = 1
    duracion_meses: int = 3
    requiere_carnet: bool = False

    def __post_init__(self):
        if self.fecha_publicacion is None:
            self.fecha_publicacion = datetime.utcnow()
        if self.habilidades_requeridas is None:
            self.habilidades_requeridas = []

    def esta_activa(self) -> bool:
        """Verifica si la convocatoria está activa."""
        return (self.estado == 'activa' and 
                self.fecha_limite_postulacion >= datetime.now().date())

    def cerrar(self) -> None:
        """Cierra la convocatoria."""
        self.estado = 'cerrada'

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "titulo": self.titulo,
            "descripcion": self.descripcion,
            "empresa_id": self.empresa_id,
            "habilidades_requeridas": self.habilidades_requeridas,
            "estado": self.estado,
            "fecha_publicacion": self.fecha_publicacion.isoformat() if self.fecha_publicacion else None,
            "fecha_limite_postulacion": self.fecha_limite_postulacion.isoformat() if self.fecha_limite_postulacion else None,
            "ubicacion": self.ubicacion,
            "modalidad": self.modalidad,
            "num_vacantes": self.num_vacantes,
            "duracion_meses": self.duracion_meses,
            "requiere_carnet": self.requiere_carnet
        }