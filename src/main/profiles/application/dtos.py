from dataclasses import dataclass
from typing import Optional

UNSET = object()


@dataclass(frozen=True)
class ActualizarPracticanteDTO:
    """Parameter Object para actualización de perfil de practicante (Introduce Parameter Object)."""

    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    dni: object = UNSET
    carnet_universitario: object = UNSET
    habilidades: object = UNSET
    formacion_educativa: object = UNSET

    @classmethod
    def from_dict(cls, data):
        if isinstance(data, cls):
            return data
        payload = data or {}
        return cls(
            nombres=payload.get("nombres"),
            apellidos=payload.get("apellidos"),
            dni=payload["dni"] if "dni" in payload else UNSET,
            carnet_universitario=(
                payload["carnet_universitario"]
                if "carnet_universitario" in payload
                else UNSET
            ),
            habilidades=payload["habilidades"] if "habilidades" in payload else UNSET,
            formacion_educativa=(
                payload["formacion_educativa"]
                if "formacion_educativa" in payload
                else UNSET
            ),
        )


@dataclass(frozen=True)
class ActualizarEmpresaDTO:
    """Parameter Object para actualización de perfil de empresa (Introduce Parameter Object)."""

    razon_social: Optional[str] = None
    ruc: Optional[str] = None

    @classmethod
    def from_dict(cls, data):
        if isinstance(data, cls):
            return data
        payload = data or {}
        return cls(
            razon_social=payload.get("razon_social"),
            ruc=payload.get("ruc"),
        )
