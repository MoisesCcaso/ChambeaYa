# domain/perfil/empresa.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class Empresa:
    id: Optional[int]
    usuario_id: int
    razon_social: str
    ruc: str
    descripcion: Optional[str] = None
    ubicacion: Optional[str] = None