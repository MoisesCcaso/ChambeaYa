import hashlib
from shared.errors import DomainError
class ArchivoPDF:
    def __init__(self, url=None, hash_integridad=None, contenido=None):
        self.url = url
        self.hash_integridad = hash_integridad
        self.contenido = contenido

    @staticmethod
    def create(internship_id, contenido, url=None):
        if not contenido:
            raise DomainError("Debe proveerse el contenido del PDF para generar el archivo")

        contenido_bytes = contenido.encode() if isinstance(contenido, str) else contenido
        hash_integridad = hashlib.sha256(contenido_bytes).hexdigest()
        return ArchivoPDF(
            url=url,
            hash_integridad=hash_integridad,
            contenido=contenido_bytes.decode("utf-8"),
        )

    def verificar_integridad(self, contenido):
        if contenido is None or not self.hash_integridad:
            return False
        contenido_bytes = contenido.encode() if isinstance(contenido, str) else contenido
        return hashlib.sha256(contenido_bytes).hexdigest() == self.hash_integridad
