from shared.database import db
from shared.mixins import TimestampMixin


class NotificationModel(TimestampMixin, db.Model):
    # Table and column names are the existing database schema: they stay in Spanish.
    __tablename__ = "notificaciones"

    id = db.Column(db.Integer, primary_key=True)
    recipient_user_id = db.Column(
        "usuario_destino_id", db.Integer, db.ForeignKey("usuarios.id"), nullable=False, index=True
    )
    notification_type = db.Column("tipo", db.String(50), nullable=False)
    message = db.Column("mensaje", db.Text, nullable=False)
    metadata_json = db.Column("metadata", db.Text, nullable=True)
    is_read = db.Column("leida", db.Boolean, nullable=False, default=False, index=True)
