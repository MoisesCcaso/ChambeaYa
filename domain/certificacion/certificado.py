import hashlib
from datetime import datetime, timezone


class Certificado:
    def __init__(self, id=None, practica_id=None, codigo_qr=None,
                 documento=None, fecha_emision=None, hash_integridad=None):
        self.id = id
        self.practica_id = practica_id
        self.codigo_qr = codigo_qr
        self.documento = documento
        self.fecha_emision = fecha_emision or datetime.now(timezone.utc)
        self.hash_integridad = hash_integridad

    def generar_hash(self):
        datos = f"{self.practica_id}{self.fecha_emision}"
        self.hash_integridad = hashlib.sha256(datos.encode()).hexdigest()
        return self.hash_integridad

    def verificar_integridad(self):
        if not self.hash_integridad:
            raise ValueError("Hash de integridad no generado")

        datos = f"{self.practica_id}{self.fecha_emision}"
        return hashlib.sha256(datos.encode()).hexdigest() == self.hash_integridad
