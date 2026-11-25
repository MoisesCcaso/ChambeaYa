"""I-13 - Pruebas aisladas del servicio de aplicación de matching con dobles."""

from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import Mock, call

from matching.application.matching_application_service import MatchingApplicationService
from recruitment.domain.i_job_posting_repository import IJobPostingRepository
from matching.domain.i_sugerencia_repository import ISugerenciaRepository
from profiles.domain.i_intern_repository import IInternRepository


class TestMatchingApplicationService(TestCase):
    """Comprueba resultados e interacciones sin acceder a infraestructura real."""

    def setUp(self):
        self.profile_repository = Mock(spec=IInternRepository)
        self.job_posting_repository = Mock(spec=IJobPostingRepository)
        self.sugerencia_repository = Mock(spec=ISugerenciaRepository)
        self.matching_servicio = Mock()

        self.intern = SimpleNamespace(id=17, skills=["python", "sql"])
        self.job_postings = [SimpleNamespace(id=31), SimpleNamespace(id=32)]
        self.resultado_1 = SimpleNamespace(
            job_posting_id=31,
            sugerencia=SimpleNamespace(intern_id=17, job_posting_id=31),
        )
        self.resultado_2 = SimpleNamespace(
            job_posting_id=32,
            sugerencia=SimpleNamespace(intern_id=17, job_posting_id=32),
        )
        self.results = [self.resultado_1, self.resultado_2]

        self.profile_repository.find_intern_by_user_id.return_value = self.intern
        self.job_posting_repository.find_all.return_value = self.job_postings
        self.matching_servicio.filtrar_convocatorias.return_value = self.results

        self.service = MatchingApplicationService(
            sugerencia_repository=self.sugerencia_repository,
            profile_repository=self.profile_repository,
            job_posting_repository=self.job_posting_repository,
            matching_servicio=self.matching_servicio,
        )

    def test_suggest_convocatorias_devuelve_resultados_y_consulta_dependencias(self):
        results = self.service.suggest_convocatorias(user_id=5, umbral=65.0)

        self.assertIs(self.results, results)
        self.profile_repository.find_intern_by_user_id.assert_called_once_with(5)
        self.job_posting_repository.find_all.assert_called_once_with()
        self.matching_servicio.filtrar_convocatorias.assert_called_once_with(
            self.intern, self.job_postings, 65.0
        )
        self.sugerencia_repository.save.assert_not_called()

    def test_calculate_for_practicante_guarda_cada_sugerencia_y_devuelve_resultados(self):
        results = self.service.calculate_for_practicante(user_id=5)

        self.assertIs(self.results, results)
        self.profile_repository.find_intern_by_user_id.assert_called_once_with(5)
        self.job_posting_repository.find_all.assert_called_once_with()
        self.matching_servicio.filtrar_convocatorias.assert_called_once_with(
            self.intern, self.job_postings
        )
        self.sugerencia_repository.save.assert_has_calls(
            [call(self.resultado_1.sugerencia), call(self.resultado_2.sugerencia)]
        )
        self.assertEqual(2, self.sugerencia_repository.save.call_count)

    def test_calculate_for_practicante_sin_resultados_no_guarda_sugerencias(self):
        self.matching_servicio.filtrar_convocatorias.return_value = []

        results = self.service.calculate_for_practicante(user_id=5)

        self.assertEqual([], results)
        self.sugerencia_repository.save.assert_not_called()

    def test_lanza_error_si_no_encuentra_al_practicante(self):
        self.profile_repository.find_intern_by_user_id.return_value = None

        with self.assertRaisesRegex(ValueError, "Practicante no encontrado"):
            self.service.suggest_convocatorias(user_id=404)

        self.profile_repository.find_intern_by_user_id.assert_called_once_with(404)
        self.job_posting_repository.find_all.assert_not_called()
        self.matching_servicio.filtrar_convocatorias.assert_not_called()

    def test_exige_los_tres_repositorios(self):
        service = MatchingApplicationService(
            profile_repository=self.profile_repository,
            job_posting_repository=self.job_posting_repository,
            matching_servicio=self.matching_servicio,
        )

        with self.assertRaisesRegex(RuntimeError, "repositorio de sugerencias"):
            service.suggest_convocatorias(user_id=5)

        self.profile_repository.find_intern_by_user_id.assert_not_called()


if __name__ == "__main__":
    import unittest

    unittest.main()
