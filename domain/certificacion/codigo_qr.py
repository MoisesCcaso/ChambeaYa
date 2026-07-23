import hashlib
import secrets


class CodigoQR:
    def __init__(self, valor=None, url_verificacion=None, hash_integridad=None):
        self.valor = valor
        self.url_verificacion = url_verificacion
        self.hash_integridad = hash_integridad

    def generar(self, certificado_id, base_url="http://localhost:5000"):
        self.valor = secrets.token_urlsafe(16)
        self.url_verificacion = f"{base_url}/certificados/verificar/{self.valor}"
        self.hash_integridad = hashlib.sha256(self.valor.encode()).hexdigest()
        return self

    def verificar(self):
        if not self.valor or not self.hash_integridad:
            return False

        return hashlib.sha256(self.valor.encode()).hexdigest() == self.hash_integridad
