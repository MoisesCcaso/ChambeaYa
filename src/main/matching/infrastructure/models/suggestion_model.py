from shared.database import db
from shared.mixins import TimestampMixin


class SuggestionModel(TimestampMixin, db.Model):
    __tablename__ = "sugerencias"
    __table_args__ = (
        db.UniqueConstraint(
            "practicante_id",
            "convocatoria_id",
            name="uq_sugerencia_practicante_convocatoria",
        ),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    intern_id = db.Column("practicante_id", db.Integer, db.ForeignKey("practicantes.id"), nullable=False)
    job_posting_id = db.Column("convocatoria_id", db.Integer, db.ForeignKey("convocatorias.id"), nullable=False)
    match_score = db.Column("puntaje_match", db.Float, nullable=False, default=0.0)
    matched_skills = db.Column("habilidades_coincidentes", db.Text, nullable=True)
