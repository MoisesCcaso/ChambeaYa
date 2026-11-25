from domain.matching.matching_dominio_servicio import MatchingDominioServicio
from shared.errors import ForbiddenError


class MatchingApplicationService:
    def __init__(self, sugerencia_repository=None, perfil_repository=None,
                 convocatoria_repository=None, matching_servicio=None,
                 practicante_repository=None):
        self.sugerencia_repository = sugerencia_repository
        self.practicante_repository = practicante_repository or perfil_repository
        self.perfil_repository = self.practicante_repository
        self.convocatoria_repository = convocatoria_repository
        self.matching_servicio = matching_servicio or MatchingDominioServicio()

    def suggest_convocatorias(self, user_id, umbral=50.0):
        self._require_repositories()

        practicante = self.perfil_repository.find_practicante_by_user_id(user_id)
        if practicante is None:
            raise ForbiddenError("Practicante no encontrado")

        convocatorias = self.convocatoria_repository.find_all()
        return self.matching_servicio.filtrar_convocatorias(practicante, convocatorias, umbral)

    def calculate_for_practicante(self, user_id):
        self._require_repositories()

        practicante = self.perfil_repository.find_practicante_by_user_id(user_id)
        if practicante is None:
            raise ForbiddenError("Practicante no encontrado")

        convocatorias = self.convocatoria_repository.find_all()
        resultados = self.matching_servicio.filtrar_convocatorias(practicante, convocatorias)

        for result in resultados:
            self.sugerencia_repository.save(getattr(result, "sugerencia", result))

        return resultados

    def _require_repositories(self):
        if self.sugerencia_repository is None:
            raise RuntimeError("MatchingApplicationService requiere un repositorio de sugerencias")
        if self.perfil_repository is None:
            raise RuntimeError("MatchingApplicationService requiere un repositorio de perfil")
        if self.convocatoria_repository is None:
            raise RuntimeError("MatchingApplicationService requiere un repositorio de convocatorias")
