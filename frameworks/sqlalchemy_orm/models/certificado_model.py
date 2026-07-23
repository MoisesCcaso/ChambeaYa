from frameworks.sqlalchemy_orm.database import db


class CertificadoModel(db.Model):
    __tablename__ = "certificados"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    practica_id = db.Column(db.Integer, db.ForeignKey("practicas.id"), nullable=False)
    qr_valor = db.Column(db.String(64), unique=True, nullable=False)
    qr_url = db.Column(db.String(256), nullable=False)
    hash_integridad = db.Column(db.String(128), nullable=False)
    fecha_emision = db.Column(db.DateTime(timezone=True), nullable=False)
