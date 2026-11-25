from shared.database import db
from shared.mixins import TimestampMixin


class PostulacionModel(TimestampMixin, db.Model):
    __tablename__ = "postulaciones"
    __table_args__ = (
        db.UniqueConstraint(
            "convocatoria_id",
            "practicante_id",
            name="uq_postulacion_convocatoria_practicante",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    convocatoria_id = db.Column(db.Integer, db.ForeignKey("convocatorias.id"), nullable=False)
    intern_id = db.Column("practicante_id", db.Integer, db.ForeignKey("practicantes.id"), nullable=False)
    status = db.Column("estado", db.String(40), nullable=False, default="pendiente")
