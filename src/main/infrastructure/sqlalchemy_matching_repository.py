import json

from domain.matching.i_sugerencia_repository import ISugerenciaRepository
from domain.matching.sugerencia import Sugerencia
from shared.database import db
from frameworks.sqlalchemy_orm.models.sugerencia_model import SugerenciaModel


class SqlAlchemyMatchingRepository(ISugerenciaRepository):
    def save(self, sugerencia):
        model = None
        if sugerencia.id is not None:
            model = db.session.get(SugerenciaModel, sugerencia.id)

        if model is None:
            model = SugerenciaModel.query.filter_by(
                intern_id=sugerencia.intern_id,
                job_posting_id=sugerencia.job_posting_id,
            ).first()

        if model is None:
            model = SugerenciaModel(
                intern_id=sugerencia.intern_id,
                job_posting_id=sugerencia.job_posting_id,
            )
            db.session.add(model)

        model.puntaje_match = sugerencia.puntaje_match
        model.habilidades_coincidentes = self._dump_list(sugerencia.habilidades_coincidentes)

        db.session.commit()
        return self._to_domain(model)

    def find_by_intern_id(self, intern_id):
        models = SugerenciaModel.query.filter_by(intern_id=intern_id).all()
        return [self._to_domain(model) for model in models]

    def _to_domain(self, model):
        if model is None:
            return None

        return Sugerencia(
            id=model.id,
            intern_id=model.intern_id,
            job_posting_id=model.job_posting_id,
            puntaje_match=model.puntaje_match,
            habilidades_coincidentes=self._load_list(model.habilidades_coincidentes),
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
