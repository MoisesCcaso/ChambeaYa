#!/usr/bin/python
# -*- coding: utf-8 -*-

class CertificadoController:
    def __init__(self, certificacion_application_service=None):
        self.certificacion_application_service = certificacion_application_service

    def issue(self, empresa_id, practica_id):
        self._require_service()
        certificado = self.certificacion_application_service.issue_certificate(empresa_id, practica_id)
        return self._serialize_certificado(certificado), 201

    def verify(self, codigo_qr_valor):
        self._require_service()
        es_valido = self.certificacion_application_service.verify_certificate(codigo_qr_valor)
        return {"codigo_qr_valor": codigo_qr_valor, "valido": es_valido}, 200

    def _require_service(self):
        if self.certificacion_application_service is None:
            raise RuntimeError("CertificadoController requiere un servicio de aplicación")

    def _serialize_certificado(self, certificado):
        return {
            "id": certificado.id,
            "practica_id": certificado.practica_id,
            "codigo_qr": {
                "valor": certificado.codigo_qr.valor,
                "url_verificacion": certificado.codigo_qr.url_verificacion,
            } if certificado.codigo_qr else None,
            "documento": {
                "url": certificado.documento.url,
            } if certificado.documento else None,
        }

