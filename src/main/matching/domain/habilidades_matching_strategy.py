from matching.domain.matching_strategy import MatchingStrategy


class HabilidadesMatchingStrategy(MatchingStrategy):
    """Calcula compatibilidad como porcentaje de habilidades requeridas coincidentes."""

    def calcular_compatibilidad(self, habilidades_practicante, required_skills):
        habilidades_practicante = self._normalizar_habilidades(habilidades_practicante)
        required_skills = self._normalizar_habilidades(required_skills)

        if not required_skills:
            return 0.0, []

        coincidentes = habilidades_practicante & required_skills
        puntaje = len(coincidentes) / len(required_skills) * 100
        return puntaje, list(coincidentes)

    def _normalizar_habilidades(self, skills):
        return {
            str(skill).strip().casefold()
            for skill in skills or []
            if str(skill).strip()
        }
