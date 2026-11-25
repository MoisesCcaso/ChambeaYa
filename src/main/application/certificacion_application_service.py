from domain.certificacion.certificacion_dominio_servicio import CertificacionDominioServicio
from shared.error_messages import JOB_POSTING_NOT_FOUND, JOB_APPLICATION_NOT_FOUND
from shared.errors import ForbiddenError, NotFoundError

class CertificacionApplicationService:
    def __init__(self, certificado_repository=None, practica_repository=None,
                 postulacion_repository=None, convocatoria_repository=None,
                 perfil_repository=None, notificacion_service=None):
        self.certificado_repository = certificado_repository
        self.practica_repository = practica_repository
        self.postulacion_repository = postulacion_repository
        self.convocatoria_repository = convocatoria_repository
        self.perfil_repository = perfil_repository
        self.notificacion_service = notificacion_service

    def issue_certificate(self, empresa_id, practica_id):
        self._require_repositories()

        practica = self.practica_repository.find_by_id(practica_id)
        if practica is None:
            raise NotFoundError("Práctica no encontrada")

        postulacion = self.postulacion_repository.find_by_id(practica.postulacion_id)
        if postulacion is None:
            raise NotFoundError(JOB_APPLICATION_NOT_FOUND)

        convocatoria = self.convocatoria_repository.find_by_id(postulacion.convocatoria_id)
        if convocatoria is None:
            raise NotFoundError(JOB_POSTING_NOT_FOUND)
        if convocatoria.empresa_id != empresa_id:
            raise ForbiddenError("La práctica no pertenece a una convocatoria de esta empresa")

        practicante = self.perfil_repository.find_practicante_by_id(practica.practicante_id)
        if practicante is None:
            raise NotFoundError("Practicante no encontrado")

        existente = self.certificado_repository.find_by_practica_id(practica_id)
        if existente is not None:
            return existente, False

        certificado = CertificacionDominioServicio().generar_certificado(
            practica, practicante, convocatoria
        )
        guardado = self.certificado_repository.save(certificado)
        self._notificar_emision(practicante, practica_id)
        return guardado, True

    def _notificar_emision(self, practicante, practica_id):
        if self.notificacion_service is None:
            return
        usuario_id = getattr(practicante, "usuario_id", None)
        if not usuario_id:
            return
        try:
            self.notificacion_service.create_notification(
                usuario_destino_id=usuario_id,
                tipo="CERTIFICADO_EMITIDO",
                mensaje="Tu certificado digital ha sido emitido",
                metadata={"practica_id": practica_id},
            )
        except Exception:
            pass

    def verify_certificate(self, codigo_qr_valor):
        self._require_repositories()

        certificado = self.certificado_repository.find_by_codigo(codigo_qr_valor)
        if certificado is None:
            raise NotFoundError("Certificado no encontrado")

        qr_valido = certificado.verificar_qr(codigo_qr_valor)
        documento_valido = (
            certificado.documento is not None
            and certificado.verificar_integridad(certificado.documento.contenido)
        )
        return qr_valido and documento_valido

    def find_by_practica_id(self, practica_id):
        self._require_repositories()
        return self.certificado_repository.find_by_practica_id(practica_id)

    def _require_repositories(self):
        if any(
            repository is None
            for repository in (
                self.certificado_repository,
                self.practica_repository,
                self.postulacion_repository,
                self.convocatoria_repository,
                self.perfil_repository,
            )
        ):
            raise RuntimeError("CertificacionApplicationService requiere todos sus repositorios")


