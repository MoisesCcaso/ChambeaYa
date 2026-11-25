import json

from recruitment.domain.i_job_posting_repository import IJobPostingRepository
from recruitment.domain.job_posting import JobPosting
from shared.database import db
from recruitment.infrastructure.models.job_posting_model import JobPostingModel


class SqlAlchemyJobPostingRepository(IJobPostingRepository):
    def save(self, job_posting):
        model = None
        if job_posting.id is not None:
            model = db.session.get(JobPostingModel, job_posting.id)

        if model is None:
            model = JobPostingModel(company_id=job_posting.company_id)
            db.session.add(model)

        model.title = job_posting.title
        model.description = job_posting.description
        model.status = job_posting.status
        model.required_skills = self._dump_list(job_posting.required_skills)
        model.benefits = self._dump_list(job_posting.benefits)
        model.published_at = job_posting.published_at
        model.closing_date = job_posting.closing_date
        db.session.commit()
        return self._to_job_posting_domain(model)

    def find_by_id(self, job_posting_id):
        model = db.session.get(JobPostingModel, job_posting_id)
        return self._to_job_posting_domain(model)


    def find_all(self):
        models = JobPostingModel.query.all()
        return [self._to_job_posting_domain(model) for model in models]

    def find_by_company_id(self, company_id):
        models = JobPostingModel.query.filter_by(company_id=company_id).all()
        return [self._to_job_posting_domain(model) for model in models]

    def delete(self, job_posting_id):
        model = db.session.get(JobPostingModel, job_posting_id)
        if model is None:
            return False
        db.session.delete(model)
        db.session.commit()
        return True

    def search(self, query=None, status=None):
        statement = JobPostingModel.query
        if status:
            statement = statement.filter_by(status=status)
        if query:
            pattern = f"%{str(query).strip()}%"
            statement = statement.filter(
                db.or_(
                    JobPostingModel.title.ilike(pattern),
                    JobPostingModel.description.ilike(pattern),
                    JobPostingModel.required_skills.ilike(pattern),
                )
            )
        models = statement.order_by(JobPostingModel.created_at.desc()).all()
        return [self._to_job_posting_domain(model) for model in models]

    def _to_job_posting_domain(self, model):
        if model is None:
            return None

        job_posting = JobPosting(
            id=model.id,
            company_id=model.company_id,
            title=model.title,
            description=model.description,
            status=model.status,
            required_skills=self._load_list(model.required_skills),
            benefits=self._load_list(model.benefits),
            published_at=model.published_at,
            closing_date=model.closing_date,
        )
        
        return job_posting
    
    def _dump_list(self, values):
        return json.dumps(values or [], ensure_ascii=False)

    def _load_list(self, value):
        if not value:
            return []

        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return []

        if not isinstance(parsed, list):
            return []

        return parsed
