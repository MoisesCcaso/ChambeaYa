from abc import ABC
from shared.errors import ConflictError


class JobPostingState(ABC):
    """State of a JobPosting (State pattern).

    Each transition returns the next state; forbidden ones raise ConflictError (409).
    The closing date belongs to the closed state only.
    """

    name = None
    closing_date = None

    def publish(self):
        raise ConflictError("Solo una convocatoria en borrador puede publicarse")

    def close(self, closing_date):
        raise ConflictError("Solo una convocatoria publicada puede cerrarse")

    def reopen(self):
        raise ConflictError("Solo una convocatoria cerrada puede reabrirse")


class DraftState(JobPostingState):
    name = "borrador"

    def publish(self):
        return PublishedState()


class PublishedState(JobPostingState):
    name = "publicada"

    def close(self, closing_date):
        return ClosedState(closing_date)


class ClosedState(JobPostingState):
    name = "cerrada"

    def __init__(self, closing_date=None):
        self.closing_date = closing_date

    def reopen(self):
        return PublishedState()


class UnknownState(JobPostingState):
    """Unrecognized (or missing) state: no transition is valid."""

    def __init__(self, name=None):
        self.name = name


def state_from_name(name, closing_date=None):
    if name == DraftState.name:
        return DraftState()
    if name == PublishedState.name:
        return PublishedState()
    if name == ClosedState.name:
        return ClosedState(closing_date)
    return UnknownState(name)