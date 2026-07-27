# domain/certificacion/certificado.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
import uuid

@dataclass
class Certificado:
    """Entidad que representa un certificado digital de práctica."""
    id: Optional[int]
    practica_id: int
    codigo_unico: str
    fecha_emision: datetime
    estado: str  # emitido, revocado
    metadatos: Dict[str, Any]  # habilidades, horas, evaluacion_final
    url_verificacion: Optional[str] = None
    fecha_expiracion: Optional[datetime] = None

    def __post_init__(self):
        if self.codigo_unico is None:
            self.codigo_unico = str(uuid.uuid4()).replace('-', '')[:16].upper()
        if self.fecha_emision is None:
            self.fecha_emision = datetime.utcnow()
        if self.metadatos is None:
            self.metadatos = {}

    def revocar(self, motivo: str) -> None:
        """Revoca el certificado."""
        if self.estado == 'revocado':
            raise ValueError("El certificado ya está revocado")
        self.estado = 'revocado'
        self.metadatos['motivo_revocacion'] = motivo

    def es_valido(self) -> bool:
        """Verifica si el certificado es válido."""
        if self.estado == 'revocado':
            return False
        if self.fecha_expiracion and datetime.utcnow() > self.fecha_expiracion:
            return False
        return True

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "practica_id": self.practica_id,
            "codigo_unico": self.codigo_unico,
            "fecha_emision": self.fecha_emision.isoformat() if self.fecha_emision else None,
            "fecha_expiracion": self.fecha_expiracion.isoformat() if self.fecha_expiracion else None,
            "estado": self.estado,
            "metadatos": self.metadatos,
            "url_verificacion": self.url_verificacion
        }