from dataclasses import dataclass
from typing import Optional

UNSET = object()


@dataclass(frozen=True)
class UpdateInternDTO:
    """Parameter Object to update an intern profile (Introduce Parameter Object)."""

    first_names: Optional[str] = None
    last_names: Optional[str] = None
    dni: object = UNSET
    university_id_card: object = UNSET
    skills: object = UNSET
    education: object = UNSET

    @classmethod
    def from_dict(cls, data):
        if isinstance(data, cls):
            return data
        payload = data or {}
        return cls(
            first_names=payload.get("nombres"),
            last_names=payload.get("apellidos"),
            dni=payload["dni"] if "dni" in payload else UNSET,
            university_id_card=(
                payload["carnet_universitario"]
                if "carnet_universitario" in payload
                else UNSET
            ),
            skills=payload["habilidades"] if "habilidades" in payload else UNSET,
            education=(
                payload["formacion_educativa"]
                if "formacion_educativa" in payload
                else UNSET
            ),
        )


@dataclass(frozen=True)
class UpdateCompanyDTO:
    """Parameter Object to update a company profile (Introduce Parameter Object)."""

    legal_name: Optional[str] = None
    ruc: Optional[str] = None

    @classmethod
    def from_dict(cls, data):
        if isinstance(data, cls):
            return data
        payload = data or {}
        return cls(
            legal_name=payload.get("razon_social"),
            ruc=payload.get("ruc"),
        )
