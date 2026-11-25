from shared.database import db
from shared.mixins import TimestampMixin


class CertificateModel(TimestampMixin, db.Model):
    __tablename__ = "certificados"

    id = db.Column(db.Integer, primary_key=True)
    internship_id = db.Column(
        "practica_id", db.Integer,
        db.ForeignKey("practicas.id"),
        unique=True,
        nullable=False,
    )
    qr_code_value = db.Column("codigo_qr_valor", db.String(80), unique=True, nullable=True)
    qr_code_verification_url = db.Column("codigo_qr_url_verificacion", db.String(255), nullable=True)
    qr_code_hash = db.Column("codigo_qr_hash", db.String(64), nullable=True)
    document_url = db.Column("documento_url", db.String(255), nullable=True)
    document_hash = db.Column("documento_hash", db.String(64), nullable=True)
    document_content = db.Column("documento_contenido", db.Text, nullable=True)
