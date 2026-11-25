from domain.certificacion.certificado import Certificado
from domain.certificacion.codigo_qr import CodigoQR
from internships.api import Internship
from shared.errors import ConflictError

class CertificacionDominioServicio:
    def generar_certificado(self, internship, intern, job_posting):
        if internship.status != Internship.STATUS_FINISHED:
            raise ConflictError("Solo se puede certificar una práctica finalizada")
        if not any(evaluation.is_approved() for evaluation in internship.evaluations):
            raise ConflictError("La práctica no tiene una evaluación aprobada")

        contenido = self._construir_contenido(intern, job_posting)
        codigo_qr = CodigoQR.generar(internship.id)
        certificado = Certificado(internship_id=internship.id, codigo_qr=codigo_qr)
        certificado.generar_pdf(contenido)
        return certificado

    def _construir_contenido(self, intern, job_posting):
        return (
            f"Se certifica que {intern.first_names} {intern.last_names} "
            f"completó satisfactoriamente la práctica \"{job_posting.title}\"."
        )
