import json

from matching.domain.i_suggestion_repository import ISuggestionRepository
from matching.domain.suggestion import Suggestion
from shared.database import db
from matching.infrastructure.models.suggestion_model import SuggestionModel


class SqlAlchemyMatchingRepository(ISuggestionRepository):
    def save(self, suggestion):
        model = None
        if suggestion.id is not None:
            model = db.session.get(SuggestionModel, suggestion.id)

        if model is None:
            model = SuggestionModel.query.filter_by(
                intern_id=suggestion.intern_id,
                job_posting_id=suggestion.job_posting_id,
            ).first()

        if model is None:
            model = SuggestionModel(
                intern_id=suggestion.intern_id,
                job_posting_id=suggestion.job_posting_id,
            )
            db.session.add(model)

        model.match_score = suggestion.match_score
        model.matched_skills = self._dump_list(suggestion.matched_skills)

        db.session.commit()
        return self._to_domain(model)

    def find_by_intern_id(self, intern_id):
        models = SuggestionModel.query.filter_by(intern_id=intern_id).all()
        return [self._to_domain(model) for model in models]

    def _to_domain(self, model):
        if model is None:
            return None

        return Suggestion(
            id=model.id,
            intern_id=model.intern_id,
            job_posting_id=model.job_posting_id,
            match_score=model.match_score,
            matched_skills=self._load_list(model.matched_skills),
        )

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
