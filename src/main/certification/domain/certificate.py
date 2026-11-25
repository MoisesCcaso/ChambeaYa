from certification.domain.pdf_file import PdfFile

class Certificate:
    def __init__(self, id=None, internship_id=None, qr_code=None, document=None):
        self.id = id
        self.internship_id = internship_id
        self.qr_code = qr_code
        self.document = document

    def generate_pdf(self, content):
        self.document = PdfFile.create(self.internship_id, content)
        return self.document

    def verify_integrity(self, content):
        if self.document is None:
            return False
        return self.document.verify_integrity(content)

    def verify_qr(self, value):
        if self.qr_code is None:
            return False
        return self.qr_code.verify(value)