from domain.convocatorias.i_postulacion_repository import IPostulacionRepository
from domain.convocatorias.postulacion import Postulacion
from shared.database import db
from frameworks.sqlalchemy_orm.models.postulacion_model import PostulacionModel

class SqlAlchemyPostulacionRepository(IPostulacionRepository):
    def save(self, postulacion):
        return self.save_all([postulacion])[0]

    def save_all(self, postulaciones):
        models = [self._upsert(postulacion) for postulacion in postulaciones]
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
        return [self._to_postulacion_domain(model) for model in models]

    def _upsert(self, postulacion):
        model = None
        if postulacion.id is not None:
            model = db.session.get(PostulacionModel, postulacion.id)

        if model is None:
            model = PostulacionModel(
                convocatoria_id=postulacion.convocatoria_id,
                practicante_id=postulacion.practicante_id,
            )
            db.session.add(model)

        model.status = postulacion.status
        return model

    def find_by_id(self, postulacion_id):
        model = db.session.get(PostulacionModel, postulacion_id)
        return self._to_postulacion_domain(model)

    def find_by_practicante_id(self, practicante_id):
        models = PostulacionModel.query.filter_by(practicante_id=practicante_id).all()
        return [self._to_postulacion_domain(model) for model in models]

    def find_by_convocatoria_id(self, convocatoria_id):
        models = PostulacionModel.query.filter_by(convocatoria_id=convocatoria_id).all()
        return [self._to_postulacion_domain(model) for model in models]

    def find_by_convocatoria_and_practicante(self, convocatoria_id, practicante_id):
        model = PostulacionModel.query.filter_by(
            convocatoria_id=convocatoria_id,
            practicante_id=practicante_id,
        ).first()
        return self._to_postulacion_domain(model)

    def _to_postulacion_domain(self, model):
        if model is None:
            return None

        return Postulacion(
            id=model.id,
            convocatoria_id=model.convocatoria_id,
            practicante_id=model.practicante_id,
            status=model.status,
        )
