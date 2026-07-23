from frameworks.sqlalchemy_orm.database import db
from frameworks.sqlalchemy_orm.models.mixins import TimestampMixin


class SugerenciaModel(TimestampMixin, db.Model):
    __tablename__ = "sugerencias"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    practicante_id = db.Column(db.Integer, db.ForeignKey("practicantes.id"), nullable=False)
    convocatoria_id = db.Column(db.Integer, db.ForeignKey("convocatorias.id"), nullable=False)
    puntaje_match = db.Column(db.Float, nullable=False, default=0.0)
    habilidades_coincidentes = db.Column(db.Text, nullable=True)
