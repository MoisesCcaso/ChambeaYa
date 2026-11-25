"""Pruebas unitarias del dominio de matching (I-11).

Framework: unittest
Cobertura: Coverage.py

Cubre:
  - Sugerencia.calcular_compatibilidad  (cálculo y normalización)
  - Sugerencia.es_compatible            (regla de compatibilidad / umbral)
  - MatchingDominioServicio             (calcular_match y filtrar_convocatorias)
"""

import unittest

from recruitment.domain.job_posting import JobPosting
from domain.matching.matching_dominio_servicio import MatchingDominioServicio
from domain.matching.sugerencia import Sugerencia
from profiles.domain.intern import Intern


def crear_practicante(skills, id=1):
    return Intern(id=id, skills=skills)


def create_job_posting(skills, id=1, status=JobPosting.STATUS_PUBLISHED):
    return JobPosting(id=id, status=status, required_skills=skills)


class SugerenciaCalculoTest(unittest.TestCase):
    """Cálculo del puntaje de compatibilidad."""

    def setUp(self):
        self.sugerencia = Sugerencia(intern_id=1, job_posting_id=2)

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


class SugerenciaCompatibilidadTest(unittest.TestCase):
    """Estructura y regla de compatibilidad en Sugerencia (Move Method / Inline Class)."""

    def test_valores_por_defecto(self):
        r = Sugerencia()
        self.assertEqual(0.0, r.puntaje_match)
        self.assertEqual(0.0, r.score_compatibilidad)
        self.assertIsNone(r.intern_id)
        self.assertIsNone(r.job_posting_id)
        self.assertIs(r, r.sugerencia)
        self.assertIsNone(r.job_posting)

    def test_guarda_los_valores_recibidos(self):
        conv = JobPosting(id=2)
        r = Sugerencia(
            intern_id=1,
            job_posting_id=2,
            puntaje_match=75.0,
            habilidades_coincidentes=["python"],
            job_posting=conv,
        )
        self.assertEqual(75.0, r.puntaje_match)
        self.assertEqual(75.0, r.score_compatibilidad)
        self.assertEqual(1, r.intern_id)
        self.assertEqual(2, r.job_posting_id)
        self.assertEqual(["python"], r.habilidades_coincidentes)
        self.assertIs(conv, r.job_posting)

    def test_es_compatible_por_encima_del_umbral(self):
        self.assertTrue(Sugerencia(puntaje_match=80.0).es_compatible())

    def test_es_compatible_en_el_limite_exacto(self):
        self.assertTrue(Sugerencia(puntaje_match=50.0).es_compatible())

    def test_no_es_compatible_por_debajo_del_umbral(self):
        self.assertFalse(Sugerencia(puntaje_match=49.99).es_compatible())

    def test_es_compatible_con_umbral_personalizado(self):
        r = Sugerencia(puntaje_match=30.0)
        self.assertFalse(r.es_compatible())
        self.assertTrue(r.es_compatible(umbral=30))
        self.assertTrue(r.es_compatible(umbral=10))


class MatchingDominioServicioCalcularMatchTest(unittest.TestCase):
    """MatchingDominioServicio.calcular_match."""

    def setUp(self):
        self.service = MatchingDominioServicio()

    def test_practicante_none_devuelve_none(self):
        self.assertIsNone(self.service.calcular_match(None, create_job_posting(["python"])))

    def test_convocatoria_none_devuelve_none(self):
        self.assertIsNone(self.service.calcular_match(crear_practicante(["python"]), None))

    def test_ambos_none_devuelve_none(self):
        self.assertIsNone(self.service.calcular_match(None, None))

    def test_devuelve_resultado_con_ids_y_score(self):
        intern = crear_practicante(["Python", "SQL"], id=7)
        job_posting = create_job_posting(["python", "sql", "git", "docker"], id=9)

        result = self.service.calcular_match(intern, job_posting)

        self.assertIsInstance(result, Sugerencia)
        self.assertEqual(50.0, result.puntaje_match)
        self.assertEqual(50.0, result.score_compatibilidad)
        self.assertEqual(7, result.intern_id)
        self.assertEqual(9, result.job_posting_id)
        self.assertIs(job_posting, result.job_posting)

    def test_la_sugerencia_asociada_refleja_el_calculo(self):
        intern = crear_practicante(["python"], id=3)
        job_posting = create_job_posting(["python", "sql"], id=4)

        result = self.service.calcular_match(intern, job_posting)

        self.assertIsInstance(result, Sugerencia)
        self.assertEqual(3, result.intern_id)
        self.assertEqual(4, result.job_posting_id)
        self.assertEqual(50.0, result.puntaje_match)
        self.assertEqual(["python"], result.habilidades_coincidentes)

    def test_convocatoria_sin_habilidades_da_score_cero(self):
        result = self.service.calcular_match(
            crear_practicante(["python"]), create_job_posting([])
        )
        self.assertEqual(0.0, result.score_compatibilidad)

    def test_calcular_match_no_filtra_por_estado(self):
        job_posting = create_job_posting(["python"], status=JobPosting.STATUS_CLOSED)
        result = self.service.calcular_match(crear_practicante(["python"]), job_posting)
        self.assertEqual(100.0, result.score_compatibilidad)


