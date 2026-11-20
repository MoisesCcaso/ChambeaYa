from domain.matching.sugerencia import Sugerencia
from domain.convocatorias.convocatoria import Convocatoria


class MatchingDominioServicio:
    def calcular_match(self, practicante, convocatoria):
        if practicante is None or convocatoria is None:
            return None

        sugerencia = Sugerencia(
            practicante_id=practicante.id,
            convocatoria_id=convocatoria.id,
            convocatoria=convocatoria,
        )
        sugerencia.calcular_compatibilidad(
            practicante.habilidades,
            convocatoria.habilidades_requeridas,
        )

        return sugerencia

    def filtrar_convocatorias(self, practicante, convocatorias, umbral=50.0):
        resultados = []
        for convocatoria in convocatorias:
            if convocatoria.estado != Convocatoria.ESTADO_PUBLICADA:
                continue
            sugerencia = self.calcular_match(practicante, convocatoria)
            if sugerencia is not None and sugerencia.es_compatible(umbral):
                resultados.append(sugerencia)

        return sorted(resultados, key=lambda r: r.puntaje_match, reverse=True)
