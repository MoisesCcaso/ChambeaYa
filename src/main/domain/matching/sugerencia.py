from domain.matching.habilidades_matching_strategy import HabilidadesMatchingStrategy


class Sugerencia:
    def __init__(self, id=None, intern_id=None, job_posting_id=None,
                 puntaje_match=None, habilidades_coincidentes=None, job_posting=None,
                 matching_strategy=None):
        self.id = id
        self.intern_id = intern_id
        self.job_posting_id = job_posting_id
        self.puntaje_match = puntaje_match or 0.0
        self.habilidades_coincidentes = habilidades_coincidentes or []
        self.job_posting = job_posting
        self.matching_strategy = (
            matching_strategy
            if matching_strategy is not None
            else HabilidadesMatchingStrategy()
        )

    @property
    def score_compatibilidad(self):
        return self.puntaje_match

    @property
    def sugerencia(self):
        return self

    def es_compatible(self, umbral=50.0):
        return self.puntaje_match >= umbral

    def calcular_compatibilidad(self, habilidades_practicante, required_skills):
        self.puntaje_match, self.habilidades_coincidentes = (
            self.matching_strategy.calcular_compatibilidad(
                habilidades_practicante, required_skills
            )
        )
        return self.puntaje_match
