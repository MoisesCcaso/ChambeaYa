from shared.database import db
from shared.mixins import TimestampMixin


class JobPostingModel(TimestampMixin, db.Model):
    __tablename__ = "convocatorias"

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column("empresa_id", db.Integer, db.ForeignKey("empresas.id"), nullable=False)
    title = db.Column("titulo", db.String(180), nullable=False)
    description = db.Column("descripcion", db.Text, nullable=True)
    required_skills = db.Column("habilidades_requeridas", db.Text, nullable=True)
    benefits = db.Column("beneficios", db.Text, nullable=True)
    status = db.Column("estado", db.String(40), nullable=False, default="borrador")
    published_at = db.Column("fecha_publicacion", db.DateTime(timezone=True), nullable=True)
    closing_date = db.Column("fecha_cierre", db.DateTime(timezone=True), nullable=True)

    company = db.relationship("CompanyModel", back_populates="job_postings")
