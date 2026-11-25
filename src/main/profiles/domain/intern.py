from profiles.domain.full_name import FullName
from shared.errors import DomainError


class Intern:
    def __init__(
        self,
        id=None,
        user_id=None,
        first_names=None,
        last_names=None,
        dni=None,
        university_id_card=None,
        skills=None,
        education=None,
        reputation_score=0.0,
        identity_verified=False,
    ):
        self.id = id
        self.user_id = user_id
        self.full_name = FullName(first_names, last_names)
        self.dni = dni
        self.university_id_card = university_id_card
        self.skills = skills or []
        self.education = education or []
        self.reputation_score = reputation_score
        self.identity_verified = identity_verified

    @property
    def first_names(self):
        return self.full_name.first_names

    @property
    def last_names(self):
        return self.full_name.last_names

    def update_details(self, first_names=None, last_names=None, dni=None, university_id_card=None):
        if first_names is not None or last_names is not None:
            self.full_name = FullName(
                first_names if first_names is not None else self.first_names,
                last_names if last_names is not None else self.last_names,
            ).validate()
        if dni is not None:
            self.dni = dni
        if university_id_card is not None:
            self.university_id_card = university_id_card

        return self

    def add_skill(self, skill):
        normalized_skill = self._normalize_text(skill)
        if normalized_skill and normalized_skill not in self.skills:
            self.skills.append(normalized_skill)
        self.calculate_score()

        return self

    def add_education(self, education_entry):
        normalized_education = self._normalize_text(education_entry)
        if normalized_education and normalized_education not in self.education:
            self.education.append(normalized_education)
        self.calculate_score()

        return self

    def replace_skills(self, skills):
        if not isinstance(skills, list):
            raise DomainError("Las habilidades deben ser una lista")
        self.skills = self._normalize_items(skills)
        self.calculate_score()
        return self

    def replace_education(self, education_entries):
        if not isinstance(education_entries, list):
            raise DomainError("La formación educativa debe ser una lista")
        self.education = self._normalize_items(education_entries)
        self.calculate_score()
        return self

    def verify_identity(self):
        if not self.dni and not self.university_id_card:
            raise DomainError("Se requiere DNI o carnet universitario")
        if self.dni and (not str(self.dni).isdigit() or len(str(self.dni)) != 8):
            raise DomainError("El DNI debe contener exactamente 8 dígitos")
        if self.university_id_card and len(str(self.university_id_card).strip()) < 4:
            raise DomainError("El carnet universitario no es válido")

        self.identity_verified = True
        self.calculate_score()
        return self

    def revoke_identity_verification(self):
        self.identity_verified = False
        self.calculate_score()
        return self

    def calculate_score(self):
        base = 0.0
        base += min(len(self.skills), 10) * 5
        base += min(len(self.education), 5) * 5
        if self.identity_verified:
            base += 25

        self.reputation_score = min(base, 100.0)
        return self.reputation_score

    def _normalize_text(self, value):
        if value is None:
            return None

        return str(value).strip()

    def _normalize_items(self, values_list):
        normalized_values = []
        for value in values_list:
            normalized_value = self._normalize_text(value)
            if normalized_value and normalized_value not in normalized_values:
                normalized_values.append(normalized_value)
        return normalized_values
