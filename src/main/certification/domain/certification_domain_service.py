from certification.domain.certificate import Certificate
from certification.domain.qr_code import QrCode
from internships.api import Internship
from shared.errors import ConflictError

class CertificationDomainService:
    def generate_certificate(self, internship, intern, job_posting):
        if internship.status != Internship.STATUS_FINISHED:
            raise ConflictError("Solo se puede certificar una práctica finalizada")
        if not any(evaluation.is_approved() for evaluation in internship.evaluations):
            raise ConflictError("La práctica no tiene una evaluación aprobada")

        content = self._build_content(intern, job_posting)
        qr_code = QrCode.generate(internship.id)
        certificate = Certificate(internship_id=internship.id, qr_code=qr_code)
        certificate.generate_pdf(content)
        return certificate

    def _build_content(self, intern, job_posting):
        return (
            f"Se certifica que {intern.first_names} {intern.last_names} "
            f"completó satisfactoriamente la práctica \"{job_posting.title}\"."
        )
