from frameworks.sqlalchemy_orm.database import db
from frameworks.sqlalchemy_orm.models.mixins import TimestampMixin


class PostulacionModel(TimestampMixin, db.Model):
    __tablename__ = "postulaciones"

    id = db.Column(db.Integer, primary_key=True)
    convocatoria_id = db.Column(db.Integer, db.ForeignKey("convocatorias.id"), nullable=False)
    practicante_id = db.Column(db.Integer, db.ForeignKey("practicantes.id"), nullable=False)
    estado = db.Column(db.String(40), nullable=False, default="pendiente")