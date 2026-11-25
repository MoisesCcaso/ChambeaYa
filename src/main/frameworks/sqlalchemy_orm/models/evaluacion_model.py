from shared.database import db


class EvaluacionModel(db.Model):
    __tablename__ = "evaluaciones"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    practica_id = db.Column(db.Integer, db.ForeignKey("practicas.id"), nullable=False)
    score = db.Column("puntaje", db.Float, nullable=False)
    fecha_evaluacion = db.Column(db.DateTime, nullable=False)