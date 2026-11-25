from shared.errors import DomainError
class FullName:
    def __init__(self, first_names=None, last_names=None):
        self.first_names = first_names
        self.last_names = last_names

    def validate(self):
        first_names = str(self.first_names or "").strip()
        last_names = str(self.last_names or "").strip()
        if not first_names or not last_names:
            raise DomainError("Nombres y apellidos son obligatorios")
        self.first_names = first_names
        self.last_names = last_names
        return self

    def __str__(self):
        return f"{self.first_names} {self.last_names}".strip()
