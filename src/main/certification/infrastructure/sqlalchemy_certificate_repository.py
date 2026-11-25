from certification.domain.pdf_file import PdfFile
from certification.domain.certificate import Certificate
from certification.domain.qr_code import QrCode
from certification.domain.i_certificate_repository import ICertificateRepository
from shared.database import db
from certification.infrastructure.models.certificate_model import CertificateModel
 
 

class SqlAlchemyCertificateRepository(ICertificateRepository):
    def save(self, certificate):
        model = None
        if certificate.id is not None:
            model = db.session.get(CertificateModel, certificate.id)

        if model is None:
            model = CertificateModel(internship_id=certificate.internship_id)
            db.session.add(model)

        if certificate.qr_code is not None:
            model.qr_code_value = certificate.qr_code.value
            model.qr_code_verification_url = (
                certificate.qr_code.verification_url
                or f"/certificados/verificar/{certificate.qr_code.value}"
            )
            model.qr_code_hash = certificate.qr_code.integrity_hash

        if certificate.document is not None:
            model.document_url = (
                certificate.document.url
                or f"/certificados/practica/{certificate.internship_id}/pdf"
            )
            model.document_hash = certificate.document.integrity_hash
            model.document_content = certificate.document.content

        db.session.commit()
        return self._to_certificate_domain(model)

    def find_by_id(self, certificate_id):
        model = db.session.get(CertificateModel, certificate_id)
        return self._to_certificate_domain(model)

    def find_by_code(self, qr_code_value):
        model = CertificateModel.query.filter_by(qr_code_value=qr_code_value).first()
        return self._to_certificate_domain(model)

    def find_by_internship_id(self, internship_id):
        model = CertificateModel.query.filter_by(internship_id=internship_id).first()
        return self._to_certificate_domain(model)

    def _to_certificate_domain(self, model):
        if model is None:
            return None

        qr_code = None
        if model.qr_code_value is not None:
            qr_code = QrCode(
                value=model.qr_code_value,
                verification_url=model.qr_code_verification_url,
                integrity_hash=model.qr_code_hash,
            )

        document = None
        if model.document_url is not None or model.document_content is not None:
            document = PdfFile(
                url=model.document_url,
                integrity_hash=model.document_hash,
                content=model.document_content,
            )

        return Certificate(
            id=model.id,
            internship_id=model.internship_id,
            qr_code=qr_code,
            document=document,
        )
