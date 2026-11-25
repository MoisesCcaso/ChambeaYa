"""I-13 - Pruebas aisladas del servicio de aplicación de matching con dobles."""

from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import Mock, call

from application.matching_application_service import MatchingApplicationService
from domain.convocatorias.i_convocatoria_repository import IConvocatoriaRepository
from domain.matching.i_sugerencia_repository import ISugerenciaRepository
from profiles.domain.i_intern_repository import IInternRepository


class TestMatchingApplicationService(TestCase):
    """Comprueba resultados e interacciones sin acceder a infraestructura real."""

    def setUp(self):
        self.profile_repository = Mock(spec=IInternRepository)
        self.convocatoria_repository = Mock(spec=IConvocatoriaRepository)
        self.sugerencia_repository = Mock(spec=ISugerenciaRepository)
        self.matching_servicio = Mock()

        self.intern = SimpleNamespace(id=17, skills=["python", "sql"])
        self.convocatorias = [SimpleNamespace(id=31), SimpleNamespace(id=32)]
        self.resultado_1 = SimpleNamespace(
            convocatoria_id=31,
            sugerencia=SimpleNamespace(intern_id=17, convocatoria_id=31),
        )
        self.resultado_2 = SimpleNamespace(
            convocatoria_id=32,
            sugerencia=SimpleNamespace(intern_id=17, convocatoria_id=32),
        )
        self.resultados = [self.resultado_1, self.resultado_2]

        self.profile_repository.find_intern_by_user_id.return_value = self.intern
        self.convocatoria_repository.find_all.return_value = self.convocatorias
        self.matching_servicio.filtrar_convocatorias.return_value = self.resultados

        self.service = MatchingApplicationService(
            sugerencia_repository=self.sugerencia_repository,
            profile_repository=self.profile_repository,
            convocatoria_repository=self.convocatoria_repository,
            matching_servicio=self.matching_servicio,
        )

    def test_suggest_convocatorias_devuelve_resultados_y_consulta_dependencias(self):
        resultados = self.service.suggest_convocatorias(user_id=5, umbral=65.0)

        self.assertIs(self.resultados, resultados)
        self.profile_repository.find_intern_by_user_id.assert_called_once_with(5)
        self.convocatoria_repository.find_all.assert_called_once_with()
        self.matching_servicio.filtrar_convocatorias.assert_called_once_with(
            self.intern, self.convocatorias, 65.0
        )
        self.sugerencia_repository.save.assert_not_called()

    def test_calculate_for_practicante_guarda_cada_sugerencia_y_devuelve_resultados(self):
        resultados = self.service.calculate_for_practicante(user_id=5)

        self.assertIs(self.resultados, resultados)
        self.profile_repository.find_intern_by_user_id.assert_called_once_with(5)
        self.convocatoria_repository.find_all.assert_called_once_with()
        self.matching_servicio.filtrar_convocatorias.assert_called_once_with(
            self.intern, self.convocatorias
        )
        self.sugerencia_repository.save.assert_has_calls(
            [call(self.resultado_1.sugerencia), call(self.resultado_2.sugerencia)]
        )
        self.assertEqual(2, self.sugerencia_repository.save.call_count)

    def test_calculate_for_practicante_sin_resultados_no_guarda_sugerencias(self):
        self.matching_servicio.filtrar_convocatorias.return_value = []

        resultados = self.service.calculate_for_practicante(user_id=5)

        self.assertEqual([], resultados)
        self.sugerencia_repository.save.assert_not_called()

    def test_lanza_error_si_no_encuentra_al_practicante(self):
        self.profile_repository.find_intern_by_user_id.return_value = None

        with self.assertRaisesRegex(ValueError, "Practicante no encontrado"):
            self.service.suggest_convocatorias(user_id=404)

        self.profile_repository.find_intern_by_user_id.assert_called_once_with(404)
        self.convocatoria_repository.find_all.assert_not_called()
        self.matching_servicio.filtrar_convocatorias.assert_not_called()

    def test_exige_los_tres_repositorios(self):
        service = MatchingApplicationService(
            profile_repository=self.profile_repository,
            convocatoria_repository=self.convocatoria_repository,
            matching_servicio=self.matching_servicio,
        )

        with self.assertRaisesRegex(RuntimeError, "repositorio de sugerencias"):
            service.suggest_convocatorias(user_id=5)

        self.profile_repository.find_intern_by_user_id.assert_not_called()


if __name__ == "__main__":
    import unittest

    unittest.main()
