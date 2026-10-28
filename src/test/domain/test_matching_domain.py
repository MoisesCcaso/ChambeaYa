"""Pruebas unitarias del dominio de matching (I-11).

Framework: unittest
Cobertura: Coverage.py

Cubre:
  - Sugerencia.calcular_compatibilidad  (cálculo y normalización)
  - ResultadoMatching.es_compatible     (resultados / umbral)
  - MatchingDominioServicio             (calcular_match y filtrar_convocatorias)
"""

import unittest

from domain.convocatorias.convocatoria import Convocatoria
from domain.matching.matching_dominio_servicio import MatchingDominioServicio
from domain.matching.resultado_matching import ResultadoMatching
from domain.matching.sugerencia import Sugerencia
from domain.perfil.practicante import Practicante


def crear_practicante(habilidades, id=1):
    return Practicante(id=id, habilidades=habilidades)


def crear_convocatoria(habilidades, id=1, estado=Convocatoria.ESTADO_PUBLICADA):
    return Convocatoria(id=id, estado=estado, habilidades_requeridas=habilidades)


class SugerenciaCalculoTest(unittest.TestCase):
    """Cálculo del puntaje de compatibilidad."""

    def setUp(self):
        self.sugerencia = Sugerencia(practicante_id=1, convocatoria_id=2)

    def test_valores_por_defecto(self):
        s = Sugerencia()
        self.assertIsNone(s.id)
        self.assertEqual(0.0, s.puntaje_match)
        self.assertEqual([], s.habilidades_coincidentes)

    def test_coincidencia_total_da_100(self):
        score = self.sugerencia.calcular_compatibilidad(
            ["python", "sql"], ["python", "sql"]
        )
        self.assertEqual(100.0, score)
        self.assertEqual(100.0, self.sugerencia.puntaje_match)

    def test_coincidencia_parcial(self):
        score = self.sugerencia.calcular_compatibilidad(
            ["python"], ["python", "sql"]
        )
        self.assertEqual(50.0, score)
        self.assertEqual(["python"], self.sugerencia.habilidades_coincidentes)

    def test_sin_coincidencias_da_cero(self):
        score = self.sugerencia.calcular_compatibilidad(["java"], ["python", "sql"])
        self.assertEqual(0.0, score)
        self.assertEqual([], self.sugerencia.habilidades_coincidentes)

    def test_habilidades_extra_del_practicante_no_penalizan(self):
        score = self.sugerencia.calcular_compatibilidad(
            ["python", "sql", "docker", "git"], ["python", "sql"]
        )
        self.assertEqual(100.0, score)

    def test_proporcion_un_tercio(self):
        score = self.sugerencia.calcular_compatibilidad(
            ["python"], ["python", "sql", "git"]
        )
        self.assertAlmostEqual(100 / 3, score)

    def test_requeridas_vacias_da_cero(self):
        self.assertEqual(0.0, self.sugerencia.calcular_compatibilidad(["python"], []))

    def test_requeridas_none_da_cero(self):
        self.assertEqual(0.0, self.sugerencia.calcular_compatibilidad(["python"], None))

    def test_practicante_sin_habilidades_da_cero(self):
        self.assertEqual(0.0, self.sugerencia.calcular_compatibilidad([], ["python"]))

    def test_practicante_none_da_cero(self):
        self.assertEqual(0.0, self.sugerencia.calcular_compatibilidad(None, ["python"]))

    def test_recalcular_actualiza_el_puntaje(self):
        self.sugerencia.calcular_compatibilidad(["python"], ["python"])
        self.sugerencia.calcular_compatibilidad(["java"], ["python"])
        self.assertEqual(0.0, self.sugerencia.puntaje_match)


