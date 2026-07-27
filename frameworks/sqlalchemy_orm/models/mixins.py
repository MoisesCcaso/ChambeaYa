# frameworks/sqlalchemy_orm/models/mixins.py
from sqlalchemy import Column, DateTime
from datetime import datetime

class TimestampMixin:
    """Mixin que agrega campos de timestamp a los modelos."""
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)