from shared.database import db
from shared.mixins import TimestampMixin


class UserModel(TimestampMixin, db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column("tipo", db.String(40), nullable=False)
    status = db.Column("estado", db.String(40), nullable=False, default="pendiente")
    activation_token = db.Column(db.String(255), unique=True, nullable=True, index=True)
    activation_token_expires_at = db.Column(db.DateTime(timezone=True), nullable=True)
    password_reset_token = db.Column(db.String(255), unique=True, nullable=True, index=True)
    password_reset_expires_at = db.Column(db.DateTime(timezone=True), nullable=True)

    practicante = db.relationship(
        "PracticanteModel",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    empresa = db.relationship(
        "EmpresaModel",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
