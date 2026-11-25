from dataclasses import dataclass
from typing import NamedTuple, Optional

from recruitment.domain.job_posting import JobPosting
from recruitment.domain.job_application import JobApplication

@dataclass(frozen=True)
class JobPostingCommand:
    """Parameter Object to create and update job postings (Introduce Parameter Object)."""

    title: Optional[str] = None
    description: Optional[str] = None
    required_skills: Optional[list] = None
    benefits: Optional[list] = None

    @classmethod
    def from_dict(cls, data):
        if isinstance(data, cls):
            return data
        payload = data or {}
        return cls(
            title=payload.get("titulo"),
            description=payload.get("descripcion"),
            required_skills=payload.get("habilidades_requeridas"),
            benefits=payload.get("beneficios"),
        )


class JobApplicationDetailDTO(NamedTuple):
    """Result of list_for_intern (Replace Array with Object)."""

    job_application: JobApplication
    job_posting: Optional[JobPosting]


class CandidateDTO(NamedTuple):
    """Result of list_for_job_posting (Replace Array with Object)."""

    job_application: JobApplication
    intern: Optional[object]
    practica: Optional[object]