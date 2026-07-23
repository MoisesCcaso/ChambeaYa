import hashlib


class ArchivoPDF:
    def __init__(self, url=None, hash_integridad=None):
        self.url = url
        self.hash_integridad = hash_integridad

    def verificar_integridad(self, contenido_bytes):
        actual = hashlib.sha256(contenido_bytes).hexdigest()
        return actual == self.hash_integridad