class SugerenciaNormalizacionTest(unittest.TestCase):
    """Normalización de habilidades (mayúsculas, espacios, vacías, duplicadas)."""

    def setUp(self):
        self.sugerencia = Sugerencia()

    def test_ignora_mayusculas_y_minusculas(self):
        score = self.sugerencia.calcular_compatibilidad(["PYTHON"], ["python"])
        self.assertEqual(100.0, score)

    def test_ignora_espacios_alrededor(self):
        score = self.sugerencia.calcular_compatibilidad(["  python  "], ["python"])
        self.assertEqual(100.0, score)

    def test_usa_casefold(self):
        score = self.sugerencia.calcular_compatibilidad(["STRASSE"], ["straße"])
        self.assertEqual(100.0, score)

    def test_descarta_habilidades_vacias_o_en_blanco(self):
        score = self.sugerencia.calcular_compatibilidad(
            ["python", "", "   "], ["python", "", "  "]
        )
        self.assertEqual(100.0, score)

    def test_duplicados_se_cuentan_una_vez(self):
        score = self.sugerencia.calcular_compatibilidad(
            ["python", "Python", " PYTHON "], ["python", "sql", "SQL"]
        )
        self.assertEqual(50.0, score)
        self.assertEqual(1, len(self.sugerencia.habilidades_coincidentes))

    def test_convierte_valores_no_texto_a_string(self):
        score = self.sugerencia.calcular_compatibilidad([101, "python"], ["101", "python"])
        self.assertEqual(100.0, score)

    def test_requeridas_solo_en_blanco_da_cero_y_limpia_coincidentes(self):
        self.sugerencia.habilidades_coincidentes = ["previa"]
        score = self.sugerencia.calcular_compatibilidad(["python"], ["", "   "])
        self.assertEqual(0.0, score)
        self.assertEqual([], self.sugerencia.habilidades_coincidentes)

    def test_habilidades_coincidentes_se_guardan_normalizadas(self):
        self.sugerencia.calcular_compatibilidad([" Python ", "SQL"], ["python", "Sql"])
        self.assertCountEqual(["python", "sql"], self.sugerencia.habilidades_coincidentes)


class ResultadoMatchingTest(unittest.TestCase):
    """Estructura y regla de compatibilidad del resultado."""

    def test_valores_por_defecto(self):
        r = ResultadoMatching()
        self.assertEqual(0.0, r.score_compatibilidad)
        self.assertIsNone(r.practicante_id)
        self.assertIsNone(r.convocatoria_id)
        self.assertIsNone(r.sugerencia)
        self.assertIsNone(r.convocatoria)

    def test_guarda_los_valores_recibidos(self):
        sug, conv = Sugerencia(), Convocatoria()
        r = ResultadoMatching(75.0, 1, 2, sug, conv)
        self.assertEqual(75.0, r.score_compatibilidad)
        self.assertEqual(1, r.practicante_id)
        self.assertEqual(2, r.convocatoria_id)
        self.assertIs(sug, r.sugerencia)
        self.assertIs(conv, r.convocatoria)

    def test_es_compatible_por_encima_del_umbral(self):
        self.assertTrue(ResultadoMatching(score_compatibilidad=80).es_compatible())

    def test_es_compatible_en_el_limite_exacto(self):
        self.assertTrue(ResultadoMatching(score_compatibilidad=50).es_compatible())

    def test_no_es_compatible_por_debajo_del_umbral(self):
        self.assertFalse(ResultadoMatching(score_compatibilidad=49.99).es_compatible())

    def test_es_compatible_con_umbral_personalizado(self):
        r = ResultadoMatching(score_compatibilidad=30)
        self.assertFalse(r.es_compatible())
        self.assertTrue(r.es_compatible(umbral=30))
        self.assertTrue(r.es_compatible(umbral=10))


class MatchingDominioServicioCalcularMatchTest(unittest.TestCase):
    """MatchingDominioServicio.calcular_match."""

    def setUp(self):
        self.servicio = MatchingDominioServicio()

    def test_practicante_none_devuelve_none(self):
        self.assertIsNone(self.servicio.calcular_match(None, crear_convocatoria(["python"])))

    def test_convocatoria_none_devuelve_none(self):
        self.assertIsNone(self.servicio.calcular_match(crear_practicante(["python"]), None))

    def test_ambos_none_devuelve_none(self):
        self.assertIsNone(self.servicio.calcular_match(None, None))

    def test_devuelve_resultado_con_ids_y_score(self):
        practicante = crear_practicante(["Python", "SQL"], id=7)
        convocatoria = crear_convocatoria(["python", "sql", "git", "docker"], id=9)

        resultado = self.servicio.calcular_match(practicante, convocatoria)

        self.assertIsInstance(resultado, ResultadoMatching)
        self.assertEqual(50.0, resultado.score_compatibilidad)
        self.assertEqual(7, resultado.practicante_id)
        self.assertEqual(9, resultado.convocatoria_id)
        self.assertIs(convocatoria, resultado.convocatoria)

    def test_la_sugerencia_asociada_refleja_el_calculo(self):
        practicante = crear_practicante(["python"], id=3)
        convocatoria = crear_convocatoria(["python", "sql"], id=4)

        resultado = self.servicio.calcular_match(practicante, convocatoria)

        self.assertIsInstance(resultado.sugerencia, Sugerencia)
        self.assertEqual(3, resultado.sugerencia.practicante_id)
        self.assertEqual(4, resultado.sugerencia.convocatoria_id)
        self.assertEqual(50.0, resultado.sugerencia.puntaje_match)
        self.assertEqual(["python"], resultado.sugerencia.habilidades_coincidentes)

    def test_convocatoria_sin_habilidades_da_score_cero(self):
        resultado = self.servicio.calcular_match(
            crear_practicante(["python"]), crear_convocatoria([])
        )
        self.assertEqual(0.0, resultado.score_compatibilidad)

    def test_calcular_match_no_filtra_por_estado(self):
        convocatoria = crear_convocatoria(["python"], estado=Convocatoria.ESTADO_CERRADA)
        resultado = self.servicio.calcular_match(crear_practicante(["python"]), convocatoria)
        self.assertEqual(100.0, resultado.score_compatibilidad)


