# domain/notificacion/i_notificacion_repository.py
from abc import ABC, abstractmethod
from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any

@dataclass
class Notificacion:
    """Entidad de notificación."""
    id: Optional[int]
    usuario_id: int
    tipo: str
    canal: str
    asunto: str
    mensaje: str
    mensaje_html: Optional[str]
    leida: bool
    fecha_envio: datetime
    fecha_lectura: Optional[datetime]
    metadata: Dict[str, Any]

    def marcar_como_leida(self) -> None:
        """Marca la notificación como leída."""
        if not self.leida:
            self.leida = True
            self.fecha_lectura = datetime.utcnow()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "usuario_id": self.usuario_id,
            "tipo": self.tipo,
            "canal": self.canal,
            "asunto": self.asunto,
            "mensaje": self.mensaje,
            "mensaje_html": self.mensaje_html,
            "leida": self.leida,
            "fecha_envio": self.fecha_envio.isoformat() if self.fecha_envio else None,
            "fecha_lectura": self.fecha_lectura.isoformat() if self.fecha_lectura else None,
            "metadata": self.metadata
        }

class INotificacionRepository(ABC):
    """Interfaz para el repositorio de notificaciones."""

    @abstractmethod
    def guardar(self, notificacion: Notificacion) -> Notificacion:
        pass

    @abstractmethod
    def obtener_por_usuario(self, usuario_id: int, limit: int = 50) -> List[Notificacion]:
        pass

    @abstractmethod
    def obtener_no_leidas(self, usuario_id: int) -> List[Notificacion]:
        pass

    @abstractmethod
    def marcar_como_leida(self, notificacion_id: int) -> Optional[Notificacion]:
        pass

    @abstractmethod
    def marcar_todas_como_leidas(self, usuario_id: int) -> int:
        pass

    @abstractmethod
    def eliminar_antiguas(self, dias: int) -> int:
        pass