class MatchingDominioServicioFiltrarTest(unittest.TestCase):
    """MatchingDominioServicio.filtrar_convocatorias."""

    def setUp(self):
        self.service = MatchingDominioServicio()
        self.intern = crear_practicante(["python", "sql"], id=1)

    def test_lista_vacia_devuelve_lista_vacia(self):
        self.assertEqual([], self.service.filtrar_convocatorias(self.intern, []))

    def test_excluye_convocatorias_borrador_y_cerradas(self):
        job_postings = [
            create_job_posting(["python"], id=1, status=JobPosting.STATUS_DRAFT),
            create_job_posting(["python"], id=2, status=JobPosting.STATUS_CLOSED),
            create_job_posting(["python"], id=3, status=JobPosting.STATUS_PUBLISHED),
        ]
        results = self.service.filtrar_convocatorias(self.intern, job_postings)
        self.assertEqual([3], [r.job_posting_id for r in results])

    def test_excluye_convocatorias_sin_estado(self):
        job_postings = [create_job_posting(["python"], id=1, status=None)]
        self.assertEqual([], self.service.filtrar_convocatorias(self.intern, job_postings))

    def test_excluye_las_que_no_alcanzan_el_umbral_por_defecto(self):
        job_postings = [
            create_job_posting(["python"], id=1),                      # 100
            create_job_posting(["python", "java", "go"], id=2),        # 33.3
        ]
        results = self.service.filtrar_convocatorias(self.intern, job_postings)
        self.assertEqual([1], [r.job_posting_id for r in results])

    def test_incluye_las_que_igualan_el_umbral(self):
        job_postings = [create_job_posting(["python", "java"], id=1)]  # 50 exacto
        results = self.service.filtrar_convocatorias(self.intern, job_postings)
        self.assertEqual(1, len(results))
        self.assertEqual(50.0, results[0].score_compatibilidad)

    def test_umbral_personalizado(self):
        job_postings = [
            create_job_posting(["python", "java", "go"], id=1),  # 33.3
            create_job_posting(["python"], id=2),                # 100
        ]
        results = self.service.filtrar_convocatorias(
            self.intern, job_postings, umbral=30.0
        )
        self.assertEqual(2, len(results))

    def test_umbral_cero_incluye_publicadas_sin_coincidencias(self):
        job_postings = [create_job_posting(["java"], id=1)]
        results = self.service.filtrar_convocatorias(
            self.intern, job_postings, umbral=0.0
        )
        self.assertEqual([1], [r.job_posting_id for r in results])

    def test_ordena_por_score_descendente(self):
        job_postings = [
            create_job_posting(["python", "java"], id=1),                  # 50
            create_job_posting(["python", "sql"], id=2),                   # 100
            create_job_posting(["python", "sql", "java", "go"], id=3),     # 50
            create_job_posting(["python", "sql", "java"], id=4),           # 66.6
        ]
        results = self.service.filtrar_convocatorias(self.intern, job_postings)
        scores = [r.score_compatibilidad for r in results]
        self.assertEqual(sorted(scores, reverse=True), scores)
        self.assertEqual(2, results[0].job_posting_id)
        self.assertEqual(4, results[1].job_posting_id)

    def test_cada_resultado_es_compatible_con_el_umbral(self):
        job_postings = [create_job_posting(["python"], id=i) for i in range(1, 4)]
        for r in self.service.filtrar_convocatorias(self.intern, job_postings, 60.0):
            self.assertTrue(r.es_compatible(60.0))

    def test_practicante_none_devuelve_lista_vacia(self):
        job_postings = [create_job_posting(["python"], id=1)]
        self.assertEqual([], self.service.filtrar_convocatorias(None, job_postings))

    def test_practicante_sin_habilidades_devuelve_lista_vacia(self):
        job_postings = [create_job_posting(["python"], id=1)]
        results = self.service.filtrar_convocatorias(crear_practicante([]), job_postings)
        self.assertEqual([], results)


if __name__ == "__main__":
    unittest.main()