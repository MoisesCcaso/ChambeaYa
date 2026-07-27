# domain/auth/usuario.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Usuario:
    id: Optional[int]
    email: str
    password_hash: str
    nombre: str
    apellido: str
    rol: str
    activo: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()

    def es_practicante(self) -> bool:
        return self.rol == 'practicante'

    def es_empresa(self) -> bool:
        return self.rol == 'empresa'

    def es_admin(self) -> bool:
        return self.rol == 'admin'

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "email": self.email,
            "nombre": self.nombre,
            "apellido": self.apellido,
            "rol": self.rol,
            "activo": self.activo,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }