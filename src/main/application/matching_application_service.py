from domain.matching.matching_dominio_servicio import MatchingDominioServicio


class MatchingApplicationService:
    def __init__(self, sugerencia_repository=None, perfil_repository=None,
                 convocatoria_repository=None, matching_servicio=None):
        self.sugerencia_repository = sugerencia_repository
        self.perfil_repository = perfil_repository
        self.convocatoria_repository = convocatoria_repository
        self.matching_servicio = matching_servicio or MatchingDominioServicio()

    def suggest_convocatorias(self, usuario_id, umbral=50.0):
        self._require_repositories()

        practicante = self.perfil_repository.find_practicante_by_user_id(usuario_id)
        if practicante is None:
            raise ValueError("Practicante no encontrado")

        convocatorias = self.convocatoria_repository.find_all()
        return self.matching_servicio.filtrar_convocatorias(practicante, convocatorias, umbral)

    def calculate_for_practicante(self, usuario_id):
        self._require_repositories()

        practicante = self.perfil_repository.find_practicante_by_user_id(usuario_id)
        if practicante is None:
            raise ValueError("Practicante no encontrado")

        convocatorias = self.convocatoria_repository.find_all()
        resultados = self.matching_servicio.filtrar_convocatorias(practicante, convocatorias)

        for resultado in resultados:
            self.sugerencia_repository.save(resultado.sugerencia)

        return resultados

    def _require_repositories(self):
        if self.sugerencia_repository is None:
            raise RuntimeError("MatchingApplicationService requiere un repositorio de sugerencias")
        if self.perfil_repository is None:
            raise RuntimeError("MatchingApplicationService requiere un repositorio de perfil")
        if self.convocatoria_repository is None:
            raise RuntimeError("MatchingApplicationService requiere un repositorio de convocatorias")
