from shared.database import db


class EvaluationModel(db.Model):
    __tablename__ = "evaluaciones"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    internship_id = db.Column("practica_id", db.Integer, db.ForeignKey("practicas.id"), nullable=False)
    score = db.Column("puntaje", db.Float, nullable=False)
    evaluated_at = db.Column("fecha_evaluacion", db.DateTime, nullable=False)