#!/usr/bin/python
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from typing import NamedTuple, Optional

from domain.convocatorias.convocatoria import Convocatoria
from domain.convocatorias.postulacion import Postulacion

UNSET = object()


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

class PostulacionDetalleDTO(NamedTuple):
    """Resultado de list_for_practicante (Replace Array with Object)."""

    postulacion: Postulacion
    convocatoria: Optional[Convocatoria]


class CandidatoConvocatoriaDTO(NamedTuple):
    """Resultado de list_for_convocatoria (Replace Array with Object)."""

    postulacion: Postulacion
    practicante: Optional[object]
    practica: Optional[object]