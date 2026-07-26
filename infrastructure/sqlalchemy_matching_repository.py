import json

from domain.matching.i_sugerencia_repository import ISugerenciaRepository
from domain.matching.sugerencia import Sugerencia
from frameworks.sqlalchemy_orm.database import db
from frameworks.sqlalchemy_orm.models.sugerencia_model import SugerenciaModel


class SqlAlchemyMatchingRepository(ISugerenciaRepository):
    def __init__(self):
        pass

    def save(self, sugerencia):
        model = None
        if sugerencia.id is not None:
            model = db.session.get(SugerenciaModel, sugerencia.id)

        if model is None:
            model = SugerenciaModel(
                practicante_id=sugerencia.practicante_id,
                convocatoria_id=sugerencia.convocatoria_id,
            )
            db.session.add(model)

        model.puntaje_match = sugerencia.puntaje_match
        model.habilidades_coincidentes = self._dump_list(sugerencia.habilidades_coincidentes)

        db.session.commit()
        return self._to_domain(model)

    def find_by_practicante_id(self, practicante_id):
        models = SugerenciaModel.query.filter_by(practicante_id=practicante_id).all()
        return [self._to_domain(model) for model in models]

    def _to_domain(self, model):
        if model is None:
            return None

        return Sugerencia(
            id=model.id,
            practicante_id=model.practicante_id,
            convocatoria_id=model.convocatoria_id,
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
