import hashlib
from shared.errors import DomainError
class PdfFile:
    def __init__(self, url=None, integrity_hash=None, content=None):
        self.url = url
        self.integrity_hash = integrity_hash
        self.content = content

    @staticmethod
    def create(internship_id, content, url=None):
        if not content:
            raise DomainError("Debe proveerse el contenido del PDF para generar el archivo")

        content_bytes = content.encode() if isinstance(content, str) else content
        integrity_hash = hashlib.sha256(content_bytes).hexdigest()
        return PdfFile(
            url=url,
            integrity_hash=integrity_hash,
            content=content_bytes.decode("utf-8"),
        )

    def verify_integrity(self, content):
        if content is None or not self.integrity_hash:
            return False
        content_bytes = content.encode() if isinstance(content, str) else content
        return hashlib.sha256(content_bytes).hexdigest() == self.integrity_hash
