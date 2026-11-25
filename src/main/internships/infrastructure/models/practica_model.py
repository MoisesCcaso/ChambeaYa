from shared.database import db


class PracticaModel(db.Model):
    __tablename__ = "practicas"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    job_application_id = db.Column(
        "postulacion_id", db.Integer,
        db.ForeignKey("postulaciones.id"),
        unique=True,
        nullable=False,
    )
    intern_id = db.Column("practicante_id", db.Integer, db.ForeignKey("practicantes.id"), nullable=False)
    status = db.Column("estado", db.String(20), nullable=False, default="EN_CURSO")

    entregables = db.relationship(
        "EntregableModel", backref="practica", cascade="all, delete-orphan", lazy="select"
    )
    evaluaciones = db.relationship(
        "EvaluacionModel", backref="practica", cascade="all, delete-orphan", lazy="select"
    )
