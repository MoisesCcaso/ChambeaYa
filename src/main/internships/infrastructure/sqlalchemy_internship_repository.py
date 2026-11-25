from internships.domain.i_internship_repository import IInternshipRepository
from internships.domain.internship import Internship
from internships.domain.deliverable import Deliverable
from internships.domain.evaluation import Evaluation
from shared.database import db
from internships.infrastructure.models.internship_model import InternshipModel
from internships.infrastructure.models.deliverable_model import DeliverableModel
from internships.infrastructure.models.evaluation_model import EvaluationModel


class SqlAlchemyInternshipRepository(IInternshipRepository):
    def save(self, internship):
        model = None
        if internship.id is not None:
            model = db.session.get(InternshipModel, internship.id)

        if model is None:
            model = InternshipModel(
                job_application_id=internship.job_application_id,
                intern_id=internship.intern_id,
            )
            db.session.add(model)

        model.status = internship.status

        self._sync_collection(
            model.deliverables,
            internship.deliverables,
            lambda deliverable: DeliverableModel(
                file_name=deliverable.file_name,
                uploaded_at=deliverable.uploaded_at,
            ),
        )
        self._sync_collection(
            model.evaluations,
            internship.evaluations,
            lambda evaluation: EvaluationModel(
                score=evaluation.score,
                evaluated_at=evaluation.evaluated_at,
            ),
        )

        db.session.commit()
        return self._to_internship_domain(model)

    def _sync_collection(self, model_collection, domain_collection, mapper_func):
        current_ids = {
            item.id for item in domain_collection if item.id is not None
        }
        for item_model in list(model_collection):
            if item_model.id not in current_ids:
                model_collection.remove(item_model)

        existing_ids = {item_model.id for item_model in model_collection}
        for item in domain_collection:
            if item.id in existing_ids:
                continue
            model_collection.append(mapper_func(item))

    def find_by_id(self, internship_id):
        model = db.session.get(InternshipModel, internship_id)
        return self._to_internship_domain(model)

    def find_by_intern_id(self, intern_id):
        models = InternshipModel.query.filter_by(intern_id=intern_id).all()
        return [self._to_internship_domain(model) for model in models]

    def find_by_job_application_id(self, job_application_id):
        model = InternshipModel.query.filter_by(job_application_id=job_application_id).first()
        return self._to_internship_domain(model)

    def find_by_job_application_ids(self, job_application_ids):
        if not job_application_ids:
            return []
        models = (
            InternshipModel.query
            .filter(InternshipModel.job_application_id.in_(job_application_ids))
            .order_by(InternshipModel.id)
            .all()
        )
        return [self._to_internship_domain(model) for model in models]

    def _to_internship_domain(self, model):
        if model is None:
            return None

        deliverables = [
            Deliverable(id=e.id, internship_id=model.id, file_name=e.file_name, uploaded_at=e.uploaded_at)
            for e in model.deliverables
        ]
        evaluations = [
            Evaluation(id=ev.id, internship_id=model.id, score=ev.score, evaluated_at=ev.evaluated_at)
            for ev in model.evaluations
        ]

        return Internship(
            id=model.id,
            job_application_id=model.job_application_id,
            intern_id=model.intern_id,
            status=model.status,
            deliverables=deliverables,
            evaluations=evaluations,
        )
