from shared.database import db
from shared.mixins import TimestampMixin


class InternModel(TimestampMixin, db.Model):
    __tablename__ = "practicantes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column("usuario_id", db.Integer, db.ForeignKey("usuarios.id"), unique=True, nullable=False)
    first_names = db.Column("nombres", db.String(120), nullable=True)
    last_names = db.Column("apellidos", db.String(120), nullable=True)
    dni = db.Column(db.String(20), unique=True, nullable=True)
    university_id_card = db.Column("carnet_universitario", db.String(40), unique=True, nullable=True)
    skills = db.Column("habilidades", db.Text, nullable=True)
    education = db.Column("formacion_educativa", db.Text, nullable=True)
    reputation_score = db.Column("score_reputacion", db.Float, nullable=False, default=0.0)
    identity_verified = db.Column("identidad_verificada", db.Boolean, nullable=False, default=False)

    user = db.relationship("UserModel", back_populates="intern")
