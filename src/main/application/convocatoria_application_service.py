from application.dtos import ConvocatoriaCommand
from domain.convocatorias.convocatoria_fabrica import ConvocatoriaFabrica
from application.mensajes_error import CONVOCATORIA_NO_ENCONTRADA, POSTULACION_NO_ENCONTRADA

class ConvocatoriaApplicationService:
    def __init__(self, convocatoria_repository=None, convocatoria_fabrica=None):
        self.convocatoria_repository = convocatoria_repository
        self.convocatoria_fabrica = convocatoria_fabrica or ConvocatoriaFabrica()

    def create_convocatoria(self, empresa_id, data):
        self._require_repository()
        command = ConvocatoriaCommand.from_dict(data)
        convocatoria = self.convocatoria_fabrica.crear_convocatoria(
            empresa_id,
            command.titulo,
            descripcion=command.descripcion,
            habilidades_requeridas=command.habilidades_requeridas,
            beneficios=command.beneficios,
        )
        return self.convocatoria_repository.save(convocatoria)

    def publish(self, empresa_id, convocatoria_id):
        self._require_repository()
        convocatoria = self.convocatoria_repository.find_by_id(convocatoria_id)
        if convocatoria is None:
            raise ValueError(CONVOCATORIA_NO_ENCONTRADA)
        if convocatoria.empresa_id != empresa_id:
            raise ValueError("La convocatoria no pertenece a esta empresa")

        convocatoria.publicar()
        return self.convocatoria_repository.save(convocatoria)

    def update(self, empresa_id, convocatoria_id, data):
        self._require_repository()
        command = ConvocatoriaCommand.from_dict(data)
        convocatoria = self._find_owned(empresa_id, convocatoria_id)
        convocatoria.actualizar(
            titulo=command.titulo,
            descripcion=command.descripcion,
            habilidades_requeridas=command.habilidades_requeridas,
            beneficios=command.beneficios,
        )
        return self.convocatoria_repository.save(convocatoria)

    def close(self, empresa_id, convocatoria_id):
        self._require_repository()
        convocatoria = self._find_owned(empresa_id, convocatoria_id)
        convocatoria.cerrar()
        return self.convocatoria_repository.save(convocatoria)

    def reopen(self, empresa_id, convocatoria_id):
        self._require_repository()
        convocatoria = self._find_owned(empresa_id, convocatoria_id)
        convocatoria.reabrir()
        return self.convocatoria_repository.save(convocatoria)

    def duplicate(self, empresa_id, convocatoria_id):
        self._require_repository()
        original = self._find_owned(empresa_id, convocatoria_id)
        return self.create_convocatoria(
            empresa_id,
            {
                "titulo": f"Copia de {original.titulo}",
                "descripcion": original.descripcion,
                "habilidades_requeridas": list(original.habilidades_requeridas),
                "beneficios": list(original.beneficios),
            },
        )

    def delete(self, empresa_id, convocatoria_id):
        self._require_repository()
        convocatoria = self._find_owned(empresa_id, convocatoria_id)
        convocatoria.validar_eliminacion()
        if not self.convocatoria_repository.delete(convocatoria_id):
            raise ValueError(CONVOCATORIA_NO_ENCONTRADA)
        return convocatoria

    def search(self, query=None, estado=None):
        self._require_repository()
        return self.convocatoria_repository.search(query=query, estado=estado)

    def find_by_id(self, convocatoria_id):
        self._require_repository()
        convocatoria = self.convocatoria_repository.find_by_id(convocatoria_id)
        if convocatoria is None:
            raise ValueError(CONVOCATORIA_NO_ENCONTRADA)
        return convocatoria

    def list_for_empresa(self, empresa_id):
        self._require_repository()
        return self.convocatoria_repository.find_by_empresa_id(empresa_id)

    def _find_owned(self, empresa_id, convocatoria_id):
        convocatoria = self.convocatoria_repository.find_by_id(convocatoria_id)
        if convocatoria is None:
            raise ValueError(CONVOCATORIA_NO_ENCONTRADA)
        if convocatoria.empresa_id != empresa_id:
            raise ValueError("La convocatoria no pertenece a esta empresa")
        return convocatoria

    def _require_repository(self):
        if self.convocatoria_repository is None:
            raise RuntimeError("ConvocatoriaApplicationService requiere un repositorio")
