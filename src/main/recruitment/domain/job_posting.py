from datetime import datetime, timezone
from recruitment.domain.job_posting_state import state_from_name
from shared.errors import ConflictError, DomainError


class JobPosting:
    STATUS_DRAFT = "borrador"
    STATUS_PUBLISHED = "publicada"
    STATUS_CLOSED = "cerrada"

    def __init__(
        self,
        id=None,
        company_id=None,
        title=None,
        description=None,
        status=None,
        required_skills=None,
        benefits=None,
        published_at=None,
        closing_date=None,
    ):
        self.id = id
        self.company_id = company_id
        self.title = title
        self.description = description
        self._state = state_from_name(status, closing_date)
        self.required_skills = required_skills or []
        self.benefits = benefits or []
        self.published_at = published_at

    @property
    def status(self):
        return self._state.name

    @status.setter
    def status(self, name):
        self._state = state_from_name(name)

    @property
    def closing_date(self):
        """Only has a value while the job posting is closed."""
        return self._state.closing_date

    def publish(self):
        """Publishes the job posting if it is a draft."""
        self._state = self._state.publish()
        self.published_at = datetime.now(timezone.utc)
        return self

    def close(self):
        self._state = self._state.close(datetime.now(timezone.utc))
        return self

    def reopen(self):
        self._state = self._state.reopen()
        self.published_at = datetime.now(timezone.utc)
        return self

    def validate_deletion(self):
        if self.status != self.STATUS_DRAFT:
            raise ConflictError("Solo una convocatoria en borrador puede eliminarse")
        return self

    def update(
        self,
        title=None,
        description=None,
        required_skills=None,
        benefits=None,
    ):
        if self.status != self.STATUS_DRAFT:
            raise ConflictError("Solo una convocatoria en borrador puede editarse")
        if title is not None:
            self.title = self.normalize_title(title)
        if description is not None:
            self.description = str(description).strip()
        if required_skills is not None:
            self.validate_list(required_skills, "Las habilidades requeridas")
            self.required_skills = []
            for skill in required_skills:
                self.add_required_skill(skill)
        if benefits is not None:
            self.validate_list(benefits, "Los beneficios")
            self.benefits = []
            for benefit in benefits:
                self.add_benefit(benefit)
        return self

    @staticmethod
    def normalize_title(title):
        normalized_title = str(title).strip() if title is not None else ""
        if not normalized_title:
            raise DomainError("El título es obligatorio")
        return normalized_title

    @staticmethod
    def validate_list(values_list, name):
        if not isinstance(values_list, list):
            raise DomainError(f"{name} deben ser una lista")
        return values_list

    def add_required_skill(self, skill):
        normalized_skill = self._normalize_text(skill)
        if normalized_skill and normalized_skill not in self.required_skills:
            self.required_skills.append(normalized_skill)
        return self
    
    def add_benefit(self, benefit):
        normalized_benefit = self._normalize_text(benefit)
        if normalized_benefit and normalized_benefit not in self.benefits:
            self.benefits.append(normalized_benefit)
        return self
    
    def _normalize_text(self, value):
        if value is None:
            return None
        return str(value).strip()
