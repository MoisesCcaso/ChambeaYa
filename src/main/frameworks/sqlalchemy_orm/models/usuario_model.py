from frameworks.sqlalchemy_orm.database import db
from frameworks.sqlalchemy_orm.models.mixins import TimestampMixin


class UsuarioModel(TimestampMixin, db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    tipo = db.Column(db.String(40), nullable=False)
    estado = db.Column(db.String(40), nullable=False, default="pendiente")
    activation_token = db.Column(db.String(255), unique=True, nullable=True, index=True)
    activation_token_expires_at = db.Column(db.DateTime(timezone=True), nullable=True)
    password_reset_token = db.Column(db.String(255), unique=True, nullable=True, index=True)
    password_reset_expires_at = db.Column(db.DateTime(timezone=True), nullable=True)

    practicante = db.relationship(
        "PracticanteModel",
        back_populates="usuario",
        uselist=False,
        cascade="all, delete-orphan",
    )
    empresa = db.relationship(
        "EmpresaModel",
        back_populates="usuario",
        uselist=False,
        cascade="all, delete-orphan",
    )
