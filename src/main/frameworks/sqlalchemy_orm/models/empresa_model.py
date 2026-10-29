from frameworks.sqlalchemy_orm.database import db
from frameworks.sqlalchemy_orm.models.mixins import TimestampMixin


class EmpresaModel(TimestampMixin, db.Model):
    __tablename__ = "empresas"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), unique=True, nullable=False)
    razon_social = db.Column(db.String(180), nullable=True)
    ruc = db.Column(db.String(20), unique=True, nullable=False)
    verificada = db.Column(db.Boolean, nullable=False, default=False)

    usuario = db.relationship("UsuarioModel", back_populates="empresa")
    convocatorias = db.relationship(
        "ConvocatoriaModel",
        back_populates="empresa",
        cascade="all, delete-orphan",
    )
