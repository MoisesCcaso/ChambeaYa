"""Pruebas unitarias para PostulacionApplicationService con dobles."""

import unittest
from unittest.mock import MagicMock, create_autospec

from application.postulacion_application_service import PostulacionApplicationService
from domain.convocatorias.convocatoria import Convocatoria
from domain.convocatorias.i_convocatoria_repository import IConvocatoriaRepository
from domain.convocatorias.i_postulacion_repository import IPostulacionRepository
from domain.convocatorias.postulacion import Postulacion
from domain.perfil.i_perfil_repository import IPerfilRepository
from domain.practica_evaluacion.i_practica_repository import IPracticaRepository


class TestPostulacionApplicationService(unittest.TestCase):
    """Pruebas aisladas del servicio de postulación usando autospec en sus 4 repositorios."""

    def setUp(self):
        self.mock_postulacion_repo = create_autospec(IPostulacionRepository, instance=True)
        self.mock_convocatoria_repo = create_autospec(IConvocatoriaRepository, instance=True)
        self.mock_perfil_repo = create_autospec(IPerfilRepository, instance=True)
        self.mock_practica_repo = create_autospec(IPracticaRepository, instance=True)

        self.service = PostulacionApplicationService(
            postulacion_repository=self.mock_postulacion_repo,
            convocatoria_repository=self.mock_convocatoria_repo,
            perfil_repository=self.mock_perfil_repo,
            practica_repository=self.mock_practica_repo,
        )

    def test_require_repositories_lanza_error_si_falta_alguno(self):
        servicios_incompletos = [
            PostulacionApplicationService(None, self.mock_convocatoria_repo, self.mock_perfil_repo, self.mock_practica_repo),
            PostulacionApplicationService(self.mock_postulacion_repo, None, self.mock_perfil_repo, self.mock_practica_repo),
            PostulacionApplicationService(self.mock_postulacion_repo, self.mock_convocatoria_repo, None, self.mock_practica_repo),
            PostulacionApplicationService(self.mock_postulacion_repo, self.mock_convocatoria_repo, self.mock_perfil_repo, None),
        ]

        for s in servicios_incompletos:
            with self.assertRaises(RuntimeError) as ctx:
                s.apply(usuario_id=1, convocatoria_id=10)
            self.assertIn("requiere todos sus repositorios", str(ctx.exception))

            with self.assertRaises(RuntimeError):
                s.list_for_practicante(1)

            with self.assertRaises(RuntimeError):
                s.list_for_convocatoria(1, 10)

            with self.assertRaises(RuntimeError):
                s.select_candidate(1, 100)

            with self.assertRaises(RuntimeError):
                s.reject_candidate(1, 100)

            with self.assertRaises(RuntimeError):
                s.cancel(1, 100)

            with self.assertRaises(RuntimeError):
                s.reconsider_candidate(1, 100)

    # ------------------- Tests de apply -------------------

    def test_apply_perfil_practicante_no_encontrado(self):
        self.mock_perfil_repo.find_practicante_by_user_id.return_value = None

        with self.assertRaises(ValueError) as ctx:
            self.service.apply(usuario_id=1, convocatoria_id=10)
        self.assertIn("Perfil de practicante no encontrado", str(ctx.exception))

    def test_apply_perfil_incompleto_sin_nombres_o_apellidos(self):
        practicante_sin_nombres = MagicMock(nombres="", apellidos="Perez")
        self.mock_perfil_repo.find_practicante_by_user_id.return_value = practicante_sin_nombres

        with self.assertRaises(ValueError) as ctx:
            self.service.apply(usuario_id=1, convocatoria_id=10)
        self.assertIn("Completa tus nombres y apellidos antes de postular", str(ctx.exception))

        practicante_sin_apellidos = MagicMock(nombres="Juan", apellidos="")
        self.mock_perfil_repo.find_practicante_by_user_id.return_value = practicante_sin_apellidos

        with self.assertRaises(ValueError) as ctx2:
            self.service.apply(usuario_id=1, convocatoria_id=10)
        self.assertIn("Completa tus nombres y apellidos antes de postular", str(ctx2.exception))

    def test_apply_convocatoria_no_encontrada(self):
        practicante = MagicMock(id=5, nombres="Juan", apellidos="Perez")
        self.mock_perfil_repo.find_practicante_by_user_id.return_value = practicante
        self.mock_convocatoria_repo.find_by_id.return_value = None

        with self.assertRaises(ValueError) as ctx:
            self.service.apply(usuario_id=1, convocatoria_id=99)
        self.assertIn("Convocatoria no encontrada", str(ctx.exception))

    def test_apply_convocatoria_no_publicada_lanza_error(self):
        practicante = MagicMock(id=5, nombres="Juan", apellidos="Perez")
        self.mock_perfil_repo.find_practicante_by_user_id.return_value = practicante
        convocatoria_borrador = Convocatoria(id=10, estado=Convocatoria.ESTADO_BORRADOR)
        self.mock_convocatoria_repo.find_by_id.return_value = convocatoria_borrador

        with self.assertRaises(ValueError) as ctx:
            self.service.apply(usuario_id=1, convocatoria_id=10)
        self.assertIn("Solo se puede postular a convocatorias publicadas", str(ctx.exception))

    def test_apply_postulacion_existente_no_cancelada_lanza_error(self):
        practicante = MagicMock(id=5, nombres="Juan", apellidos="Perez")
        self.mock_perfil_repo.find_practicante_by_user_id.return_value = practicante
        convocatoria = Convocatoria(id=10, estado=Convocatoria.ESTADO_PUBLICADA)
        self.mock_convocatoria_repo.find_by_id.return_value = convocatoria

        existente = Postulacion(id=1, convocatoria_id=10, practicante_id=5, estado=Postulacion.ESTADO_PENDIENTE)
        self.mock_postulacion_repo.find_by_convocatoria_and_practicante.return_value = existente

        with self.assertRaises(ValueError) as ctx:
            self.service.apply(usuario_id=1, convocatoria_id=10)
        self.assertIn("Ya existe una postulación para esta convocatoria", str(ctx.exception))

    def test_apply_postulacion_existente_cancelada_se_reactiva_y_guarda(self):
        practicante = MagicMock(id=5, nombres="Juan", apellidos="Perez")
        self.mock_perfil_repo.find_practicante_by_user_id.return_value = practicante
        convocatoria = Convocatoria(id=10, estado=Convocatoria.ESTADO_PUBLICADA)
        self.mock_convocatoria_repo.find_by_id.return_value = convocatoria

        existente_cancelada = Postulacion(id=1, convocatoria_id=10, practicante_id=5, estado=Postulacion.ESTADO_CANCELADA)
        self.mock_postulacion_repo.find_by_convocatoria_and_practicante.return_value = existente_cancelada
        self.mock_postulacion_repo.save.return_value = existente_cancelada

        resultado = self.service.apply(usuario_id=1, convocatoria_id=10)

        self.assertEqual(resultado.estado, Postulacion.ESTADO_PENDIENTE)
        self.mock_postulacion_repo.save.assert_called_once_with(existente_cancelada)

    def test_apply_nueva_postulacion_exitosa(self):
        practicante = MagicMock(id=5, nombres="Juan", apellidos="Perez")
        self.mock_perfil_repo.find_practicante_by_user_id.return_value = practicante
        convocatoria = Convocatoria(id=10, estado=Convocatoria.ESTADO_PUBLICADA)
        self.mock_convocatoria_repo.find_by_id.return_value = convocatoria
        self.mock_postulacion_repo.find_by_convocatoria_and_practicante.return_value = None

        guardada = Postulacion(id=20, convocatoria_id=10, practicante_id=5, estado=Postulacion.ESTADO_PENDIENTE)
        self.mock_postulacion_repo.save.return_value = guardada

        resultado = self.service.apply(usuario_id=1, convocatoria_id=10)

        self.assertEqual(resultado, guardada)
        self.mock_postulacion_repo.save.assert_called_once()
        postulacion_creada = self.mock_postulacion_repo.save.call_args[0][0]
        self.assertEqual(postulacion_creada.convocatoria_id, 10)
        self.assertEqual(postulacion_creada.practicante_id, 5)

    # ------------------- Tests de listados -------------------

    def test_list_for_practicante(self):
        practicante = MagicMock(id=5)
        self.mock_perfil_repo.find_practicante_by_user_id.return_value = practicante

        p1 = Postulacion(id=1, convocatoria_id=100, practicante_id=5)
        p2 = Postulacion(id=2, convocatoria_id=101, practicante_id=5)
        self.mock_postulacion_repo.find_by_practicante_id.return_value = [p1, p2]

        c1 = Convocatoria(id=100, titulo="Convo 100")
        c2 = Convocatoria(id=101, titulo="Convo 101")
        self.mock_convocatoria_repo.find_by_id.side_effect = lambda cid: c1 if cid == 100 else c2

        resultado = self.service.list_for_practicante(usuario_id=2)

        self.assertEqual(len(resultado), 2)
        self.assertEqual(resultado[0], (p1, c1))
        self.assertEqual(resultado[1], (p2, c2))

    def test_list_for_practicante_sin_perfil_lanza_error(self):
        self.mock_perfil_repo.find_practicante_by_user_id.return_value = None
        with self.assertRaises(ValueError) as ctx:
            self.service.list_for_practicante(usuario_id=2)
        self.assertIn("Perfil de practicante no encontrado", str(ctx.exception))

    def test_list_for_convocatoria(self):
        convocatoria = Convocatoria(id=10, empresa_id=3)
        self.mock_convocatoria_repo.find_by_id.return_value = convocatoria

        p1 = Postulacion(id=1, convocatoria_id=10, practicante_id=50)
        self.mock_postulacion_repo.find_by_convocatoria_id.return_value = [p1]

        practicante = MagicMock(id=50, nombres="Carlos")
        self.mock_perfil_repo.find_practicante_by_id.return_value = practicante

        practica = MagicMock(id=1000)
        self.mock_practica_repo.find_by_postulacion_id.return_value = practica

        resultado = self.service.list_for_convocatoria(empresa_id=3, convocatoria_id=10)

        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0], (p1, practicante, practica))

    def test_require_owned_convocatoria_en_list_for_convocatoria(self):
        # Convocatoria inexistente
        self.mock_convocatoria_repo.find_by_id.return_value = None
        with self.assertRaises(ValueError) as ctx:
            self.service.list_for_convocatoria(empresa_id=1, convocatoria_id=99)
        self.assertIn("Convocatoria no encontrada", str(ctx.exception))

        # Convocatoria perteneciente a otra empresa
        convocatoria_ajena = Convocatoria(id=10, empresa_id=2)
        self.mock_convocatoria_repo.find_by_id.return_value = convocatoria_ajena
        with self.assertRaises(ValueError) as ctx2:
            self.service.list_for_convocatoria(empresa_id=1, convocatoria_id=10)
        self.assertIn("La convocatoria no pertenece a esta empresa", str(ctx2.exception))

    # ------------------- Tests de select_candidate -------------------

    def test_select_candidate_postulacion_o_convocatoria_no_encontrada(self):
        self.mock_postulacion_repo.find_by_id.return_value = None
        with self.assertRaises(ValueError) as ctx:
            self.service.select_candidate(empresa_id=1, postulacion_id=99)
        self.assertIn("Postulación no encontrada", str(ctx.exception))

        postulacion = Postulacion(id=1, convocatoria_id=10)
        self.mock_postulacion_repo.find_by_id.return_value = postulacion
        self.mock_convocatoria_repo.find_by_id.return_value = None
        with self.assertRaises(ValueError) as ctx2:
            self.service.select_candidate(empresa_id=1, postulacion_id=1)
        self.assertIn("Convocatoria no encontrada", str(ctx2.exception))

    def test_select_candidate_convocatoria_ajena_lanza_error(self):
        postulacion = Postulacion(id=1, convocatoria_id=10)
        self.mock_postulacion_repo.find_by_id.return_value = postulacion
        convocatoria_otra_empresa = Convocatoria(id=10, empresa_id=2)
        self.mock_convocatoria_repo.find_by_id.return_value = convocatoria_otra_empresa

        with self.assertRaises(ValueError) as ctx:
            self.service.select_candidate(empresa_id=1, postulacion_id=1)
        self.assertIn("La convocatoria no pertenece a esta empresa", str(ctx.exception))

    def test_select_candidate_falla_si_otra_practica_ya_iniciada(self):
        postulacion_a_elegir = Postulacion(id=1, convocatoria_id=10, estado=Postulacion.ESTADO_PENDIENTE)
        otra_postulacion = Postulacion(id=2, convocatoria_id=10, estado=Postulacion.ESTADO_SELECCIONADA)

        self.mock_postulacion_repo.find_by_id.return_value = postulacion_a_elegir
        self.mock_convocatoria_repo.find_by_id.return_value = Convocatoria(id=10, empresa_id=1)
        self.mock_postulacion_repo.find_by_convocatoria_id.return_value = [postulacion_a_elegir, otra_postulacion]

        # Simular que otra ya tiene práctica iniciada
        self.mock_practica_repo.find_by_postulacion_id.return_value = MagicMock(id=555)

        with self.assertRaises(ValueError) as ctx:
            self.service.select_candidate(empresa_id=1, postulacion_id=1)
        self.assertIn("No se puede cambiar al candidato porque la práctica seleccionada ya inició", str(ctx.exception))

    def test_select_candidate_exitoso_y_rechaza_otras_pendientes_o_seleccionadas(self):
        postulacion_1 = Postulacion(id=1, convocatoria_id=10, estado=Postulacion.ESTADO_PENDIENTE)
        postulacion_2 = Postulacion(id=2, convocatoria_id=10, estado=Postulacion.ESTADO_PENDIENTE)
        postulacion_3 = Postulacion(id=3, convocatoria_id=10, estado=Postulacion.ESTADO_SELECCIONADA)

        self.mock_postulacion_repo.find_by_id.return_value = postulacion_1
        self.mock_convocatoria_repo.find_by_id.return_value = Convocatoria(id=10, empresa_id=1)
        self.mock_postulacion_repo.find_by_convocatoria_id.return_value = [postulacion_1, postulacion_2, postulacion_3]
        self.mock_practica_repo.find_by_postulacion_id.return_value = None
        self.mock_postulacion_repo.save.side_effect = lambda p: p

        resultado = self.service.select_candidate(empresa_id=1, postulacion_id=1)

        self.assertEqual(resultado.id, 1)
        self.assertEqual(resultado.estado, Postulacion.ESTADO_SELECCIONADA)
        self.assertEqual(postulacion_2.estado, Postulacion.ESTADO_RECHAZADA)
        self.assertEqual(postulacion_3.estado, Postulacion.ESTADO_RECHAZADA)

        # Debe guardar postulacion_1 (seleccionada), postulacion_2 (rechazada) y postulacion_3 (rechazada)
        self.assertEqual(self.mock_postulacion_repo.save.call_count, 3)

    # ------------------- Tests de reject_candidate, cancel y reconsider_candidate -------------------

    def test_reject_candidate_exitoso(self):
        postulacion = Postulacion(id=1, convocatoria_id=10, estado=Postulacion.ESTADO_PENDIENTE)
        self.mock_postulacion_repo.find_by_id.return_value = postulacion
        self.mock_convocatoria_repo.find_by_id.return_value = Convocatoria(id=10, empresa_id=1)
        self.mock_postulacion_repo.save.return_value = postulacion

        resultado = self.service.reject_candidate(empresa_id=1, postulacion_id=1)

        self.assertEqual(resultado.estado, Postulacion.ESTADO_RECHAZADA)
        self.mock_postulacion_repo.save.assert_called_once_with(postulacion)

    def test_reject_candidate_postulacion_no_encontrada(self):
        self.mock_postulacion_repo.find_by_id.return_value = None
        with self.assertRaises(ValueError) as ctx:
            self.service.reject_candidate(empresa_id=1, postulacion_id=99)
        self.assertIn("Postulación no encontrada", str(ctx.exception))

    def test_cancel_exitoso_y_errores(self):
        # Practicante no encontrado
        self.mock_perfil_repo.find_practicante_by_user_id.return_value = None
        with self.assertRaises(ValueError) as ctx:
            self.service.cancel(usuario_id=1, postulacion_id=10)
        self.assertIn("Perfil de practicante no encontrado", str(ctx.exception))

        # Postulación no encontrada
        practicante = MagicMock(id=5)
        self.mock_perfil_repo.find_practicante_by_user_id.return_value = practicante
        self.mock_postulacion_repo.find_by_id.return_value = None
        with self.assertRaises(ValueError) as ctx2:
            self.service.cancel(usuario_id=1, postulacion_id=10)
        self.assertIn("Postulación no encontrada", str(ctx2.exception))

        # Postulación de otro practicante
        postulacion_otra = Postulacion(id=10, practicante_id=99, estado=Postulacion.ESTADO_PENDIENTE)
        self.mock_postulacion_repo.find_by_id.return_value = postulacion_otra
        with self.assertRaises(ValueError) as ctx3:
            self.service.cancel(usuario_id=1, postulacion_id=10)
        self.assertIn("La postulación no pertenece a este practicante", str(ctx3.exception))

        # Cancelación exitosa
        postulacion_propia = Postulacion(id=10, practicante_id=5, estado=Postulacion.ESTADO_PENDIENTE)
        self.mock_postulacion_repo.find_by_id.return_value = postulacion_propia
        self.mock_postulacion_repo.save.return_value = postulacion_propia

        resultado = self.service.cancel(usuario_id=1, postulacion_id=10)
        self.assertEqual(resultado.estado, Postulacion.ESTADO_CANCELADA)
        self.mock_postulacion_repo.save.assert_called_once_with(postulacion_propia)

    def test_reconsider_candidate_exitoso_y_errores(self):
        # Postulación no encontrada
        self.mock_postulacion_repo.find_by_id.return_value = None
        with self.assertRaises(ValueError) as ctx:
            self.service.reconsider_candidate(empresa_id=1, postulacion_id=99)
        self.assertIn("Postulación no encontrada", str(ctx.exception))

        postulacion = Postulacion(id=1, convocatoria_id=10, estado=Postulacion.ESTADO_RECHAZADA)
        self.mock_postulacion_repo.find_by_id.return_value = postulacion
        self.mock_convocatoria_repo.find_by_id.return_value = Convocatoria(id=10, empresa_id=1)

        # Con práctica ya iniciada
        self.mock_practica_repo.find_by_postulacion_id.return_value = MagicMock(id=123)
        with self.assertRaises(ValueError) as ctx2:
            self.service.reconsider_candidate(empresa_id=1, postulacion_id=1)
        self.assertIn("No se puede cambiar la decisión porque la práctica ya fue iniciada", str(ctx2.exception))

        # Reconsideración exitosa
        self.mock_practica_repo.find_by_postulacion_id.return_value = None
        self.mock_postulacion_repo.save.return_value = postulacion

        resultado = self.service.reconsider_candidate(empresa_id=1, postulacion_id=1)
        self.assertEqual(resultado.estado, Postulacion.ESTADO_PENDIENTE)
        self.mock_postulacion_repo.save.assert_called_once_with(postulacion)
