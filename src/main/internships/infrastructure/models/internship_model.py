from shared.database import db


class InternshipModel(db.Model):
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

    deliverables = db.relationship(
        "DeliverableModel", backref="practica", cascade="all, delete-orphan", lazy="select"
    )
    evaluations = db.relationship(
        "EvaluationModel", backref="practica", cascade="all, delete-orphan", lazy="select"
    )
