from abc import ABC
from shared.errors import ConflictError


class EstadoConvocatoria(ABC):
    """Estado de una Convocatoria (patron State).

    Cada transicion devuelve el estado siguiente; las no permitidas lanzan ConflictError (409).
    La fecha de cierre pertenece solo al estado cerrado.
    """

    nombre = None
    fecha_cierre = None

    def publicar(self):
        raise ConflictError("Solo una convocatoria en borrador puede publicarse")

    def cerrar(self, fecha_cierre):
        raise ConflictError("Solo una convocatoria publicada puede cerrarse")

    def reabrir(self):
        raise ConflictError("Solo una convocatoria cerrada puede reabrirse")


class BorradorState(EstadoConvocatoria):
    nombre = "borrador"

    def publicar(self):
        return PublicadaState()


class PublicadaState(EstadoConvocatoria):
    nombre = "publicada"

    def cerrar(self, fecha_cierre):
        return CerradaState(fecha_cierre)


class CerradaState(EstadoConvocatoria):
    nombre = "cerrada"

    def __init__(self, fecha_cierre=None):
        self.fecha_cierre = fecha_cierre

    def reabrir(self):
        return PublicadaState()


class EstadoDesconocido(EstadoConvocatoria):
    """Estado no reconocido (o ausente): ninguna transicion es valida."""

    def __init__(self, nombre=None):
        self.nombre = nombre


def estado_desde_nombre(nombre, fecha_cierre=None):
    if nombre == BorradorState.nombre:
        return BorradorState()
    if nombre == PublicadaState.nombre:
        return PublicadaState()
    if nombre == CerradaState.nombre:
        return CerradaState(fecha_cierre)
    return EstadoDesconocido(nombre)