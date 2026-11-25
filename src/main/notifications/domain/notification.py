class Notification:
    # Values are persisted and read by the frontend: they stay in Spanish.
    TYPE_JOB_APPLICATION_SELECTED = "POSTULACION_SELECCIONADA"
    TYPE_EVALUATION_AVAILABLE = "EVALUACION_DISPONIBLE"
    TYPE_CERTIFICATE_ISSUED = "CERTIFICADO_EMITIDO"
    TYPE_NEW_SUGGESTIONS = "NUEVAS_SUGERENCIAS"

    def __init__(self, id=None, recipient_user_id=None, notification_type=None, message=None,
                 metadata=None, is_read=False, created_at=None):
        self.id = id
        self.recipient_user_id = recipient_user_id
        self.notification_type = notification_type
        self.message = message
        self.metadata = metadata or {}
        self.is_read = is_read
        self.created_at = created_at

    def mark_as_read(self):
        self.is_read = True
