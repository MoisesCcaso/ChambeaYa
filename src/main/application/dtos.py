from dataclasses import dataclass
from typing import NamedTuple, Optional

from domain.convocatorias.convocatoria import Convocatoria
from domain.convocatorias.postulacion import Postulacion

@dataclass(frozen=True)
class ConvocatoriaCommand:
    """Parameter Object para creación y actualización de convocatorias (Introduce Parameter Object)."""

    titulo: Optional[str] = None
    descripcion: Optional[str] = None
    habilidades_requeridas: Optional[list] = None
    beneficios: Optional[list] = None

    @classmethod
    def from_dict(cls, data):
        if isinstance(data, cls):
            return data
        payload = data or {}
        return cls(
            titulo=payload.get("titulo"),
            descripcion=payload.get("descripcion"),
            habilidades_requeridas=payload.get("habilidades_requeridas"),
            beneficios=payload.get("beneficios"),
        )


class PostulacionDetalleDTO(NamedTuple):
    """Resultado de list_for_practicante (Replace Array with Object)."""

    postulacion: Postulacion
    convocatoria: Optional[Convocatoria]


class CandidatoConvocatoriaDTO(NamedTuple):
    """Resultado de list_for_convocatoria (Replace Array with Object)."""

    postulacion: Postulacion
    intern: Optional[object]
    practica: Optional[object]