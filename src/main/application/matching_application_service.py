from domain.matching.matching_dominio_servicio import MatchingDominioServicio
from shared.errors import ForbiddenError


class MatchingApplicationService:
    def __init__(self, sugerencia_repository=None, profile_repository=None,
                 job_posting_repository=None, matching_servicio=None,
                 intern_repository=None):
        self.sugerencia_repository = sugerencia_repository
        self.intern_repository = intern_repository or profile_repository
        self.profile_repository = self.intern_repository
        self.job_posting_repository = job_posting_repository
        self.matching_servicio = matching_servicio or MatchingDominioServicio()

    def suggest_convocatorias(self, user_id, umbral=50.0):
        self._require_repositories()

        intern = self.profile_repository.find_intern_by_user_id(user_id)
        if intern is None:
            raise ForbiddenError("Practicante no encontrado")

        job_postings = self.job_posting_repository.find_all()
        return self.matching_servicio.filtrar_convocatorias(intern, job_postings, umbral)

    def calculate_for_practicante(self, user_id):
        self._require_repositories()

        intern = self.profile_repository.find_intern_by_user_id(user_id)
        if intern is None:
            raise ForbiddenError("Practicante no encontrado")

        job_postings = self.job_posting_repository.find_all()
        results = self.matching_servicio.filtrar_convocatorias(intern, job_postings)

        for result in results:
            self.sugerencia_repository.save(getattr(result, "sugerencia", result))

        return results

    def _require_repositories(self):
        if self.sugerencia_repository is None:
            raise RuntimeError("MatchingApplicationService requiere un repositorio de sugerencias")
        if self.profile_repository is None:
            raise RuntimeError("MatchingApplicationService requiere un repositorio de perfil")
        if self.job_posting_repository is None:
            raise RuntimeError("MatchingApplicationService requiere un repositorio de convocatorias")
