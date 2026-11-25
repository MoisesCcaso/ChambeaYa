from datetime import datetime, timezone
from shared.errors import DomainError


class Deliverable:
    def __init__(self, id=None, internship_id=None, file_name=None, uploaded_at=None):
        self.id = id
        self.internship_id = internship_id
        self.file_name = file_name
        self.uploaded_at = uploaded_at

    @staticmethod
    def create(internship_id, file_name):
        if not file_name or not str(file_name).strip():
            raise DomainError("Debe adjuntarse un archivo para el entregable")

        return Deliverable(
            internship_id=internship_id,
            file_name=str(file_name).strip(),
            uploaded_at=datetime.now(timezone.utc),
        )