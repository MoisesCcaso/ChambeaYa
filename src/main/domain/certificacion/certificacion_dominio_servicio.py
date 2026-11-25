from domain.certificacion.certificado import Certificado
from domain.certificacion.codigo_qr import CodigoQR
from domain.practica_evaluacion.practica import Practica
from shared.errors import ConflictError

class CertificacionDominioServicio:
    def generar_certificado(self, practica, practicante, convocatoria):
        if practica.estado != Practica.ESTADO_FINALIZADA:
            raise ConflictError("Solo se puede certificar una práctica finalizada")
        if not any(evaluacion.esta_aprobada() for evaluacion in practica.evaluaciones):
            raise ConflictError("La práctica no tiene una evaluación aprobada")

        contenido = self._construir_contenido(practicante, convocatoria)
        codigo_qr = CodigoQR.generar(practica.id)
        certificado = Certificado(practica_id=practica.id, codigo_qr=codigo_qr)
        certificado.generar_pdf(contenido)
        return certificado

    def _construir_contenido(self, practicante, convocatoria):
        return (
            f"Se certifica que {practicante.nombres} {practicante.apellidos} "
            f"completó satisfactoriamente la práctica \"{convocatoria.titulo}\"."
        )
