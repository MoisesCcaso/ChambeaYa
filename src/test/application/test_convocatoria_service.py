"""Pruebas unitarias para ConvocatoriaApplicationService con dobles."""

import unittest
from unittest.mock import create_autospec

from application.convocatoria_application_service import ConvocatoriaApplicationService
from domain.convocatorias.convocatoria import Convocatoria
from domain.convocatorias.convocatoria_fabrica import ConvocatoriaFabrica
from domain.convocatorias.i_convocatoria_repository import IConvocatoriaRepository


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
        convocatoria_guardada = Convocatoria(id=1, empresa_id=5, titulo="Practicante Python")
        self.mock_repo.save.return_value = convocatoria_guardada

        resultado = self.service.create_convocatoria(empresa_id=5, data=data)

        self.assertEqual(resultado, convocatoria_guardada)
        self.mock_repo.save.assert_called_once()
        convocatoria_pasada = self.mock_repo.save.call_args[0][0]
        self.assertEqual(convocatoria_pasada.empresa_id, 5)
        self.assertEqual(convocatoria_pasada.titulo, "Practicante Python")
        self.assertEqual(convocatoria_pasada.estado, Convocatoria.ESTADO_BORRADOR)

    def test_publish_convocatoria_inexistente_lanza_error(self):
        self.mock_repo.find_by_id.return_value = None

        with self.assertRaises(ValueError) as ctx:
            self.service.publish(empresa_id=1, convocatoria_id=99)
        self.assertIn("Convocatoria no encontrada", str(ctx.exception))
        self.mock_repo.save.assert_not_called()

    def test_publish_convocatoria_de_otra_empresa_lanza_error(self):
        convocatoria = Convocatoria(id=10, empresa_id=2, estado=Convocatoria.ESTADO_BORRADOR)
        self.mock_repo.find_by_id.return_value = convocatoria

        with self.assertRaises(ValueError) as ctx:
            self.service.publish(empresa_id=1, convocatoria_id=10)
        self.assertIn("La convocatoria no pertenece a esta empresa", str(ctx.exception))
        self.mock_repo.save.assert_not_called()

    def test_publish_exitoso_cambia_a_publicada_y_guarda(self):
        convocatoria = Convocatoria(id=10, empresa_id=1, estado=Convocatoria.ESTADO_BORRADOR)
        self.mock_repo.find_by_id.return_value = convocatoria
        self.mock_repo.save.return_value = convocatoria

        resultado = self.service.publish(empresa_id=1, convocatoria_id=10)

        self.assertEqual(resultado.estado, Convocatoria.ESTADO_PUBLICADA)
        self.mock_repo.find_by_id.assert_called_once_with(10)
        self.mock_repo.save.assert_called_once_with(convocatoria)

    def test_update_modifica_campos_y_guarda(self):
        convocatoria = Convocatoria(
            id=10,
            empresa_id=1,
            titulo="Original",
            descripcion="Desc",
            estado=Convocatoria.ESTADO_BORRADOR,
        )
        self.mock_repo.find_by_id.return_value = convocatoria
        self.mock_repo.save.return_value = convocatoria

        nuevos_datos = {
            "titulo": "Titulo Actualizado",
            "descripcion": "Desc Nueva",
            "habilidades_requeridas": ["FastAPI"],
            "beneficios": ["Seguro EPS"],
        }
        resultado = self.service.update(empresa_id=1, convocatoria_id=10, data=nuevos_datos)

        self.assertEqual(resultado.titulo, "Titulo Actualizado")
        self.assertEqual(resultado.descripcion, "Desc Nueva")
        self.assertEqual(resultado.habilidades_requeridas, ["FastAPI"])
        self.assertEqual(resultado.beneficios, ["Seguro EPS"])
        self.mock_repo.save.assert_called_once_with(convocatoria)

    def test_find_owned_lanza_error_si_no_existe_o_no_pertenece_a_empresa(self):
        # Caso 1: No existe
        self.mock_repo.find_by_id.return_value = None
        with self.assertRaises(ValueError) as ctx:
            self.service.update(empresa_id=1, convocatoria_id=99, data={})
        self.assertIn("Convocatoria no encontrada", str(ctx.exception))

        # Caso 2: Pertenece a otra empresa
        convocatoria_ajena = Convocatoria(id=50, empresa_id=999)
        self.mock_repo.find_by_id.return_value = convocatoria_ajena
        with self.assertRaises(ValueError) as ctx2:
            self.service.update(empresa_id=1, convocatoria_id=50, data={})
        self.assertIn("La convocatoria no pertenece a esta empresa", str(ctx2.exception))

    def test_close_y_reopen_flujo_completo(self):
        convocatoria = Convocatoria(id=10, empresa_id=1, estado=Convocatoria.ESTADO_PUBLICADA)
        self.mock_repo.find_by_id.return_value = convocatoria
        self.mock_repo.save.return_value = convocatoria

        # Cerrar
        cerrada = self.service.close(empresa_id=1, convocatoria_id=10)
        self.assertEqual(cerrada.estado, Convocatoria.ESTADO_CERRADA)
        self.mock_repo.save.assert_called_with(convocatoria)

        # Reabrir
        reabierta = self.service.reopen(empresa_id=1, convocatoria_id=10)
        self.assertEqual(reabierta.estado, Convocatoria.ESTADO_PUBLICADA)
        self.mock_repo.save.assert_called_with(convocatoria)

    def test_duplicate_convocatoria(self):
        original = Convocatoria(
            id=10,
            empresa_id=1,
            titulo="Practicante Mobile",
            descripcion="Flutter dev",
            habilidades_requeridas=["Dart", "Flutter"],
            beneficios=["Capacitaciones"],
            estado=Convocatoria.ESTADO_PUBLICADA,
        )
        self.mock_repo.find_by_id.return_value = original
        duplicada = Convocatoria(id=11, empresa_id=1, titulo="Copia de Practicante Mobile")
        self.mock_repo.save.return_value = duplicada

        resultado = self.service.duplicate(empresa_id=1, convocatoria_id=10)

        self.assertEqual(resultado.id, 11)
        self.assertEqual(resultado.titulo, "Copia de Practicante Mobile")
        self.mock_repo.save.assert_called_once()
        convocatoria_creada = self.mock_repo.save.call_args[0][0]
        self.assertEqual(convocatoria_creada.titulo, "Copia de Practicante Mobile")
        self.assertEqual(convocatoria_creada.descripcion, "Flutter dev")
        self.assertEqual(convocatoria_creada.habilidades_requeridas, ["Dart", "Flutter"])
        self.assertEqual(convocatoria_creada.beneficios, ["Capacitaciones"])
        self.assertEqual(convocatoria_creada.estado, Convocatoria.ESTADO_BORRADOR)

    def test_delete_en_borrador_exitoso(self):
        convocatoria = Convocatoria(id=10, empresa_id=1, estado=Convocatoria.ESTADO_BORRADOR)
        self.mock_repo.find_by_id.return_value = convocatoria
        self.mock_repo.delete.return_value = True

        eliminada = self.service.delete(empresa_id=1, convocatoria_id=10)

        self.assertEqual(eliminada, convocatoria)
        self.mock_repo.delete.assert_called_once_with(10)

    def test_delete_falla_si_repo_retorna_false(self):
        convocatoria = Convocatoria(id=10, empresa_id=1, estado=Convocatoria.ESTADO_BORRADOR)
        self.mock_repo.find_by_id.return_value = convocatoria
        self.mock_repo.delete.return_value = False

        with self.assertRaises(ValueError) as ctx:
            self.service.delete(empresa_id=1, convocatoria_id=10)
        self.assertIn("Convocatoria no encontrada", str(ctx.exception))

    def test_search_delega_query_y_estado(self):
        lista_esperada = [Convocatoria(id=1), Convocatoria(id=2)]
        self.mock_repo.search.return_value = lista_esperada

        resultado = self.service.search(query="Python", estado="publicada")

        self.assertEqual(resultado, lista_esperada)
        self.mock_repo.search.assert_called_once_with(query="Python", estado="publicada")

    def test_find_by_id_existente_e_inexistente(self):
        convocatoria = Convocatoria(id=5, empresa_id=1)
        self.mock_repo.find_by_id.return_value = convocatoria

        # Existente
        resultado = self.service.find_by_id(5)
        self.assertEqual(resultado, convocatoria)
        self.mock_repo.find_by_id.assert_called_once_with(5)

        # Inexistente
        self.mock_repo.find_by_id.return_value = None
        with self.assertRaises(ValueError) as ctx:
            self.service.find_by_id(99)
        self.assertIn("Convocatoria no encontrada", str(ctx.exception))

    def test_list_for_empresa_delega_a_repositorio(self):
        lista_empresa = [Convocatoria(id=1, empresa_id=3)]
        self.mock_repo.find_by_empresa_id.return_value = lista_empresa

        resultado = self.service.list_for_empresa(empresa_id=3)

        self.assertEqual(resultado, lista_empresa)
        self.mock_repo.find_by_empresa_id.assert_called_once_with(3)
