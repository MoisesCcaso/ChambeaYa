from shared.database import db
from shared.mixins import TimestampMixin


class EmpresaModel(TimestampMixin, db.Model):
    __tablename__ = "empresas"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column("usuario_id", db.Integer, db.ForeignKey("usuarios.id"), unique=True, nullable=False)
    razon_social = db.Column(db.String(180), nullable=True)
    ruc = db.Column(db.String(20), unique=True, nullable=False)
    verificada = db.Column(db.Boolean, nullable=False, default=False)

    user = db.relationship("UserModel", back_populates="empresa")
    convocatorias = db.relationship(
        "ConvocatoriaModel",
        back_populates="empresa",
        cascade="all, delete-orphan",
    )