class MatchingDominioServicioFiltrarTest(unittest.TestCase):
    """MatchingDominioServicio.filtrar_convocatorias."""

    def setUp(self):
        self.servicio = MatchingDominioServicio()
        self.practicante = crear_practicante(["python", "sql"], id=1)

    def test_lista_vacia_devuelve_lista_vacia(self):
        self.assertEqual([], self.servicio.filtrar_convocatorias(self.practicante, []))

    def test_excluye_convocatorias_borrador_y_cerradas(self):
        convocatorias = [
            crear_convocatoria(["python"], id=1, estado=Convocatoria.ESTADO_BORRADOR),
            crear_convocatoria(["python"], id=2, estado=Convocatoria.ESTADO_CERRADA),
            crear_convocatoria(["python"], id=3, estado=Convocatoria.ESTADO_PUBLICADA),
        ]
        resultados = self.servicio.filtrar_convocatorias(self.practicante, convocatorias)
        self.assertEqual([3], [r.convocatoria_id for r in resultados])

    def test_excluye_convocatorias_sin_estado(self):
        convocatorias = [crear_convocatoria(["python"], id=1, estado=None)]
        self.assertEqual([], self.servicio.filtrar_convocatorias(self.practicante, convocatorias))

    def test_excluye_las_que_no_alcanzan_el_umbral_por_defecto(self):
        convocatorias = [
            crear_convocatoria(["python"], id=1),                      # 100
            crear_convocatoria(["python", "java", "go"], id=2),        # 33.3
        ]
        resultados = self.servicio.filtrar_convocatorias(self.practicante, convocatorias)
        self.assertEqual([1], [r.convocatoria_id for r in resultados])

    def test_incluye_las_que_igualan_el_umbral(self):
        convocatorias = [crear_convocatoria(["python", "java"], id=1)]  # 50 exacto
        resultados = self.servicio.filtrar_convocatorias(self.practicante, convocatorias)
        self.assertEqual(1, len(resultados))
        self.assertEqual(50.0, resultados[0].score_compatibilidad)

    def test_umbral_personalizado(self):
        convocatorias = [
            crear_convocatoria(["python", "java", "go"], id=1),  # 33.3
            crear_convocatoria(["python"], id=2),                # 100
        ]
        resultados = self.servicio.filtrar_convocatorias(
            self.practicante, convocatorias, umbral=30.0
        )
        self.assertEqual(2, len(resultados))

    def test_umbral_cero_incluye_publicadas_sin_coincidencias(self):
        convocatorias = [crear_convocatoria(["java"], id=1)]
        resultados = self.servicio.filtrar_convocatorias(
            self.practicante, convocatorias, umbral=0.0
        )
        self.assertEqual([1], [r.convocatoria_id for r in resultados])

    def test_ordena_por_score_descendente(self):
        convocatorias = [
            crear_convocatoria(["python", "java"], id=1),                  # 50
            crear_convocatoria(["python", "sql"], id=2),                   # 100
            crear_convocatoria(["python", "sql", "java", "go"], id=3),     # 50
            crear_convocatoria(["python", "sql", "java"], id=4),           # 66.6
        ]
        resultados = self.servicio.filtrar_convocatorias(self.practicante, convocatorias)
        scores = [r.score_compatibilidad for r in resultados]
        self.assertEqual(sorted(scores, reverse=True), scores)
        self.assertEqual(2, resultados[0].convocatoria_id)
        self.assertEqual(4, resultados[1].convocatoria_id)

    def test_cada_resultado_es_compatible_con_el_umbral(self):
        convocatorias = [crear_convocatoria(["python"], id=i) for i in range(1, 4)]
        for r in self.servicio.filtrar_convocatorias(self.practicante, convocatorias, 60.0):
            self.assertTrue(r.es_compatible(60.0))

    def test_practicante_none_devuelve_lista_vacia(self):
        convocatorias = [crear_convocatoria(["python"], id=1)]
        self.assertEqual([], self.servicio.filtrar_convocatorias(None, convocatorias))

    def test_practicante_sin_habilidades_devuelve_lista_vacia(self):
        convocatorias = [crear_convocatoria(["python"], id=1)]
        resultados = self.servicio.filtrar_convocatorias(crear_practicante([]), convocatorias)
        self.assertEqual([], resultados)


if __name__ == "__main__":
    unittest.main()