class MatchingController:
    def __init__(self, matching_application_service=None):
        self.matching_application_service = matching_application_service

    def suggest_convocatorias(self, usuario_id):
        self._require_service()
        resultados = self.matching_application_service.suggest_convocatorias(usuario_id)
        return [self._serialize_resultado(r) for r in resultados], 200

    def calculate_match(self, usuario_id):
        self._require_service()
        resultados = self.matching_application_service.calculate_for_practicante(usuario_id)
        return [self._serialize_resultado(r) for r in resultados], 200

    def _serialize_resultado(self, resultado):
        return {
            "practicante_id": resultado.practicante_id,
            "convocatoria_id": resultado.convocatoria_id,
            "score_compatibilidad": round(resultado.score_compatibilidad, 2),
            "es_compatible": resultado.es_compatible(),
        }

    def _require_service(self):
        if self.matching_application_service is None:
            raise RuntimeError("MatchingController requiere un servicio de aplicación")
