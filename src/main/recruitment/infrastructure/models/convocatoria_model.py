from shared.database import db
from shared.mixins import TimestampMixin


class ConvocatoriaModel(TimestampMixin, db.Model):
    __tablename__ = "convocatorias"

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column("empresa_id", db.Integer, db.ForeignKey("empresas.id"), nullable=False)
    titulo = db.Column(db.String(180), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    habilidades_requeridas = db.Column(db.Text, nullable=True)
    beneficios = db.Column(db.Text, nullable=True)
    status = db.Column("estado", db.String(40), nullable=False, default="borrador")
    fecha_publicacion = db.Column(db.DateTime(timezone=True), nullable=True)
    fecha_cierre = db.Column(db.DateTime(timezone=True), nullable=True)

    company = db.relationship("CompanyModel", back_populates="convocatorias")
