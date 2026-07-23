from domain.certificacion.certificacion_dominio_servicio import CertificacionDominioServicio


class CertificacionApplicationService:
    def __init__(self, certificado_repository=None, practica_repository=None,
                 perfil_repository=None, certificacion_servicio=None):
        self.certificado_repository = certificado_repository
        self.practica_repository = practica_repository
        self.perfil_repository = perfil_repository
        self.certificacion_servicio = certificacion_servicio or CertificacionDominioServicio()

    def issue_certificate(self, practica_id, base_url="http://localhost:5000"):
        self._require_repositories()

        practica = self.practica_repository.find_by_id(practica_id)
        if practica is None:
            raise ValueError("Práctica no encontrada")

        practicante = self.perfil_repository.find_practicante_by_user_id(practica.practicante_id)
        if practicante is None:
            raise ValueError("Practicante no encontrado")

        certificado = self.certificacion_servicio.generar_certificado(
            practica_id=practica.id,
            practicante_nombres=practicante.nombres,
            practicante_apellidos=practicante.apellidos,
            evaluacion_puntaje=None,
            base_url=base_url,
        )
        return self.certificado_repository.save(certificado)

    def verify_certificate(self, codigo):
        self._require_repositories()

        certificado = self.certificado_repository.find_by_codigo(codigo)
        if certificado is None:
            return {"valido": False, "error": "Certificado no encontrado"}

        return {
            "valido": certificado.verificar_integridad(),
            "certificado_id": certificado.id,
            "practica_id": certificado.practica_id,
            "fecha_emision": certificado.fecha_emision.isoformat(),
        }

    def _require_repositories(self):
        if self.certificado_repository is None:
            raise RuntimeError("CertificacionApplicationService requiere un repositorio de certificados")

        if self.practica_repository is None:
            raise RuntimeError("CertificacionApplicationService requiere un repositorio de prácticas")

        if self.perfil_repository is None:
            raise RuntimeError("CertificacionApplicationService requiere un repositorio de perfil")
