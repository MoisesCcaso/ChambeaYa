from frameworks.sqlalchemy_orm.database import db
from frameworks.sqlalchemy_orm.models.mixins import TimestampMixin


class PracticanteModel(TimestampMixin, db.Model):
    __tablename__ = "practicantes"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), unique=True, nullable=False)
    nombres = db.Column(db.String(120), nullable=True)
    apellidos = db.Column(db.String(120), nullable=True)
    dni = db.Column(db.String(20), unique=True, nullable=True)
    carnet_universitario = db.Column(db.String(40), unique=True, nullable=True)
    habilidades = db.Column(db.Text, nullable=True)
    formacion_educativa = db.Column(db.Text, nullable=True)
    score_reputacion = db.Column(db.Float, nullable=False, default=0.0)
    identidad_verificada = db.Column(db.Boolean, nullable=False, default=False)

    usuario = db.relationship("UsuarioModel", back_populates="practicante")
