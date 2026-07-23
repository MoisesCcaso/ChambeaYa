class CertificadoController:
    def __init__(self, certificacion_application_service=None):
        self.certificacion_application_service = certificacion_application_service

    def issue(self, payload):
        self._require_service()
        practica_id = payload.get("practica_id")

        if not practica_id:
            return {"error": "practica_id es requerido"}, 400

        certificado = self.certificacion_application_service.issue_certificate(practica_id)
        return self._serialize(certificado), 201

    def verify(self, codigo):
        self._require_service()
        resultado = self.certificacion_application_service.verify_certificate(codigo)
        return resultado, 200

    def _serialize(self, certificado):
        return {
            "id": certificado.id,
            "practica_id": certificado.practica_id,
            "fecha_emision": certificado.fecha_emision.isoformat(),
            "qr_valor": certificado.codigo_qr.valor,
            "qr_url": certificado.codigo_qr.url_verificacion,
        }

    def _require_service(self):
        if self.certificacion_application_service is None:
            raise RuntimeError("CertificadoController requiere un servicio de aplicación")
