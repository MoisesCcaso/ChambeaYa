import hashlib
from uuid import uuid4
class QrCode:
    def __init__(self, value=None, verification_url=None, integrity_hash=None):
         self.value = value
         self.verification_url = verification_url
         self.integrity_hash = integrity_hash

    @staticmethod
    def generate(internship_id, verification_url=None):
        value = f"CERT-{internship_id}-{uuid4().hex[:8]}"
        integrity_hash = hashlib.sha256(value.encode()).hexdigest()
        return QrCode(value=value, verification_url=verification_url, integrity_hash=integrity_hash)

    def verify(self, value_to_verify):
        if not self.value or not self.integrity_hash:
            return False
        computed_hash = hashlib.sha256(self.value.encode()).hexdigest()
        return self.value == value_to_verify and computed_hash == self.integrity_hash
