"""I-17: pruebas aisladas del servicio de aplicación de prácticas."""

import unittest
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import call, create_autospec

from application.practica_application_service import PracticaApplicationService
from domain.convocatorias.convocatoria import Convocatoria
from domain.convocatorias.i_convocatoria_repository import IConvocatoriaRepository
from domain.convocatorias.i_postulacion_repository import IPostulacionRepository
from domain.convocatorias.postulacion import Postulacion
from domain.perfil.i_perfil_repository import IPerfilRepository
from domain.practica_evaluacion.entregable import Entregable
from domain.practica_evaluacion.evaluacion import Evaluacion
from domain.practica_evaluacion.i_practica_repository import IPracticaRepository
from domain.practica_evaluacion.practica import Practica

USUARIO_PRACTICANTE_ID = 5
USUARIO_EMPRESA_ID = 6
EMPRESA_ID = 10
PRACTICANTE_ID = 30
POSTULACION_ID = 20
CONVOCATORIA_ID = 40
PRACTICA_ID = 7


class TestPracticaApplicationService(unittest.TestCase):
    def setUp(self):
        self.practicas = create_autospec(IPracticaRepository, instance=True)
        self.perfiles = create_autospec(IPerfilRepository, instance=True)
        self.postulaciones = create_autospec(IPostulacionRepository, instance=True)
        self.convocatorias = create_autospec(IConvocatoriaRepository, instance=True)
        self.service = PracticaApplicationService(
            practica_repository=self.practicas,
            perfil_repository=self.perfiles,
            postulacion_repository=self.postulaciones,
            convocatoria_repository=self.convocatorias,
        )

        self.practica = Practica(
            id=PRACTICA_ID,
            postulacion_id=POSTULACION_ID,
            practicante_id=PRACTICANTE_ID,
        )
        self.postulacion = Postulacion(
            id=POSTULACION_ID,
            convocatoria_id=CONVOCATORIA_ID,
            practicante_id=PRACTICANTE_ID,
            estado=Postulacion.ESTADO_SELECCIONADA,
        )
        self.convocatoria = Convocatoria(
            id=CONVOCATORIA_ID,
            empresa_id=EMPRESA_ID,
            estado=Convocatoria.ESTADO_PUBLICADA,
        )
        self.practicante = SimpleNamespace(id=PRACTICANTE_ID)
        self.empresa = SimpleNamespace(id=EMPRESA_ID)

        self.practicas.find_by_id.return_value = self.practica
        self.practicas.find_by_postulacion_id.return_value = None
        self.practicas.save.side_effect = lambda practica: practica
        self.perfiles.find_practicante_by_user_id.return_value = self.practicante
        self.perfiles.find_empresa_by_user_id.return_value = None
        self.postulaciones.find_by_id.return_value = self.postulacion
        self.convocatorias.find_by_id.return_value = self.convocatoria

    # Inicio de práctica
    def test_inicia_practica_y_guarda_con_argumentos_correctos(self):
        resultado = self.service.start_practica(EMPRESA_ID, POSTULACION_ID)

        self.postulaciones.find_by_id.assert_called_once_with(POSTULACION_ID)
        self.convocatorias.find_by_id.assert_called_once_with(CONVOCATORIA_ID)
        self.practicas.find_by_postulacion_id.assert_called_once_with(POSTULACION_ID)
        practica_guardada = self.practicas.save.call_args.args[0]
        self.assertIs(resultado, practica_guardada)
        self.assertEqual(POSTULACION_ID, practica_guardada.postulacion_id)
        self.assertEqual(PRACTICANTE_ID, practica_guardada.practicante_id)
        self.assertEqual(Practica.ESTADO_EN_CURSO, practica_guardada.estado)

    def test_no_inicia_si_la_postulacion_no_existe(self):
        self.postulaciones.find_by_id.return_value = None
        with self.assertRaisesRegex(ValueError, "Postulación no encontrada"):
            self.service.start_practica(EMPRESA_ID, POSTULACION_ID)
        self.convocatorias.find_by_id.assert_not_called()
        self.practicas.save.assert_not_called()

    def test_no_inicia_si_la_postulacion_no_esta_seleccionada(self):
        self.postulacion.estado = Postulacion.ESTADO_PENDIENTE
        with self.assertRaisesRegex(ValueError, "debe estar seleccionada"):
            self.service.start_practica(EMPRESA_ID, POSTULACION_ID)
        self.convocatorias.find_by_id.assert_not_called()

    def test_no_inicia_si_la_convocatoria_no_existe(self):
        self.convocatorias.find_by_id.return_value = None
        with self.assertRaisesRegex(ValueError, "Convocatoria no encontrada"):
            self.service.start_practica(EMPRESA_ID, POSTULACION_ID)
        self.practicas.find_by_postulacion_id.assert_not_called()

    def test_no_inicia_para_una_empresa_ajena(self):
        with self.assertRaisesRegex(ValueError, "no pertenece a esta empresa"):
            self.service.start_practica(999, POSTULACION_ID)
        self.practicas.find_by_postulacion_id.assert_not_called()

    def test_no_inicia_una_practica_duplicada(self):
        self.practicas.find_by_postulacion_id.return_value = self.practica
        with self.assertRaisesRegex(ValueError, "ya fue iniciada"):
            self.service.start_practica(EMPRESA_ID, POSTULACION_ID)
        self.practicas.save.assert_not_called()

    # Entregables
    def test_sube_entregable_y_guarda_el_agregado(self):
        resultado = self.service.upload_deliverable(
            USUARIO_PRACTICANTE_ID, PRACTICA_ID, "informe.pdf"
        )

        self.perfiles.find_practicante_by_user_id.assert_called_once_with(
            USUARIO_PRACTICANTE_ID
        )
        self.practicas.find_by_id.assert_called_once_with(PRACTICA_ID)
        self.assertEqual("informe.pdf", self.practica.entregables[0].archivo)
        self.practicas.save.assert_called_once_with(self.practica)
        self.assertIs(resultado, self.practica)

    def test_subida_rechaza_perfil_inexistente(self):
        self.perfiles.find_practicante_by_user_id.return_value = None
        with self.assertRaisesRegex(ValueError, "Perfil de practicante no encontrado"):
            self.service.upload_deliverable(999, PRACTICA_ID, "informe.pdf")
        self.practicas.find_by_id.assert_not_called()

    def test_subida_rechaza_practica_inexistente(self):
        self.practicas.find_by_id.return_value = None
        with self.assertRaisesRegex(ValueError, "Práctica no encontrada"):
            self.service.upload_deliverable(
                USUARIO_PRACTICANTE_ID, PRACTICA_ID, "informe.pdf"
            )

    def test_subida_rechaza_practica_de_otro_practicante(self):
        self.practica.practicante_id = 999
        with self.assertRaisesRegex(ValueError, "No autorizado"):
            self.service.upload_deliverable(
                USUARIO_PRACTICANTE_ID, PRACTICA_ID, "informe.pdf"
            )
        self.practicas.save.assert_not_called()

    def test_subida_propaga_regla_de_practica_finalizada(self):
        self.practica.estado = Practica.ESTADO_FINALIZADA
        with self.assertRaisesRegex(ValueError, "práctica finalizada"):
            self.service.upload_deliverable(
                USUARIO_PRACTICANTE_ID, PRACTICA_ID, "informe.pdf"
            )
        self.practicas.save.assert_not_called()

    def test_historial_de_entregables_se_devuelve_ordenado(self):
        ahora = datetime.now(timezone.utc)
        reciente = Entregable(id=2, fecha_subida=ahora)
        antiguo = Entregable(id=1, fecha_subida=ahora - timedelta(days=1))
        self.practica.entregables = [reciente, antiguo]

        resultado = self.service.get_deliverables_history(
            USUARIO_PRACTICANTE_ID, PRACTICA_ID
        )

        self.assertEqual([antiguo, reciente], resultado)
        self.practicas.find_by_id.assert_called_once_with(PRACTICA_ID)

    def test_elimina_entregable_y_guarda_el_agregado(self):
        entregable = Entregable(id=8, archivo="informe.pdf")
        self.practica.entregables = [entregable]

        eliminado = self.service.delete_deliverable(
            USUARIO_PRACTICANTE_ID, PRACTICA_ID, 8
        )

        self.assertIs(entregable, eliminado)
        self.assertEqual([], self.practica.entregables)
        self.practicas.save.assert_called_once_with(self.practica)

    def test_eliminar_entregable_inexistente_no_guarda(self):
        with self.assertRaisesRegex(ValueError, "Entregable no encontrado"):
            self.service.delete_deliverable(
                USUARIO_PRACTICANTE_ID, PRACTICA_ID, 999
            )
        self.practicas.save.assert_not_called()

    # Evaluaciones
    def test_evalua_practica_y_guarda_con_argumentos_correctos(self):
        resultado = self.service.evaluate(EMPRESA_ID, PRACTICA_ID, 85)

        self.practicas.find_by_id.assert_called_once_with(PRACTICA_ID)
        self.postulaciones.find_by_id.assert_called_once_with(POSTULACION_ID)
        self.convocatorias.find_by_id.assert_called_once_with(CONVOCATORIA_ID)
        self.assertEqual(85, self.practica.evaluaciones[0].puntaje)
        self.practicas.save.assert_called_once_with(self.practica)
        self.assertIs(resultado, self.practica)

    def test_evaluar_rechaza_practica_inexistente(self):
        self.practicas.find_by_id.return_value = None
        with self.assertRaisesRegex(ValueError, "Práctica no encontrada"):
            self.service.evaluate(EMPRESA_ID, PRACTICA_ID, 85)
        self.postulaciones.find_by_id.assert_not_called()

    def test_evaluar_rechaza_postulacion_inexistente(self):
        self.postulaciones.find_by_id.return_value = None
        with self.assertRaisesRegex(ValueError, "Postulación no encontrada"):
            self.service.evaluate(EMPRESA_ID, PRACTICA_ID, 85)
        self.convocatorias.find_by_id.assert_not_called()

    def test_evaluar_rechaza_convocatoria_inexistente(self):
        self.convocatorias.find_by_id.return_value = None
        with self.assertRaisesRegex(ValueError, "Convocatoria no encontrada"):
            self.service.evaluate(EMPRESA_ID, PRACTICA_ID, 85)

    def test_evaluar_rechaza_empresa_ajena(self):
        with self.assertRaisesRegex(ValueError, "convocatoria de esta empresa"):
            self.service.evaluate(999, PRACTICA_ID, 85)
        self.practicas.save.assert_not_called()

    def test_evaluar_propaga_puntaje_invalido_y_no_guarda(self):
        with self.assertRaisesRegex(ValueError, "entre 0 y 100"):
            self.service.evaluate(EMPRESA_ID, PRACTICA_ID, 101)
        self.practicas.save.assert_not_called()

    def test_historial_de_evaluaciones_se_devuelve_ordenado(self):
        ahora = datetime.now(timezone.utc)
        reciente = Evaluacion(id=2, fecha_evaluacion=ahora)
        antigua = Evaluacion(id=1, fecha_evaluacion=ahora - timedelta(days=1))
        self.practica.evaluaciones = [reciente, antigua]

        resultado = self.service.get_evaluations_history(
            USUARIO_PRACTICANTE_ID, PRACTICA_ID
        )

        self.assertEqual([antigua, reciente], resultado)

    def test_elimina_evaluacion_como_empresa_propietaria(self):
        evaluacion = Evaluacion(id=9, puntaje=90)
        self.practica.evaluaciones = [evaluacion]

        eliminada = self.service.delete_evaluation(EMPRESA_ID, PRACTICA_ID, 9)

        self.assertIs(evaluacion, eliminada)
        self.assertEqual([], self.practica.evaluaciones)
        self.postulaciones.find_by_id.assert_called_once_with(POSTULACION_ID)
        self.convocatorias.find_by_id.assert_called_once_with(CONVOCATORIA_ID)
        self.practicas.save.assert_called_once_with(self.practica)

    def test_eliminar_evaluacion_rechaza_practica_inexistente(self):
        self.practicas.find_by_id.return_value = None
        with self.assertRaisesRegex(ValueError, "Práctica no encontrada"):
            self.service.delete_evaluation(EMPRESA_ID, PRACTICA_ID, 9)

    def test_eliminar_evaluacion_inexistente_no_guarda(self):
        with self.assertRaisesRegex(ValueError, "Evaluación no encontrada"):
            self.service.delete_evaluation(EMPRESA_ID, PRACTICA_ID, 999)
        self.practicas.save.assert_not_called()

    # Finalización y autorización de empresa
    def test_finaliza_practica_cumpliendo_reglas_y_la_guarda(self):
        self.practica.entregables = [Entregable(id=8)]
        self.practica.evaluaciones = [Evaluacion(id=9, puntaje=60)]

        resultado = self.service.finish(EMPRESA_ID, PRACTICA_ID)

        self.assertEqual(Practica.ESTADO_FINALIZADA, self.practica.estado)
        self.practicas.save.assert_called_once_with(self.practica)
        self.assertIs(resultado, self.practica)

    def test_finalizar_rechaza_practica_inexistente(self):
        self.practicas.find_by_id.return_value = None
        with self.assertRaisesRegex(ValueError, "Práctica no encontrada"):
            self.service.finish(EMPRESA_ID, PRACTICA_ID)

    def test_finalizar_propaga_reglas_de_dominio_y_no_guarda(self):
        with self.assertRaisesRegex(ValueError, "sin entregables"):
            self.service.finish(EMPRESA_ID, PRACTICA_ID)
        self.practicas.save.assert_not_called()

    def test_operacion_de_empresa_rechaza_postulacion_inexistente(self):
        self.postulaciones.find_by_id.return_value = None
        with self.assertRaisesRegex(ValueError, "Postulación no encontrada"):
            self.service.finish(EMPRESA_ID, PRACTICA_ID)
        self.convocatorias.find_by_id.assert_not_called()

    def test_operacion_de_empresa_rechaza_convocatoria_inexistente(self):
        self.convocatorias.find_by_id.return_value = None
        with self.assertRaisesRegex(ValueError, "Convocatoria no encontrada"):
            self.service.finish(EMPRESA_ID, PRACTICA_ID)

    def test_operacion_de_empresa_rechaza_empresa_ajena(self):
        with self.assertRaisesRegex(ValueError, "no pertenece a esta empresa"):
            self.service.finish(999, PRACTICA_ID)
        self.practicas.save.assert_not_called()

    # Consultas y visibilidad
    def test_lista_practicas_del_practicante(self):
        esperadas = [self.practica]
        self.practicas.find_by_practicante_id.return_value = esperadas

        resultado = self.service.list_for_user(USUARIO_PRACTICANTE_ID)

        self.assertIs(esperadas, resultado)
        self.practicas.find_by_practicante_id.assert_called_once_with(PRACTICANTE_ID)
        self.perfiles.find_empresa_by_user_id.assert_not_called()

    def test_lista_practicas_de_empresa_y_omite_postulaciones_sin_practica(self):
        convocatoria_2 = SimpleNamespace(id=41)
        postulacion_2 = SimpleNamespace(id=21)
        postulacion_3 = SimpleNamespace(id=22)
        practica_2 = Practica(id=8, postulacion_id=22, practicante_id=31)
        self.perfiles.find_practicante_by_user_id.return_value = None
        self.perfiles.find_empresa_by_user_id.return_value = self.empresa
        self.convocatorias.find_by_empresa_id.return_value = [
            self.convocatoria,
            convocatoria_2,
        ]
        self.postulaciones.find_by_convocatoria_id.side_effect = [
            [self.postulacion],
            [postulacion_2, postulacion_3],
        ]
        self.practicas.find_by_postulacion_id.side_effect = [
            self.practica,
            None,
            practica_2,
        ]

        resultado = self.service.list_for_user(USUARIO_EMPRESA_ID)

        self.assertEqual([self.practica, practica_2], resultado)
        self.convocatorias.find_by_empresa_id.assert_called_once_with(EMPRESA_ID)
        self.postulaciones.find_by_convocatoria_id.assert_has_calls(
            [call(CONVOCATORIA_ID), call(41)]
        )
        self.assertEqual(
            [call(POSTULACION_ID), call(21), call(22)],
            self.practicas.find_by_postulacion_id.call_args_list,
        )

    def test_listar_rechaza_usuario_sin_perfil(self):
        self.perfiles.find_practicante_by_user_id.return_value = None
        self.perfiles.find_empresa_by_user_id.return_value = None
        with self.assertRaisesRegex(ValueError, "Perfil no encontrado"):
            self.service.list_for_user(999)

    def test_empresa_propietaria_puede_consultar_practica(self):
        self.perfiles.find_practicante_by_user_id.return_value = None
        self.perfiles.find_empresa_by_user_id.return_value = self.empresa

        resultado = self.service.get_for_user(USUARIO_EMPRESA_ID, PRACTICA_ID)

        self.assertIs(self.practica, resultado)
        self.perfiles.find_empresa_by_user_id.assert_called_once_with(USUARIO_EMPRESA_ID)
        self.postulaciones.find_by_id.assert_called_once_with(POSTULACION_ID)

    def test_consulta_visible_rechaza_practica_inexistente(self):
        self.practicas.find_by_id.return_value = None
        with self.assertRaisesRegex(ValueError, "Práctica no encontrada"):
            self.service.get_for_user(USUARIO_PRACTICANTE_ID, PRACTICA_ID)
        self.perfiles.find_practicante_by_user_id.assert_not_called()

    def test_consulta_rechaza_practicante_ajeno_sin_perfil_de_empresa(self):
        self.perfiles.find_practicante_by_user_id.return_value = SimpleNamespace(id=999)
        self.perfiles.find_empresa_by_user_id.return_value = None
        with self.assertRaisesRegex(ValueError, "No autorizado"):
            self.service.get_for_user(USUARIO_PRACTICANTE_ID, PRACTICA_ID)

    # Configuración
    def test_requiere_todos_los_repositorios_antes_de_operar(self):
        servicios_incompletos = (
            PracticaApplicationService(),
            PracticaApplicationService(
                self.practicas, self.perfiles, self.postulaciones, None
            ),
        )
        for servicio in servicios_incompletos:
            with self.subTest(servicio=servicio):
                with self.assertRaisesRegex(RuntimeError, "requiere todos sus repositorios"):
                    servicio.get_for_user(USUARIO_PRACTICANTE_ID, PRACTICA_ID)


if __name__ == "__main__":
    unittest.main()
