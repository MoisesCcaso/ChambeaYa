import hashlib
from uuid import uuid4
class CodigoQR:
    def __init__(self, value=None, url_verificacion=None, hash_integridad=None):
         self.value = value
         self.url_verificacion = url_verificacion
         self.hash_integridad = hash_integridad

    @staticmethod
    def generar(internship_id, url_verificacion=None):
        value = f"CERT-{internship_id}-{uuid4().hex[:8]}"
        hash_integridad = hashlib.sha256(value.encode()).hexdigest()
        return CodigoQR(value=value, url_verificacion=url_verificacion, hash_integridad=hash_integridad)

    def verificar(self, valor_a_verificar):
        if not self.value or not self.hash_integridad:
            return False
        hash_calculado = hashlib.sha256(self.value.encode()).hexdigest()
        return self.value == valor_a_verificar and hash_calculado == self.hash_integridad
