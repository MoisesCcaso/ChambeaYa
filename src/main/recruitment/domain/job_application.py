from shared.errors import ConflictError
class JobApplication:
    STATUS_PENDING = "pendiente"
    STATUS_SELECTED = "seleccionada"
    STATUS_REJECTED = "rechazada"
    STATUS_CANCELLED = "cancelada"

    def __init__(self, id=None, job_posting_id=None, intern_id=None, status=None):
       self.id = id
       self.job_posting_id = job_posting_id
       self.intern_id = intern_id
       self.status = status or self.STATUS_PENDING

    def reject(self):
        if self.status != self.STATUS_PENDING:
            raise ConflictError("Solo una postulación pendiente puede rechazarse")
        self.status = self.STATUS_REJECTED
        return self

    def reject_selected(self):
        """Rejects a previous selection when another candidate is selected."""
        if self.status != self.STATUS_SELECTED:
            raise ConflictError(
                "Solo una postulación seleccionada puede rechazarse al elegir otro candidato"
            )
        self.status = self.STATUS_REJECTED
        return self

    def select(self):
        """Selects the job application if it is pending."""
        if self.status != self.STATUS_PENDING:
            raise ConflictError("Solo una postulación pendiente puede seleccionarse")

        self.status = self.STATUS_SELECTED
        return self

    def cancel(self):
        if self.status != self.STATUS_PENDING:
            raise ConflictError("Solo una postulación pendiente puede retirarse")
        self.status = self.STATUS_CANCELLED
        return self

    def reactivate(self):
        if self.status != self.STATUS_CANCELLED:
            raise ConflictError("Solo una postulación retirada puede reactivarse")
        self.status = self.STATUS_PENDING
        return self

    def reconsider(self):
        if self.status not in (
            self.STATUS_SELECTED,
            self.STATUS_REJECTED,
        ):
            raise ConflictError(
                "Solo una postulación seleccionada o rechazada puede reconsiderarse"
            )
        self.status = self.STATUS_PENDING
        return self
