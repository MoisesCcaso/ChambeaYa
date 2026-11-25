"""I-12 - Matching repository tests with in-memory SQLite, no doubles."""

import unittest

from matching.domain.suggestion import Suggestion
from bootstrap.app import create_app
from shared.database import db
from recruitment.infrastructure.models.job_posting_model import JobPostingModel
from profiles.infrastructure.models.company_model import CompanyModel
from profiles.infrastructure.models.intern_model import InternModel
from matching.infrastructure.models.suggestion_model import SuggestionModel
from identity.infrastructure.models.user_model import UserModel
from matching.infrastructure.sqlalchemy_matching_repository import SqlAlchemyMatchingRepository


class TestMatchingRepository(unittest.TestCase):
    """Checks save, read and update using the real ORM models."""

    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.repository = SqlAlchemyMatchingRepository()
        self.intern_id, self.job_posting_id = self._create_related_entities()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def _create_related_entities(self):
        intern_user = UserModel(
            email="practicante_matching@test.com",
            password_hash="hash_test",
            role="practicante",
            status="activo",
        )
        company_user = UserModel(
            email="empresa_matching@test.com",
            password_hash="hash_test",
            role="empresa",
            status="activo",
        )
        db.session.add_all([intern_user, company_user])
        db.session.flush()

        intern = InternModel(
            user_id=intern_user.id,
            first_names="Ana",
            last_names="Pérez",
            dni="71112233",
        )
        company = CompanyModel(
            user_id=company_user.id,
            legal_name="Empresa Matching",
            ruc="20111222333",
            verified=True,
        )
        db.session.add_all([intern, company])
        db.session.flush()

        job_posting = JobPostingModel(
            company_id=company.id,
            title="Prácticas de desarrollo",
            status="publicada",
        )
        db.session.add(job_posting)
        db.session.commit()
        return intern.id, job_posting.id

    def _create_suggestion(self, score=75.0, skills=None, suggestion_id=None):
        return Suggestion(
            id=suggestion_id,
            intern_id=self.intern_id,
            job_posting_id=self.job_posting_id,
            match_score=score,
            matched_skills=skills or ["python", "sql"],
        )

    def test_save_stores_suggestion_and_assigns_id(self):
        saved = self.repository.save(self._create_suggestion())

        self.assertIsNotNone(saved.id)
        self.assertEqual(self.intern_id, saved.intern_id)
        self.assertEqual(self.job_posting_id, saved.job_posting_id)
        self.assertEqual(75.0, saved.match_score)
        self.assertEqual({"python", "sql"}, set(saved.matched_skills))
        self.assertEqual(1, SuggestionModel.query.count())

    def test_find_by_intern_id_returns_their_suggestions(self):
        saved = self.repository.save(self._create_suggestion())

        found = self.repository.find_by_intern_id(self.intern_id)

        self.assertEqual(1, len(found))
        self.assertEqual(saved.id, found[0].id)
        self.assertEqual(75.0, found[0].match_score)
        self.assertEqual({"python", "sql"}, set(found[0].matched_skills))
        self.assertEqual([], self.repository.find_by_intern_id(99999))

    def test_save_updates_existing_suggestion(self):
        saved = self.repository.save(self._create_suggestion())
        updated = self.repository.save(
            self._create_suggestion(
                score=100.0,
                skills=["python", "sql", "git"],
                suggestion_id=saved.id,
            )
        )

        self.assertEqual(saved.id, updated.id)
        self.assertEqual(100.0, updated.match_score)
        self.assertEqual({"python", "sql", "git"}, set(updated.matched_skills))
        self.assertEqual(1, SuggestionModel.query.count())

        reloaded = self.repository.find_by_intern_id(self.intern_id)[0]
        self.assertEqual(100.0, reloaded.match_score)
        self.assertEqual({"python", "sql", "git"}, set(reloaded.matched_skills))

    def test_save_same_intern_posting_pair_does_not_duplicate(self):
        first_result = self.repository.save(self._create_suggestion())
        second_result = self.repository.save(
            self._create_suggestion(score=50.0, skills=["python"])
        )

        self.assertEqual(first_result.id, second_result.id)
        self.assertEqual(50.0, second_result.match_score)
        self.assertEqual(["python"], second_result.matched_skills)
        self.assertEqual(1, SuggestionModel.query.count())


if __name__ == "__main__":
    unittest.main()
