from domain.matching.sugerencia import Sugerencia
from domain.matching.resultado_matching import ResultadoMatching
from domain.convocatorias.convocatoria import Convocatoria


class MatchingDominioServicio:
    def calcular_match(self, practicante, convocatoria):
        if practicante is None or convocatoria is None:
            return None

        sugerencia = Sugerencia(
            practicante_id=practicante.id,
            convocatoria_id=convocatoria.id,
        )
        score = sugerencia.calcular_compatibilidad(
            practicante.habilidades,
            convocatoria.habilidades_requeridas,
        )

        return ResultadoMatching(
            score_compatibilidad=score,
            practicante_id=practicante.id,
            convocatoria_id=convocatoria.id,
            sugerencia=sugerencia,
            convocatoria=convocatoria,
        )

    def filtrar_convocatorias(self, practicante, convocatorias, umbral=50.0):
        resultados = []
        for convocatoria in convocatorias:
            if convocatoria.estado != Convocatoria.ESTADO_PUBLICADA:
                continue
            resultado = self.calcular_match(practicante, convocatoria)
            if resultado is not None and resultado.es_compatible(umbral):
                resultados.append(resultado)

        return sorted(resultados, key=lambda r: r.score_compatibilidad, reverse=True)
