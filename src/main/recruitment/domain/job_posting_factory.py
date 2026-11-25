from recruitment.domain.job_posting import JobPosting
from shared.errors import DomainError

class JobPostingFactory:
    def create_job_posting(self, company_id, title, required_skills=None, description=None, benefits=None):

        if not company_id:
            raise DomainError("La empresa es obligatoria")
        title = JobPosting.normalize_title(title)
        if required_skills is not None:
            JobPosting.validate_list(required_skills, "Las habilidades requeridas")
        if benefits is not None:
            JobPosting.validate_list(benefits, "Los beneficios")

        job_posting = JobPosting()
        job_posting.company_id = company_id
        job_posting.title = str(title).strip()
        job_posting.description = (
            str(description).strip() if description is not None else None
        )
        job_posting.status = JobPosting.STATUS_DRAFT
        for skill in required_skills or []:
            job_posting.add_required_skill(skill)
        for benefit in benefits or []:
            job_posting.add_benefit(benefit)
        return job_posting
