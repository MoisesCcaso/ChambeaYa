from abc import ABC
from shared.errors import ConflictError


class EstadoConvocatoria(ABC):
    """Estado de una Convocatoria (patron State).

    Cada transicion devuelve el estado siguiente; las no permitidas lanzan ConflictError (409).
    La fecha de cierre pertenece solo al estado cerrado.
    """

    name = None
    fecha_cierre = None

    def publicar(self):
        raise ConflictError("Solo una convocatoria en borrador puede publicarse")

    def cerrar(self, fecha_cierre):
        raise ConflictError("Solo una convocatoria publicada puede cerrarse")

    def reabrir(self):
        raise ConflictError("Solo una convocatoria cerrada puede reabrirse")


class BorradorState(EstadoConvocatoria):
    name = "borrador"

    def publicar(self):
        return PublicadaState()


class PublicadaState(EstadoConvocatoria):
    name = "publicada"

    def cerrar(self, fecha_cierre):
        return CerradaState(fecha_cierre)


class CerradaState(EstadoConvocatoria):
    name = "cerrada"

    def __init__(self, fecha_cierre=None):
        self.fecha_cierre = fecha_cierre

    def reabrir(self):
        return PublicadaState()


class EstadoDesconocido(EstadoConvocatoria):
    """Estado no reconocido (o ausente): ninguna transicion es valida."""

    def __init__(self, name=None):
        self.name = name


def estado_desde_nombre(name, fecha_cierre=None):
    if name == BorradorState.name:
        return BorradorState()
    if name == PublicadaState.name:
        return PublicadaState()
    if name == CerradaState.name:
        return CerradaState(fecha_cierre)
    return EstadoDesconocido(name)