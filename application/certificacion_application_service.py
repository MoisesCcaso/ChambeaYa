#!/usr/bin/python
# -*- coding: utf-8 -*-
from domain.certificacion.certificacion_dominio_servicio import CertificacionDominioServicio

class CertificacionApplicationService:
    def __init__(self, certificado_repository=None, practica_repository=None,
                 postulacion_repository=None, convocatoria_repository=None,
                 perfil_repository=None):
        self.certificado_repository = certificado_repository
        self.practica_repository = practica_repository
        self.postulacion_repository = postulacion_repository
        self.convocatoria_repository = convocatoria_repository
        self.perfil_repository = perfil_repository

    def issue_certificate(self, empresa_id, practica_id):
        self._require_repositories()

        practica = self.practica_repository.find_by_id(practica_id)
        if practica is None:
            raise ValueError("Práctica no encontrada")

        postulacion = self.postulacion_repository.find_by_id(practica.postulacion_id)
        if postulacion is None:
            raise ValueError("Postulación no encontrada")

        convocatoria = self.convocatoria_repository.find_by_id(postulacion.convocatoria_id)
        if convocatoria is None:
            raise ValueError("Convocatoria no encontrada")
        if convocatoria.empresa_id != empresa_id:
            raise ValueError("La práctica no pertenece a una convocatoria de esta empresa")

        practicante = self.perfil_repository.find_practicante_by_id(practica.practicante_id)
        if practicante is None:
            raise ValueError("Practicante no encontrado")

        certificado = CertificacionDominioServicio().generar_certificado(
            practica, practicante, convocatoria
        )
        return self.certificado_repository.save(certificado)

    def verify_certificate(self, codigo_qr_valor):
        self._require_repositories()

        certificado = self.certificado_repository.find_by_codigo(codigo_qr_valor)
        if certificado is None:
            raise ValueError("Certificado no encontrado")

        return CertificacionDominioServicio().verificar_codigo_qr(certificado, codigo_qr_valor)

    def _require_repositories(self):
        if self.certificado_repository is None:
            raise RuntimeError("CertificacionApplicationService requiere un repositorio de certificado")


