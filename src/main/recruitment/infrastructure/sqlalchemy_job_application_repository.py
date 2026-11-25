from recruitment.domain.i_job_application_repository import IJobApplicationRepository
from recruitment.domain.job_application import JobApplication
from shared.database import db
from recruitment.infrastructure.models.job_application_model import JobApplicationModel

class SqlAlchemyJobApplicationRepository(IJobApplicationRepository):
    def save(self, job_application):
        return self.save_all([job_application])[0]

    def save_all(self, job_applications):
        models = [self._upsert(job_application) for job_application in job_applications]
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
        return [self._to_job_application_domain(model) for model in models]

    def _upsert(self, job_application):
        model = None
        if job_application.id is not None:
            model = db.session.get(JobApplicationModel, job_application.id)

        if model is None:
            model = JobApplicationModel(
                job_posting_id=job_application.job_posting_id,
                intern_id=job_application.intern_id,
            )
            db.session.add(model)

        model.status = job_application.status
        return model

    def find_by_id(self, job_application_id):
        model = db.session.get(JobApplicationModel, job_application_id)
        return self._to_job_application_domain(model)

    def find_by_intern_id(self, intern_id):
        models = JobApplicationModel.query.filter_by(intern_id=intern_id).all()
        return [self._to_job_application_domain(model) for model in models]

    def find_by_job_posting_id(self, job_posting_id):
        models = JobApplicationModel.query.filter_by(job_posting_id=job_posting_id).all()
        return [self._to_job_application_domain(model) for model in models]

    def find_by_job_posting_and_intern(self, job_posting_id, intern_id):
        model = JobApplicationModel.query.filter_by(
            job_posting_id=job_posting_id,
            intern_id=intern_id,
        ).first()
        return self._to_job_application_domain(model)

    def _to_job_application_domain(self, model):
        if model is None:
            return None

        return JobApplication(
            id=model.id,
            job_posting_id=model.job_posting_id,
            intern_id=model.intern_id,
            status=model.status,
        )
