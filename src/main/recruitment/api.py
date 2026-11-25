"""Published language of the recruitment context: what other contexts may import from it."""

from recruitment.domain.job_application import JobApplication
from recruitment.domain.job_posting import JobPosting

__all__ = ["JobApplication", "JobPosting"]
