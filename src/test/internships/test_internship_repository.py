"""Integration tests for the SQLAlchemy internships repository."""

from datetime import datetime, timezone

import pytest

from internships.domain.deliverable import Deliverable
from internships.domain.evaluation import Evaluation
from internships.domain.internship import Internship
from shared.database import db
from recruitment.infrastructure.models.job_posting_model import JobPostingModel
from profiles.infrastructure.models.company_model import CompanyModel
from internships.infrastructure.models.deliverable_model import DeliverableModel
from internships.infrastructure.models.evaluation_model import EvaluationModel
from recruitment.infrastructure.models.job_application_model import JobApplicationModel
from internships.infrastructure.models.internship_model import InternshipModel
from profiles.infrastructure.models.intern_model import InternModel
from identity.infrastructure.models.user_model import UserModel
from internships.infrastructure.sqlalchemy_internship_repository import SqlAlchemyInternshipRepository


@pytest.fixture
def internship_data(app_context):
    """Persists the rows required by an internship's foreign keys."""
    intern_user = UserModel(
        email="practicante-repository@test.local",
        password_hash="hash",
        role="practicante",
        status="activo",
    )
    intern = InternModel(user=intern_user)
    company_user = UserModel(
        email="empresa-repository@test.local",
        password_hash="hash",
        role="empresa",
        status="activo",
    )
    company = CompanyModel(
        user=company_user,
        legal_name="Empresa de prueba",
        ruc="20123456789",
    )
    job_posting = JobPostingModel(
        company=company,
        title="Prácticas de desarrollo",
        status="publicada",
    )
    db.session.add_all([intern, job_posting])
    db.session.flush()

    job_application = JobApplicationModel(
        job_posting_id=job_posting.id,
        intern_id=intern.id,
        status="seleccionada",
    )
    db.session.add(job_application)
    db.session.commit()

    return {
        "postulacion_id": job_application.id,
        "practicante_id": intern.id,
    }


@pytest.fixture
def repository():
    return SqlAlchemyInternshipRepository()


def make_internship(internship_data, *, deliverables=None, evaluations=None):
    return Internship(
        job_application_id=internship_data["postulacion_id"],
        intern_id=internship_data["practicante_id"],
        deliverables=deliverables,
        evaluations=evaluations,
    )


def test_uses_in_memory_sqlite(app):
    assert app.config["SQLALCHEMY_DATABASE_URI"] == "sqlite:///:memory:"


def test_save_persists_internship_deliverable_and_evaluation(
    app_context,
    repository,
    internship_data,
):
    moment = datetime(2026, 10, 28, 15, 30, tzinfo=timezone.utc)
    internship = make_internship(
        internship_data,
        deliverables=[Deliverable(file_name="informe.pdf", uploaded_at=moment)],
        evaluations=[Evaluation(score=85, evaluated_at=moment)],
    )

    saved = repository.save(internship)
    db.session.expire_all()

    orm_model = db.session.get(InternshipModel, saved.id)
    assert orm_model is not None
    assert orm_model.job_application_id == internship_data["postulacion_id"]
    assert orm_model.intern_id == internship_data["practicante_id"]
    assert orm_model.status == Internship.STATUS_IN_PROGRESS
    assert len(orm_model.deliverables) == 1
    assert orm_model.deliverables[0].file_name == "informe.pdf"
    assert len(orm_model.evaluations) == 1
    assert orm_model.evaluations[0].score == 85

    assert saved.id is not None
    assert saved.deliverables[0].id is not None
    assert saved.deliverables[0].internship_id == saved.id
    assert saved.evaluations[0].id is not None
    assert saved.evaluations[0].internship_id == saved.id


def test_find_by_id_rebuilds_the_full_aggregate(
    app_context,
    repository,
    internship_data,
):
    internship = make_internship(internship_data)
    internship.upload_deliverable("evidencia.zip")
    internship.register_evaluation(72)
    saved = repository.save(internship)

    found = repository.find_by_id(saved.id)

    assert isinstance(found, Internship)
    assert found.id == saved.id
    assert found.job_application_id == internship_data["postulacion_id"]
    assert found.intern_id == internship_data["practicante_id"]
    assert found.status == Internship.STATUS_IN_PROGRESS
    assert [item.file_name for item in found.deliverables] == ["evidencia.zip"]
    assert [item.score for item in found.evaluations] == [72]


def test_queries_by_intern_and_job_application(
    app_context,
    repository,
    internship_data,
):
    saved = repository.save(make_internship(internship_data))

    by_intern = repository.find_by_intern_id(
        internship_data["practicante_id"]
    )
    by_application = repository.find_by_job_application_id(
        internship_data["postulacion_id"]
    )

    assert [internship.id for internship in by_intern] == [saved.id]
    assert by_application.id == saved.id


def test_missing_queries_return_empty_results(app_context, repository):
    assert repository.find_by_id(9999) is None
    assert repository.find_by_job_application_id(9999) is None
    assert repository.find_by_intern_id(9999) == []


def test_save_updates_status_and_adds_new_children_without_duplicating(
    app_context,
    repository,
    internship_data,
):
    internship = make_internship(internship_data)
    internship.upload_deliverable("primer-informe.pdf")
    internship.register_evaluation(65)
    internship = repository.save(internship)

    internship.upload_deliverable("informe-final.pdf")
    internship.register_evaluation(90)
    internship.status = Internship.STATUS_FINISHED
    updated = repository.save(internship)

    assert updated.status == Internship.STATUS_FINISHED
    assert [item.file_name for item in updated.deliverables] == [
        "primer-informe.pdf",
        "informe-final.pdf",
    ]
    assert [item.score for item in updated.evaluations] == [65, 90]
    assert InternshipModel.query.count() == 1
    assert DeliverableModel.query.count() == 2
    assert EvaluationModel.query.count() == 2


def test_save_removes_children_dropped_from_the_aggregate(
    app_context,
    repository,
    internship_data,
):
    internship = make_internship(internship_data)
    internship.upload_deliverable("informe-1.pdf")
    internship.upload_deliverable("informe-2.pdf")
    internship.register_evaluation(55)
    internship.register_evaluation(95)
    internship = repository.save(internship)

    removed_deliverable_id = internship.deliverables.pop(0).id
    removed_evaluation_id = internship.evaluations.pop(0).id
    updated = repository.save(internship)

    assert [item.file_name for item in updated.deliverables] == ["informe-2.pdf"]
    assert [item.score for item in updated.evaluations] == [95]
    assert db.session.get(DeliverableModel, removed_deliverable_id) is None
    assert db.session.get(EvaluationModel, removed_evaluation_id) is None


def test_find_by_job_application_ids_filters_and_orders_by_id(
    app_context,
    repository,
    internship_data,
):
    saved = repository.save(make_internship(internship_data))

    result = repository.find_by_job_application_ids([99999, internship_data["postulacion_id"]])
    assert [item.id for item in result] == [saved.id]

    assert repository.find_by_job_application_ids([99999]) == []
    assert repository.find_by_job_application_ids([]) == []
