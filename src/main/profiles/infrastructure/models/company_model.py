from shared.database import db
from shared.mixins import TimestampMixin


class CompanyModel(TimestampMixin, db.Model):
    __tablename__ = "empresas"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column("usuario_id", db.Integer, db.ForeignKey("usuarios.id"), unique=True, nullable=False)
    legal_name = db.Column("razon_social", db.String(180), nullable=True)
    ruc = db.Column(db.String(20), unique=True, nullable=False)
    verified = db.Column("verificada", db.Boolean, nullable=False, default=False)

    user = db.relationship("UserModel", back_populates="company")
    convocatorias = db.relationship(
        "ConvocatoriaModel",
        back_populates="company",
        cascade="all, delete-orphan",
    )
