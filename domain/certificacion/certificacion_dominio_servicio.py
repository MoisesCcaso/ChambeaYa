from domain.certificacion.certificado import Certificado
from domain.certificacion.codigo_qr import CodigoQR


class CertificacionDominioServicio:
    def generar_certificado(self, practica_id, practicante_nombres,
                            practicante_apellidos, evaluacion_puntaje,
                            base_url="http://localhost:5000"):
        certificado = Certificado(practica_id=practica_id)
        certificado.generar_hash()

        qr = CodigoQR()
        qr.generar(certificado.id, base_url)
        certificado.codigo_qr = qr

        return certificado

    def verificar_codigo_qr(self, codigo_qr):
        return codigo_qr.verificar()
