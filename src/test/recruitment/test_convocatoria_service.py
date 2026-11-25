"""Pruebas unitarias para ConvocatoriaApplicationService con dobles."""

import unittest
from unittest.mock import create_autospec

from recruitment.application.convocatoria_application_service import ConvocatoriaApplicationService
from recruitment.domain.convocatoria import Convocatoria
from recruitment.domain.convocatoria_fabrica import ConvocatoriaFabrica
from recruitment.domain.i_convocatoria_repository import IConvocatoriaRepository


class TestConvocatoriaApplicationService(unittest.TestCase):
    """Pruebas aisladas del servicio de aplicación de convocatorias con dobles."""

    def setUp(self):
        self.mock_repo = create_autospec(IConvocatoriaRepository, instance=True)
        self.service = ConvocatoriaApplicationService(convocatoria_repository=self.mock_repo)

    def test_requiere_repositorio_en_todas_las_operaciones(self):
        servicio_sin_repo = ConvocatoriaApplicationService(convocatoria_repository=None)

        with self.assertRaises(RuntimeError) as ctx:
            servicio_sin_repo.create_convocatoria(1, {"titulo": "Test"})
        self.assertIn("requiere un repositorio", str(ctx.exception))

        with self.assertRaises(RuntimeError):
            servicio_sin_repo.publish(1, 10)

        with self.assertRaises(RuntimeError):
            servicio_sin_repo.update(1, 10, {"titulo": "Nuevo"})

        with self.assertRaises(RuntimeError):
            servicio_sin_repo.close(1, 10)

        with self.assertRaises(RuntimeError):
            servicio_sin_repo.reopen(1, 10)

        with self.assertRaises(RuntimeError):
            servicio_sin_repo.duplicate(1, 10)

        with self.assertRaises(RuntimeError):
            servicio_sin_repo.delete(1, 10)

        with self.assertRaises(RuntimeError):
            servicio_sin_repo.search()

        with self.assertRaises(RuntimeError):
            servicio_sin_repo.find_by_id(10)

        with self.assertRaises(RuntimeError):
            servicio_sin_repo.list_for_empresa(1)

    def test_create_convocatoria_valida_y_guarda(self):
        data = {
            "titulo": "Practicante Python",
            "descripcion": "Backend dev",
            "habilidades_requeridas": ["Python"],
            "beneficios": ["Remoto"],
        }
        convocatoria_guardada = Convocatoria(id=1, company_id=5, titulo="Practicante Python")
        self.mock_repo.save.return_value = convocatoria_guardada

        result = self.service.create_convocatoria(company_id=5, data=data)

        self.assertEqual(result, convocatoria_guardada)
        self.mock_repo.save.assert_called_once()
        convocatoria_pasada = self.mock_repo.save.call_args[0][0]
        self.assertEqual(convocatoria_pasada.company_id, 5)
        self.assertEqual(convocatoria_pasada.titulo, "Practicante Python")
        self.assertEqual(convocatoria_pasada.status, Convocatoria.ESTADO_BORRADOR)

    def test_publish_convocatoria_inexistente_lanza_error(self):
        self.mock_repo.find_by_id.return_value = None

        with self.assertRaises(ValueError) as ctx:
            self.service.publish(company_id=1, convocatoria_id=99)
        self.assertIn("Convocatoria no encontrada", str(ctx.exception))
        self.mock_repo.save.assert_not_called()

    def test_publish_convocatoria_de_otra_empresa_lanza_error(self):
        convocatoria = Convocatoria(id=10, company_id=2, status=Convocatoria.ESTADO_BORRADOR)
        self.mock_repo.find_by_id.return_value = convocatoria

        with self.assertRaises(ValueError) as ctx:
            self.service.publish(company_id=1, convocatoria_id=10)
        self.assertIn("La convocatoria no pertenece a esta empresa", str(ctx.exception))
        self.mock_repo.save.assert_not_called()

    def test_publish_exitoso_cambia_a_publicada_y_guarda(self):
        convocatoria = Convocatoria(id=10, company_id=1, status=Convocatoria.ESTADO_BORRADOR)
        self.mock_repo.find_by_id.return_value = convocatoria
        self.mock_repo.save.return_value = convocatoria

        result = self.service.publish(company_id=1, convocatoria_id=10)

        self.assertEqual(result.status, Convocatoria.ESTADO_PUBLICADA)
        self.mock_repo.find_by_id.assert_called_once_with(10)
        self.mock_repo.save.assert_called_once_with(convocatoria)

    def test_update_modifica_campos_y_guarda(self):
        convocatoria = Convocatoria(
            id=10,
            company_id=1,
            titulo="Original",
            descripcion="Desc",
            status=Convocatoria.ESTADO_BORRADOR,
        )
        self.mock_repo.find_by_id.return_value = convocatoria
        self.mock_repo.save.return_value = convocatoria

        nuevos_datos = {
            "titulo": "Titulo Actualizado",
            "descripcion": "Desc Nueva",
            "habilidades_requeridas": ["FastAPI"],
            "beneficios": ["Seguro EPS"],
        }
        result = self.service.update(company_id=1, convocatoria_id=10, data=nuevos_datos)

        self.assertEqual(result.titulo, "Titulo Actualizado")
        self.assertEqual(result.descripcion, "Desc Nueva")
        self.assertEqual(result.habilidades_requeridas, ["FastAPI"])
        self.assertEqual(result.beneficios, ["Seguro EPS"])
        self.mock_repo.save.assert_called_once_with(convocatoria)

    def test_find_owned_lanza_error_si_no_existe_o_no_pertenece_a_empresa(self):
        # Caso 1: No existe
        self.mock_repo.find_by_id.return_value = None
        with self.assertRaises(ValueError) as ctx:
            self.service.update(company_id=1, convocatoria_id=99, data={})
        self.assertIn("Convocatoria no encontrada", str(ctx.exception))

        # Caso 2: Pertenece a otra empresa
        convocatoria_ajena = Convocatoria(id=50, company_id=999)
        self.mock_repo.find_by_id.return_value = convocatoria_ajena
        with self.assertRaises(ValueError) as ctx2:
            self.service.update(company_id=1, convocatoria_id=50, data={})
        self.assertIn("La convocatoria no pertenece a esta empresa", str(ctx2.exception))

    def test_close_y_reopen_flujo_completo(self):
        convocatoria = Convocatoria(id=10, company_id=1, status=Convocatoria.ESTADO_PUBLICADA)
        self.mock_repo.find_by_id.return_value = convocatoria
        self.mock_repo.save.return_value = convocatoria

        # Cerrar
        cerrada = self.service.close(company_id=1, convocatoria_id=10)
        self.assertEqual(cerrada.status, Convocatoria.ESTADO_CERRADA)
        self.mock_repo.save.assert_called_with(convocatoria)

        # Reabrir
        reabierta = self.service.reopen(company_id=1, convocatoria_id=10)
        self.assertEqual(reabierta.status, Convocatoria.ESTADO_PUBLICADA)
        self.mock_repo.save.assert_called_with(convocatoria)

    def test_duplicate_convocatoria(self):
        original = Convocatoria(
            id=10,
            company_id=1,
            titulo="Practicante Mobile",
            descripcion="Flutter dev",
            habilidades_requeridas=["Dart", "Flutter"],
            beneficios=["Capacitaciones"],
            status=Convocatoria.ESTADO_PUBLICADA,
        )
        self.mock_repo.find_by_id.return_value = original
        duplicada = Convocatoria(id=11, company_id=1, titulo="Copia de Practicante Mobile")
        self.mock_repo.save.return_value = duplicada

        result = self.service.duplicate(company_id=1, convocatoria_id=10)

        self.assertEqual(result.id, 11)
        self.assertEqual(result.titulo, "Copia de Practicante Mobile")
        self.mock_repo.save.assert_called_once()
        convocatoria_creada = self.mock_repo.save.call_args[0][0]
        self.assertEqual(convocatoria_creada.titulo, "Copia de Practicante Mobile")
        self.assertEqual(convocatoria_creada.descripcion, "Flutter dev")
        self.assertEqual(convocatoria_creada.habilidades_requeridas, ["Dart", "Flutter"])
        self.assertEqual(convocatoria_creada.beneficios, ["Capacitaciones"])
        self.assertEqual(convocatoria_creada.status, Convocatoria.ESTADO_BORRADOR)

    def test_delete_en_borrador_exitoso(self):
        convocatoria = Convocatoria(id=10, company_id=1, status=Convocatoria.ESTADO_BORRADOR)
        self.mock_repo.find_by_id.return_value = convocatoria
        self.mock_repo.delete.return_value = True

        eliminada = self.service.delete(company_id=1, convocatoria_id=10)

        self.assertEqual(eliminada, convocatoria)
        self.mock_repo.delete.assert_called_once_with(10)

    def test_delete_falla_si_repo_retorna_false(self):
        convocatoria = Convocatoria(id=10, company_id=1, status=Convocatoria.ESTADO_BORRADOR)
        self.mock_repo.find_by_id.return_value = convocatoria
        self.mock_repo.delete.return_value = False

        with self.assertRaises(ValueError) as ctx:
            self.service.delete(company_id=1, convocatoria_id=10)
        self.assertIn("Convocatoria no encontrada", str(ctx.exception))

    def test_search_delega_query_y_estado(self):
        lista_esperada = [Convocatoria(id=1), Convocatoria(id=2)]
        self.mock_repo.search.return_value = lista_esperada

        result = self.service.search(query="Python", status="publicada")

        self.assertEqual(result, lista_esperada)
        self.mock_repo.search.assert_called_once_with(query="Python", status="publicada")

    def test_find_by_id_existente_e_inexistente(self):
        convocatoria = Convocatoria(id=5, company_id=1)
        self.mock_repo.find_by_id.return_value = convocatoria

        # Existente
        result = self.service.find_by_id(5)
        self.assertEqual(result, convocatoria)
        self.mock_repo.find_by_id.assert_called_once_with(5)

        # Inexistente
        self.mock_repo.find_by_id.return_value = None
        with self.assertRaises(ValueError) as ctx:
            self.service.find_by_id(99)
        self.assertIn("Convocatoria no encontrada", str(ctx.exception))

    def test_list_for_empresa_delega_a_repositorio(self):
        lista_empresa = [Convocatoria(id=1, company_id=3)]
        self.mock_repo.find_by_empresa_id.return_value = lista_empresa

        result = self.service.list_for_empresa(company_id=3)

        self.assertEqual(result, lista_empresa)
        self.mock_repo.find_by_empresa_id.assert_called_once_with(3)
