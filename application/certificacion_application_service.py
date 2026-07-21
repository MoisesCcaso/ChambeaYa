#!/usr/bin/python
# -*- coding: utf-8 -*-

class CertificacionApplicationService:
    def __init__(self, certificado_repository=None, perfil_repository=None):
        self.certificado_repository = certificado_repository
        self.perfil_repository = perfil_repository

    def ver_mis_certificados(self, usuario_id):
        self._require_repositories()

        practicante = self.perfil_repository.find_practicante_by_user_id(usuario_id)
        if practicante is None:
            raise ValueError("Perfil de practicante no encontrado")

        certificados = self.certificado_repository.find_by_practicante_id(practicante.id)
        return certificados or []

    def issue_certificate(self):
        raise NotImplementedError("Emisión de certificado asignada al módulo de certificación")

    def verify_certificate(self):
        raise NotImplementedError("Verificación de certificado asignada al módulo de certificación")

    def _require_repositories(self):
        if self.certificado_repository is None:
            raise RuntimeError(
                "CertificacionApplicationService requiere un repositorio de certificado"
            )
        if self.perfil_repository is None:
            raise RuntimeError(
                "CertificacionApplicationService requiere un repositorio de perfil"
            )
