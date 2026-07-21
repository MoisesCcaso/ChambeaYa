#!/usr/bin/python
# -*- coding: utf-8 -*-

from presentation._serializers import format_fecha


class CertificadoController:
    def __init__(self, certificacion_application_service=None):
        self.certificacion_application_service = certificacion_application_service

    def list_mis_certificados(self, usuario_id):
        self._require_service()
        certificados = self.certificacion_application_service.ver_mis_certificados(usuario_id)
        data = [self._serialize_certificado(c) for c in certificados]
        return {"certificados": data}, 200

    def issue(self):
        raise NotImplementedError("Emisión de certificado asignada al módulo de certificación")

    def verify(self):
        raise NotImplementedError(
            "Verificación de certificado asignada al módulo de certificación"
        )

    def _require_service(self):
        if self.certificacion_application_service is None:
            raise RuntimeError("CertificadoController requiere un servicio de aplicación")

    def _serialize_certificado(self, certificado):
        return {
            "id": certificado.id,
            "codigo": certificado.codigo,
            "practica_id": certificado.practica_id,
            "practicante_id": certificado.practicante_id,
            "estado": certificado.estado,
            "url_verificacion": self._url_verificacion(certificado.codigo_qr),
            "documento_url": self._documento_url(certificado.documento),
            "fecha_emision": format_fecha(certificado.fecha_emision),
        }

    def _url_verificacion(self, codigo_qr):
        if codigo_qr is None:
            return None

        return getattr(codigo_qr, "url_verificacion", None)

    def _documento_url(self, documento):
        if documento is None:
            return None

        return getattr(documento, "url", None)
