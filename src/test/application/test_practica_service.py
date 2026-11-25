"""I-17: pruebas aisladas del servicio de aplicación de prácticas."""

import unittest
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import call, create_autospec

from application.practica_application_service import PracticaApplicationService
from recruitment.domain.job_posting import JobPosting
from recruitment.domain.i_job_posting_repository import IJobPostingRepository
from recruitment.domain.i_job_application_repository import IJobApplicationRepository
from recruitment.domain.job_application import JobApplication
from profiles.domain.i_profile_repository import IProfileRepository
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
        self.profiles_repo = create_autospec(IProfileRepository, instance=True)
        self.job_applications = create_autospec(IJobApplicationRepository, instance=True)
        self.job_postings = create_autospec(IJobPostingRepository, instance=True)
        self.service = PracticaApplicationService(
            practica_repository=self.practicas,
            profile_repository=self.profiles_repo,
            job_application_repository=self.job_applications,
            job_posting_repository=self.job_postings,
        )

        self.practica = Practica(
            id=PRACTICA_ID,
            job_application_id=POSTULACION_ID,
            intern_id=PRACTICANTE_ID,
        )
        self.job_application = JobApplication(
            id=POSTULACION_ID,
            job_posting_id=CONVOCATORIA_ID,
            intern_id=PRACTICANTE_ID,
            status=JobApplication.STATUS_SELECTED,
        )
        self.job_posting = JobPosting(
            id=CONVOCATORIA_ID,
            company_id=EMPRESA_ID,
            status=JobPosting.STATUS_PUBLISHED,
        )
        self.intern = SimpleNamespace(id=PRACTICANTE_ID)
        self.company = SimpleNamespace(id=EMPRESA_ID)

        self.practicas.find_by_id.return_value = self.practica
        self.practicas.find_by_job_application_id.return_value = None
        self.practicas.save.side_effect = lambda practica: practica
        self.profiles_repo.find_intern_by_user_id.return_value = self.intern
        self.profiles_repo.find_company_by_user_id.return_value = None
        self.job_applications.find_by_id.return_value = self.job_application
        self.job_postings.find_by_id.return_value = self.job_posting

    # Inicio de práctica
    def test_inicia_practica_y_guarda_con_argumentos_correctos(self):
        result = self.service.start_practica(EMPRESA_ID, POSTULACION_ID)

        self.job_applications.find_by_id.assert_called_once_with(POSTULACION_ID)
        self.job_postings.find_by_id.assert_called_once_with(CONVOCATORIA_ID)
        self.practicas.find_by_job_application_id.assert_called_once_with(POSTULACION_ID)
        practica_guardada = self.practicas.save.call_args.args[0]
        self.assertIs(result, practica_guardada)
        self.assertEqual(POSTULACION_ID, practica_guardada.job_application_id)
        self.assertEqual(PRACTICANTE_ID, practica_guardada.intern_id)
        self.assertEqual(Practica.ESTADO_EN_CURSO, practica_guardada.status)

    def test_no_inicia_si_la_postulacion_no_existe(self):
        self.job_applications.find_by_id.return_value = None
        with self.assertRaisesRegex(ValueError, "Postulación no encontrada"):
            self.service.start_practica(EMPRESA_ID, POSTULACION_ID)
        self.job_postings.find_by_id.assert_not_called()
        self.practicas.save.assert_not_called()

    def test_no_inicia_si_la_postulacion_no_esta_seleccionada(self):
        self.job_application.status = JobApplication.STATUS_PENDING
        with self.assertRaisesRegex(ValueError, "debe estar seleccionada"):
            self.service.start_practica(EMPRESA_ID, POSTULACION_ID)
        self.job_postings.find_by_id.assert_not_called()

    def test_no_inicia_si_la_convocatoria_no_existe(self):
        self.job_postings.find_by_id.return_value = None
        with self.assertRaisesRegex(ValueError, "Convocatoria no encontrada"):
            self.service.start_practica(EMPRESA_ID, POSTULACION_ID)
        self.practicas.find_by_job_application_id.assert_not_called()

    def test_no_inicia_para_una_empresa_ajena(self):
        with self.assertRaisesRegex(ValueError, "no pertenece a esta empresa"):
            self.service.start_practica(999, POSTULACION_ID)
        self.practicas.find_by_job_application_id.assert_not_called()

    def test_no_inicia_una_practica_duplicada(self):
        self.practicas.find_by_job_application_id.return_value = self.practica
        with self.assertRaisesRegex(ValueError, "ya fue iniciada"):
            self.service.start_practica(EMPRESA_ID, POSTULACION_ID)
        self.practicas.save.assert_not_called()

    # Entregables
    def test_sube_entregable_y_guarda_el_agregado(self):
        result = self.service.upload_deliverable(
            USUARIO_PRACTICANTE_ID, PRACTICA_ID, "informe.pdf"
        )

        self.profiles_repo.find_intern_by_user_id.assert_called_once_with(
            USUARIO_PRACTICANTE_ID
        )
        self.practicas.find_by_id.assert_called_once_with(PRACTICA_ID)
        self.assertEqual("informe.pdf", self.practica.entregables[0].archivo)
        self.practicas.save.assert_called_once_with(self.practica)
        self.assertIs(result, self.practica)

    def test_subida_rechaza_perfil_inexistente(self):
        self.profiles_repo.find_intern_by_user_id.return_value = None
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
        self.practica.intern_id = 999
        with self.assertRaisesRegex(ValueError, "No autorizado"):
            self.service.upload_deliverable(
                USUARIO_PRACTICANTE_ID, PRACTICA_ID, "informe.pdf"
            )
        self.practicas.save.assert_not_called()

    def test_subida_propaga_regla_de_practica_finalizada(self):
        self.practica.status = Practica.ESTADO_FINALIZADA
        with self.assertRaisesRegex(ValueError, "práctica finalizada"):
            self.service.upload_deliverable(
                USUARIO_PRACTICANTE_ID, PRACTICA_ID, "informe.pdf"
            )
        self.practicas.save.assert_not_called()

    def test_historial_de_entregables_se_devuelve_ordenado(self):
        now_value = datetime.now(timezone.utc)
        reciente = Entregable(id=2, fecha_subida=now_value)
        antiguo = Entregable(id=1, fecha_subida=now_value - timedelta(days=1))
        self.practica.entregables = [reciente, antiguo]

        result = self.service.get_deliverables_history(
            USUARIO_PRACTICANTE_ID, PRACTICA_ID
        )

        self.assertEqual([antiguo, reciente], result)
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
        result = self.service.evaluate(EMPRESA_ID, PRACTICA_ID, 85)

        self.practicas.find_by_id.assert_called_once_with(PRACTICA_ID)
        self.job_applications.find_by_id.assert_called_once_with(POSTULACION_ID)
        self.job_postings.find_by_id.assert_called_once_with(CONVOCATORIA_ID)
        self.assertEqual(85, self.practica.evaluaciones[0].score)
        self.practicas.save.assert_called_once_with(self.practica)
        self.assertIs(result, self.practica)

    def test_evalua_practica_y_notifica_al_practicante(self):
        mock_notif = unittest.mock.Mock()
        self.service.notification_service = mock_notif
        self.intern.user_id = 99
        self.profiles_repo.find_intern_by_id.return_value = self.intern

        result = self.service.evaluate(EMPRESA_ID, PRACTICA_ID, 85)

        self.assertIs(result, self.practica)
        mock_notif.create_notification.assert_called_once_with(
            recipient_user_id=99,
            notification_type="EVALUACION_DISPONIBLE",
            message="Tu práctica tiene una nueva evaluación disponible",
            metadata={"practica_id": PRACTICA_ID},
        )

    def test_evalua_practica_tolera_fallo_en_notificacion(self):
        mock_notif = unittest.mock.Mock()
        mock_notif.create_notification.side_effect = RuntimeError("Notification Error")
        self.service.notification_service = mock_notif
        self.intern.user_id = 99
        self.profiles_repo.find_intern_by_id.return_value = self.intern

        result = self.service.evaluate(EMPRESA_ID, PRACTICA_ID, 85)
        self.assertIs(result, self.practica)

    def test_evaluar_rechaza_practica_inexistente(self):
        self.practicas.find_by_id.return_value = None
        with self.assertRaisesRegex(ValueError, "Práctica no encontrada"):
            self.service.evaluate(EMPRESA_ID, PRACTICA_ID, 85)
        self.job_applications.find_by_id.assert_not_called()

    def test_evaluar_rechaza_postulacion_inexistente(self):
        self.job_applications.find_by_id.return_value = None
        with self.assertRaisesRegex(ValueError, "Postulación no encontrada"):
            self.service.evaluate(EMPRESA_ID, PRACTICA_ID, 85)
        self.job_postings.find_by_id.assert_not_called()

    def test_evaluar_rechaza_convocatoria_inexistente(self):
        self.job_postings.find_by_id.return_value = None
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
        now_value = datetime.now(timezone.utc)
        reciente = Evaluacion(id=2, fecha_evaluacion=now_value)
        antigua = Evaluacion(id=1, fecha_evaluacion=now_value - timedelta(days=1))
        self.practica.evaluaciones = [reciente, antigua]

        result = self.service.get_evaluations_history(
            USUARIO_PRACTICANTE_ID, PRACTICA_ID
        )

        self.assertEqual([antigua, reciente], result)

    def test_elimina_evaluacion_como_empresa_propietaria(self):
        evaluacion = Evaluacion(id=9, score=90)
        self.practica.evaluaciones = [evaluacion]

        deleted = self.service.delete_evaluation(EMPRESA_ID, PRACTICA_ID, 9)

        self.assertIs(evaluacion, deleted)
        self.assertEqual([], self.practica.evaluaciones)
        self.job_applications.find_by_id.assert_called_once_with(POSTULACION_ID)
        self.job_postings.find_by_id.assert_called_once_with(CONVOCATORIA_ID)
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
        self.practica.evaluaciones = [Evaluacion(id=9, score=60)]

        result = self.service.finish(EMPRESA_ID, PRACTICA_ID)

        self.assertEqual(Practica.ESTADO_FINALIZADA, self.practica.status)
        self.practicas.save.assert_called_once_with(self.practica)
        self.assertIs(result, self.practica)

    def test_finalizar_rechaza_practica_inexistente(self):
        self.practicas.find_by_id.return_value = None
        with self.assertRaisesRegex(ValueError, "Práctica no encontrada"):
            self.service.finish(EMPRESA_ID, PRACTICA_ID)

    def test_finalizar_propaga_reglas_de_dominio_y_no_guarda(self):
        with self.assertRaisesRegex(ValueError, "sin entregables"):
            self.service.finish(EMPRESA_ID, PRACTICA_ID)
        self.practicas.save.assert_not_called()

    def test_operacion_de_empresa_rechaza_postulacion_inexistente(self):
        self.job_applications.find_by_id.return_value = None
        with self.assertRaisesRegex(ValueError, "Postulación no encontrada"):
            self.service.finish(EMPRESA_ID, PRACTICA_ID)
        self.job_postings.find_by_id.assert_not_called()

    def test_operacion_de_empresa_rechaza_convocatoria_inexistente(self):
        self.job_postings.find_by_id.return_value = None
        with self.assertRaisesRegex(ValueError, "Convocatoria no encontrada"):
            self.service.finish(EMPRESA_ID, PRACTICA_ID)

    def test_operacion_de_empresa_rechaza_empresa_ajena(self):
        with self.assertRaisesRegex(ValueError, "no pertenece a esta empresa"):
            self.service.finish(999, PRACTICA_ID)
        self.practicas.save.assert_not_called()

    # Consultas y visibilidad
    def test_lista_practicas_del_practicante(self):
        esperadas = [self.practica]
        self.practicas.find_by_intern_id.return_value = esperadas

        result = self.service.list_for_user(USUARIO_PRACTICANTE_ID)

        self.assertIs(esperadas, result)
        self.practicas.find_by_intern_id.assert_called_once_with(PRACTICANTE_ID)
        self.profiles_repo.find_company_by_user_id.assert_not_called()

    def test_lista_practicas_de_empresa_y_omite_postulaciones_sin_practica(self):
        practica_2 = Practica(id=8, job_application_id=22, intern_id=31)
        self.profiles_repo.find_intern_by_user_id.return_value = None
        self.profiles_repo.find_company_by_user_id.return_value = self.company
        self.practicas.find_by_company_id.return_value = [self.practica, practica_2]

        result = self.service.list_for_user(USUARIO_EMPRESA_ID)

        self.assertEqual([self.practica, practica_2], result)
        self.practicas.find_by_company_id.assert_called_once_with(EMPRESA_ID)

    def test_listar_rechaza_usuario_sin_perfil(self):
        self.profiles_repo.find_intern_by_user_id.return_value = None
        self.profiles_repo.find_company_by_user_id.return_value = None
        with self.assertRaisesRegex(ValueError, "Perfil no encontrado"):
            self.service.list_for_user(999)

    def test_empresa_propietaria_puede_consultar_practica(self):
        self.profiles_repo.find_intern_by_user_id.return_value = None
        self.profiles_repo.find_company_by_user_id.return_value = self.company

        result = self.service.get_for_user(USUARIO_EMPRESA_ID, PRACTICA_ID)

        self.assertIs(self.practica, result)
        self.profiles_repo.find_company_by_user_id.assert_called_once_with(USUARIO_EMPRESA_ID)
        self.job_applications.find_by_id.assert_called_once_with(POSTULACION_ID)

    def test_consulta_visible_rechaza_practica_inexistente(self):
        self.practicas.find_by_id.return_value = None
        with self.assertRaisesRegex(ValueError, "Práctica no encontrada"):
            self.service.get_for_user(USUARIO_PRACTICANTE_ID, PRACTICA_ID)
        self.profiles_repo.find_intern_by_user_id.assert_not_called()

    def test_consulta_rechaza_practicante_ajeno_sin_perfil_de_empresa(self):
        self.profiles_repo.find_intern_by_user_id.return_value = SimpleNamespace(id=999)
        self.profiles_repo.find_company_by_user_id.return_value = None
        with self.assertRaisesRegex(ValueError, "No autorizado"):
            self.service.get_for_user(USUARIO_PRACTICANTE_ID, PRACTICA_ID)

    # Configuración
    def test_requiere_todos_los_repositorios_antes_de_operar(self):
        incomplete_services = (
            PracticaApplicationService(),
            PracticaApplicationService(
                self.practicas, self.profiles_repo, self.job_applications, None
            ),
        )
        for service in incomplete_services:
            with self.subTest(service=service):
                with self.assertRaisesRegex(RuntimeError, "requiere todos sus repositorios"):
                    service.get_for_user(USUARIO_PRACTICANTE_ID, PRACTICA_ID)


if __name__ == "__main__":
    unittest.main()
