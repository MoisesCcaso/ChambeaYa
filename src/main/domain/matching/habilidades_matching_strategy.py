from domain.matching.matching_strategy import MatchingStrategy


class HabilidadesMatchingStrategy(MatchingStrategy):
    """Calcula compatibilidad como porcentaje de habilidades requeridas coincidentes."""

    def calcular_compatibilidad(self, habilidades_practicante, habilidades_requeridas):
        habilidades_practicante = self._normalizar_habilidades(habilidades_practicante)
        habilidades_requeridas = self._normalizar_habilidades(habilidades_requeridas)

        if not habilidades_requeridas:
            return 0.0, []

        coincidentes = habilidades_practicante & habilidades_requeridas
        puntaje = len(coincidentes) / len(habilidades_requeridas) * 100
        return puntaje, list(coincidentes)

    def _normalizar_habilidades(self, skills):
        return {
            str(skill).strip().casefold()
            for skill in skills or []
            if str(skill).strip()
        }
