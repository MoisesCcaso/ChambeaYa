from domain.matching.habilidades_matching_strategy import HabilidadesMatchingStrategy
from domain.matching.sugerencia import Sugerencia
from recruitment.api import JobPosting


class MatchingDominioServicio:
    def __init__(self, matching_strategy=None):
        self.matching_strategy = (
            matching_strategy
            if matching_strategy is not None
            else HabilidadesMatchingStrategy()
        )

    def calcular_match(self, intern, job_posting):
        if intern is None or job_posting is None:
            return None

        sugerencia = Sugerencia(
            intern_id=intern.id,
            job_posting_id=job_posting.id,
            job_posting=job_posting,
            matching_strategy=self.matching_strategy,
        )
        sugerencia.calcular_compatibilidad(
            intern.skills,
            job_posting.required_skills,
        )

        return sugerencia

    def filtrar_convocatorias(self, intern, job_postings, umbral=50.0):
        results = []
        for job_posting in job_postings:
            if job_posting.status != JobPosting.STATUS_PUBLISHED:
                continue
            sugerencia = self.calcular_match(intern, job_posting)
            if sugerencia is not None and sugerencia.es_compatible(umbral):
                results.append(sugerencia)

        return sorted(results, key=lambda r: r.puntaje_match, reverse=True)
