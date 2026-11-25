from shared.database import db


class DeliverableModel(db.Model):
    __tablename__ = "entregables"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    internship_id = db.Column("practica_id", db.Integer, db.ForeignKey("practicas.id"), nullable=False)
    file_name = db.Column("archivo", db.String(255), nullable=False)
    uploaded_at = db.Column("fecha_subida", db.DateTime, nullable=False)