from recruitment.application.dtos import ConvocatoriaCommand
from recruitment.domain.convocatoria_fabrica import ConvocatoriaFabrica
from shared.error_messages import JOB_POSTING_NOT_FOUND, JOB_APPLICATION_NOT_FOUND
from shared.errors import ForbiddenError, NotFoundError

class ConvocatoriaApplicationService:
    def __init__(self, convocatoria_repository=None, convocatoria_fabrica=None):
        self.convocatoria_repository = convocatoria_repository
        self.convocatoria_fabrica = convocatoria_fabrica or ConvocatoriaFabrica()

    def create_convocatoria(self, company_id, data):
        self._require_repository()
        command = ConvocatoriaCommand.from_dict(data)
        convocatoria = self.convocatoria_fabrica.crear_convocatoria(
            company_id,
            command.titulo,
            descripcion=command.descripcion,
            habilidades_requeridas=command.habilidades_requeridas,
            beneficios=command.beneficios,
        )
        return self.convocatoria_repository.save(convocatoria)

    def publish(self, company_id, convocatoria_id):
        self._require_repository()
        convocatoria = self.convocatoria_repository.find_by_id(convocatoria_id)
        if convocatoria is None:
            raise NotFoundError(JOB_POSTING_NOT_FOUND)
        if convocatoria.company_id != company_id:
            raise ForbiddenError("La convocatoria no pertenece a esta empresa")

        convocatoria.publicar()
        return self.convocatoria_repository.save(convocatoria)

    def update(self, company_id, convocatoria_id, data):
        self._require_repository()
        command = ConvocatoriaCommand.from_dict(data)
        convocatoria = self._find_owned(company_id, convocatoria_id)
        convocatoria.actualizar(
            titulo=command.titulo,
            descripcion=command.descripcion,
            habilidades_requeridas=command.habilidades_requeridas,
            beneficios=command.beneficios,
        )
        return self.convocatoria_repository.save(convocatoria)

    def close(self, company_id, convocatoria_id):
        self._require_repository()
        convocatoria = self._find_owned(company_id, convocatoria_id)
        convocatoria.cerrar()
        return self.convocatoria_repository.save(convocatoria)

    def reopen(self, company_id, convocatoria_id):
        self._require_repository()
        convocatoria = self._find_owned(company_id, convocatoria_id)
        convocatoria.reabrir()
        return self.convocatoria_repository.save(convocatoria)

    def duplicate(self, company_id, convocatoria_id):
        self._require_repository()
        original = self._find_owned(company_id, convocatoria_id)
        return self.create_convocatoria(
            company_id,
            {
                "titulo": f"Copia de {original.titulo}",
                "descripcion": original.descripcion,
                "habilidades_requeridas": list(original.habilidades_requeridas),
                "beneficios": list(original.beneficios),
            },
        )

    def delete(self, company_id, convocatoria_id):
        self._require_repository()
        convocatoria = self._find_owned(company_id, convocatoria_id)
        convocatoria.validar_eliminacion()
        if not self.convocatoria_repository.delete(convocatoria_id):
            raise NotFoundError(JOB_POSTING_NOT_FOUND)
        return convocatoria

    def search(self, query=None, status=None):
        self._require_repository()
        return self.convocatoria_repository.search(query=query, status=status)

    def find_by_id(self, convocatoria_id):
        self._require_repository()
        convocatoria = self.convocatoria_repository.find_by_id(convocatoria_id)
        if convocatoria is None:
            raise NotFoundError(JOB_POSTING_NOT_FOUND)
        return convocatoria

    def list_for_empresa(self, company_id):
        self._require_repository()
        return self.convocatoria_repository.find_by_empresa_id(company_id)

    def _find_owned(self, company_id, convocatoria_id):
        convocatoria = self.convocatoria_repository.find_by_id(convocatoria_id)
        if convocatoria is None:
            raise NotFoundError(JOB_POSTING_NOT_FOUND)
        if convocatoria.company_id != company_id:
            raise ForbiddenError("La convocatoria no pertenece a esta empresa")
        return convocatoria

    def _require_repository(self):
        if self.convocatoria_repository is None:
            raise RuntimeError("ConvocatoriaApplicationService requiere un repositorio")
