from shared.errors import ConflictError
class Postulacion:
    STATUS_PENDING = "pendiente"
    ESTADO_SELECCIONADA = "seleccionada"
    ESTADO_RECHAZADA = "rechazada"
    ESTADO_CANCELADA = "cancelada"

    def __init__(self, id=None, convocatoria_id=None, practicante_id=None, status=None):
       self.id = id
       self.convocatoria_id = convocatoria_id
       self.practicante_id = practicante_id
       self.status = status or self.STATUS_PENDING

    def rechazar(self):
        if self.status != self.STATUS_PENDING:
            raise ConflictError("Solo una postulación pendiente puede rechazarse")
        self.status = self.ESTADO_RECHAZADA
        return self

    def rechazar_seleccionada(self):
        """Rechaza una selección previa cuando se selecciona otro candidato."""
        if self.status != self.ESTADO_SELECCIONADA:
            raise ConflictError(
                "Solo una postulación seleccionada puede rechazarse al elegir otro candidato"
            )
        self.status = self.ESTADO_RECHAZADA
        return self

    def seleccionar(self):
        """Selecciona la postulación si está pendiente."""
        if self.status != self.STATUS_PENDING:
            raise ConflictError("Solo una postulación pendiente puede seleccionarse")

        self.status = self.ESTADO_SELECCIONADA
        return self

    def cancelar(self):
        if self.status != self.STATUS_PENDING:
            raise ConflictError("Solo una postulación pendiente puede retirarse")
        self.status = self.ESTADO_CANCELADA
        return self

    def reactivar(self):
        if self.status != self.ESTADO_CANCELADA:
            raise ConflictError("Solo una postulación retirada puede reactivarse")
        self.status = self.STATUS_PENDING
        return self

    def reconsiderar(self):
        if self.status not in (
            self.ESTADO_SELECCIONADA,
            self.ESTADO_RECHAZADA,
        ):
            raise ConflictError(
                "Solo una postulación seleccionada o rechazada puede reconsiderarse"
            )
        self.status = self.STATUS_PENDING
        return self
