"""Isolated unit tests for SqlAlchemyInternshipRepository._sync_collection (Issue #181)."""

from datetime import datetime, timezone
import sys
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch

from internships.domain.deliverable import Deliverable
from internships.domain.evaluation import Evaluation
from internships.domain.internship import Internship


def _ensure_orm_stubs():
    """Provides lightweight ORM model doubles when SQLAlchemy is not installed."""
    try:
        import shared.database  # noqa: F401
        return
    except ModuleNotFoundError:
        pass

    class DummyDeliverableModel:
        def __init__(self, id=None, file_name=None, uploaded_at=None):
            self.id = id
            self.file_name = file_name
            self.uploaded_at = uploaded_at

    class DummyEvaluationModel:
        def __init__(self, id=None, score=None, evaluated_at=None):
            self.id = id
            self.score = score
            self.evaluated_at = evaluated_at

    class DummyInternshipModel:
        query = MagicMock()

        def __init__(self, id=None, job_application_id=None, intern_id=None, status=None):
            self.id = id
            self.job_application_id = job_application_id
            self.intern_id = intern_id
            self.status = status
            self.deliverables = []
            self.evaluations = []

    db_mod = ModuleType("shared.database")
    db_mod.db = SimpleNamespace(session=MagicMock())

    internship_mod = ModuleType("internships.infrastructure.models.practica_model")
    internship_mod.InternshipModel = DummyInternshipModel

    deliverable_mod = ModuleType("internships.infrastructure.models.entregable_model")
    deliverable_mod.DeliverableModel = DummyDeliverableModel

    evaluation_mod = ModuleType("internships.infrastructure.models.evaluacion_model")
    evaluation_mod.EvaluationModel = DummyEvaluationModel

    sys.modules.setdefault("internships.infrastructure.models", ModuleType("internships.infrastructure.models"))
    sys.modules["shared.database"] = db_mod
    sys.modules["internships.infrastructure.models.practica_model"] = internship_mod
    sys.modules["internships.infrastructure.models.entregable_model"] = deliverable_mod
    sys.modules["internships.infrastructure.models.evaluacion_model"] = evaluation_mod


_ensure_orm_stubs()
from internships.infrastructure.sqlalchemy_internship_repository import SqlAlchemyInternshipRepository  # noqa: E402


class TestInternshipRepositorySyncCollection(unittest.TestCase):
    """Checks the extracted _sync_collection method (Extract Method)."""

    def setUp(self):
        self.repo = SqlAlchemyInternshipRepository()

    def test_sync_collection_removes_orphans_and_adds_new_ones_without_duplicates(self):
        kept_existing = SimpleNamespace(id=1, value="conservado")
        orphan_existing = SimpleNamespace(id=2, value="eliminar")
        model_collection = [kept_existing, orphan_existing]

        domain_collection = [
            SimpleNamespace(id=1, value="conservado"),
            SimpleNamespace(id=None, value="nuevo"),
        ]

        self.repo._sync_collection(
            model_collection,
            domain_collection,
            lambda item: SimpleNamespace(id=None, value=item.value),
        )

        self.assertEqual(len(model_collection), 2)
        self.assertIs(model_collection[0], kept_existing)
        self.assertEqual(model_collection[1].value, "nuevo")

    def test_save_syncs_deliverables_and_evaluations_through_sync_collection(self):
        from shared.database import db
        from internships.infrastructure.models.deliverable_model import DeliverableModel
        from internships.infrastructure.models.evaluation_model import EvaluationModel

        moment = datetime(2026, 11, 20, 10, 0, tzinfo=timezone.utc)
        kept_deliverable = DeliverableModel(file_name="keep.pdf", uploaded_at=moment)
        kept_deliverable.id = 10
        dropped_deliverable = DeliverableModel(file_name="drop.pdf", uploaded_at=moment)
        dropped_deliverable.id = 11

        eval_keep = EvaluationModel(score=80, evaluated_at=moment)
        eval_keep.id = 20
        eval_drop = EvaluationModel(score=50, evaluated_at=moment)
        eval_drop.id = 21

        model = SimpleNamespace(
            id=5,
            job_application_id=1,
            intern_id=2,
            status=Internship.STATUS_IN_PROGRESS,
            deliverables=[kept_deliverable, dropped_deliverable],
            evaluations=[eval_keep, eval_drop],
        )

        internship = Internship(
            id=5,
            job_application_id=1,
            intern_id=2,
            status=Internship.STATUS_FINISHED,
            deliverables=[
                Deliverable(id=10, internship_id=5, file_name="keep.pdf", uploaded_at=moment),
                Deliverable(id=None, internship_id=5, file_name="new.pdf", uploaded_at=moment),
            ],
            evaluations=[
                Evaluation(id=20, internship_id=5, score=80, evaluated_at=moment),
                Evaluation(id=None, internship_id=5, score=95, evaluated_at=moment),
            ],
        )

        with (
            patch.object(db.session, "get", return_value=model),
            patch.object(db.session, "commit"),
        ):
            result = self.repo.save(internship)

        self.assertEqual([e.file_name for e in model.deliverables], ["keep.pdf", "new.pdf"])
        self.assertEqual([ev.score for ev in model.evaluations], [80, 95])
        self.assertEqual(result.status, Internship.STATUS_FINISHED)


if __name__ == "__main__":
    unittest.main()
