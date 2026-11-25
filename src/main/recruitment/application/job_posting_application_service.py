from recruitment.application.dtos import JobPostingCommand
from recruitment.domain.job_posting_factory import JobPostingFactory
from shared.error_messages import JOB_POSTING_NOT_FOUND, JOB_APPLICATION_NOT_FOUND
from shared.errors import ForbiddenError, NotFoundError

class JobPostingApplicationService:
    def __init__(self, job_posting_repository=None, job_posting_factory=None):
        self.job_posting_repository = job_posting_repository
        self.job_posting_factory = job_posting_factory or JobPostingFactory()

    def create_job_posting(self, company_id, data):
        self._require_repository()
        command = JobPostingCommand.from_dict(data)
        job_posting = self.job_posting_factory.create_job_posting(
            company_id,
            command.title,
            description=command.description,
            required_skills=command.required_skills,
            benefits=command.benefits,
        )
        return self.job_posting_repository.save(job_posting)

    def publish(self, company_id, job_posting_id):
        self._require_repository()
        job_posting = self.job_posting_repository.find_by_id(job_posting_id)
        if job_posting is None:
            raise NotFoundError(JOB_POSTING_NOT_FOUND)
        if job_posting.company_id != company_id:
            raise ForbiddenError("La convocatoria no pertenece a esta empresa")

        job_posting.publish()
        return self.job_posting_repository.save(job_posting)

    def update(self, company_id, job_posting_id, data):
        self._require_repository()
        command = JobPostingCommand.from_dict(data)
        job_posting = self._find_owned(company_id, job_posting_id)
        job_posting.update(
            title=command.title,
            description=command.description,
            required_skills=command.required_skills,
            benefits=command.benefits,
        )
        return self.job_posting_repository.save(job_posting)

    def close(self, company_id, job_posting_id):
        self._require_repository()
        job_posting = self._find_owned(company_id, job_posting_id)
        job_posting.close()
        return self.job_posting_repository.save(job_posting)

    def reopen(self, company_id, job_posting_id):
        self._require_repository()
        job_posting = self._find_owned(company_id, job_posting_id)
        job_posting.reopen()
        return self.job_posting_repository.save(job_posting)

    def duplicate(self, company_id, job_posting_id):
        self._require_repository()
        original = self._find_owned(company_id, job_posting_id)
        return self.create_job_posting(
            company_id,
            {
                "titulo": f"Copia de {original.title}",
                "descripcion": original.description,
                "habilidades_requeridas": list(original.required_skills),
                "beneficios": list(original.benefits),
            },
        )

    def delete(self, company_id, job_posting_id):
        self._require_repository()
        job_posting = self._find_owned(company_id, job_posting_id)
        job_posting.validate_deletion()
        if not self.job_posting_repository.delete(job_posting_id):
            raise NotFoundError(JOB_POSTING_NOT_FOUND)
        return job_posting

    def search(self, query=None, status=None):
        self._require_repository()
        return self.job_posting_repository.search(query=query, status=status)

    def find_by_id(self, job_posting_id):
        self._require_repository()
        job_posting = self.job_posting_repository.find_by_id(job_posting_id)
        if job_posting is None:
            raise NotFoundError(JOB_POSTING_NOT_FOUND)
        return job_posting

    def list_for_company(self, company_id):
        self._require_repository()
        return self.job_posting_repository.find_by_company_id(company_id)

    def _find_owned(self, company_id, job_posting_id):
        job_posting = self.job_posting_repository.find_by_id(job_posting_id)
        if job_posting is None:
            raise NotFoundError(JOB_POSTING_NOT_FOUND)
        if job_posting.company_id != company_id:
            raise ForbiddenError("La convocatoria no pertenece a esta empresa")
        return job_posting

    def _require_repository(self):
        if self.job_posting_repository is None:
            raise RuntimeError("JobPostingApplicationService requires a repository")
