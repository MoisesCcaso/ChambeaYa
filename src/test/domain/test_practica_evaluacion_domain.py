"""Pruebas unitarias del dominio de prácticas, entregables y evaluaciones."""

import unittest
from datetime import datetime, timedelta, timezone

from domain.practica_evaluacion.entregable import Entregable
from domain.practica_evaluacion.evaluacion import Evaluacion
from domain.practica_evaluacion.practica import Practica
from domain.practica_evaluacion.practica_fabrica import PracticaFabrica


class TestPracticaFabrica(unittest.TestCase):
    def test_inicia_practica_en_curso_y_sin_registros(self):
        practica = PracticaFabrica().iniciar_practica(11, 22)
        self.assertEqual(practica.postulacion_id, 11)
        self.assertEqual(practica.practicante_id, 22)
        self.assertEqual(practica.estado, Practica.ESTADO_EN_CURSO)
        self.assertEqual(practica.entregables, [])
        self.assertEqual(practica.evaluaciones, [])

    def test_rechaza_datos_requeridos_ausentes(self):
        for postulacion_id, practicante_id in ((None, 22), (11, None), (None, None)):
            with self.subTest(postulacion_id=postulacion_id, practicante_id=practicante_id):
                with self.assertRaisesRegex(ValueError, "postulación y practicante"):
                    PracticaFabrica().iniciar_practica(postulacion_id, practicante_id)


class TestEntregable(unittest.TestCase):
    def test_crear_normaliza_archivo_y_registra_fecha(self):
        entregable = Entregable.crear(7, "  informe-final.pdf  ")
        self.assertEqual(entregable.practica_id, 7)
        self.assertEqual(entregable.archivo, "informe-final.pdf")
        self.assertEqual(entregable.fecha_subida.tzinfo, timezone.utc)

    def test_rechaza_archivo_vacio(self):
        for archivo in (None, "", "   "):
            with self.subTest(archivo=archivo):
                with self.assertRaisesRegex(ValueError, "Debe adjuntarse un archivo"):
                    Entregable.crear(7, archivo)


class TestEvaluacion(unittest.TestCase):
    def test_acepta_puntajes_validos_y_los_convierte_a_float(self):
        for puntaje, esperado in ((0, 0.0), ("59.5", 59.5), (60, 60.0), (100, 100.0)):
            with self.subTest(puntaje=puntaje):
                evaluacion = Evaluacion.crear(7, puntaje)
                self.assertEqual(evaluacion.practica_id, 7)
                self.assertEqual(evaluacion.puntaje, esperado)
                self.assertEqual(evaluacion.fecha_evaluacion.tzinfo, timezone.utc)

    def test_rechaza_puntajes_fuera_del_rango(self):
        for puntaje in (-0.01, 100.01):
            with self.subTest(puntaje=puntaje):
                with self.assertRaisesRegex(ValueError, "entre 0 y 100"):
                    Evaluacion.crear(7, puntaje)

    def test_rechaza_puntaje_ausente(self):
        with self.assertRaisesRegex(ValueError, "Debe indicarse un puntaje"):
            Evaluacion.crear(7, None)

    def test_rechaza_puntaje_no_numerico(self):
        for puntaje in ("no-numérico", object()):
            with self.subTest(puntaje=puntaje):
                with self.assertRaisesRegex(ValueError, "debe ser numérico"):
                    Evaluacion.crear(7, puntaje)

    def test_aprueba_desde_sesenta_puntos(self):
        for puntaje, esperado in ((None, False), (59.99, False), (60, True), (100, True)):
            with self.subTest(puntaje=puntaje):
                self.assertIs(Evaluacion(puntaje=puntaje).esta_aprobada(), esperado)


class TestPractica(unittest.TestCase):
    def test_subir_entregable_lo_agrega_a_la_practica(self):
        practica = Practica(id=7)
        entregable = practica.subir_entregable("informe.pdf")
        self.assertEqual(entregable.practica_id, 7)
        self.assertEqual(practica.entregables, [entregable])

    def test_registrar_evaluacion_la_agrega_a_la_practica(self):
        practica = Practica(id=7)
        evaluacion = practica.registrar_evaluacion(85)
        self.assertEqual(evaluacion.practica_id, 7)
        self.assertEqual(evaluacion.puntaje, 85.0)
        self.assertEqual(practica.evaluaciones, [evaluacion])

    def test_no_se_puede_finalizar_sin_entregables(self):
        practica = Practica(id=7)
        practica.registrar_evaluacion(80)
        with self.assertRaisesRegex(ValueError, "sin entregables registrados"):
            practica.finalizar()
        self.assertEqual(practica.estado, Practica.ESTADO_EN_CURSO)

    def test_no_se_puede_finalizar_sin_evaluacion_aprobada(self):
        practica = Practica(id=7)
        practica.subir_entregable("informe.pdf")
        practica.registrar_evaluacion(59)
        with self.assertRaisesRegex(ValueError, "sin una evaluación aprobada"):
            practica.finalizar()
        self.assertEqual(practica.estado, Practica.ESTADO_EN_CURSO)

    def test_finalizar_cambia_el_estado_si_cumple_las_reglas(self):
        practica = Practica(id=7)
        practica.subir_entregable("informe.pdf")
        practica.registrar_evaluacion(60)
        self.assertIs(practica.finalizar(), practica)
        self.assertEqual(practica.estado, Practica.ESTADO_FINALIZADA)

    def test_no_se_puede_finalizar_dos_veces(self):
        practica = Practica(
            estado=Practica.ESTADO_FINALIZADA,
            entregables=[Entregable(archivo="informe.pdf")],
            evaluaciones=[Evaluacion(puntaje=90)],
        )
        with self.assertRaisesRegex(ValueError, "ya está finalizada"):
            practica.finalizar()

    def test_finalizada_no_admite_nuevos_entregables_ni_evaluaciones(self):
        practica = Practica(estado=Practica.ESTADO_FINALIZADA)
        with self.assertRaisesRegex(ValueError, "entregables.*finalizada"):
            practica.subir_entregable("otro-informe.pdf")
        with self.assertRaisesRegex(ValueError, "evaluaciones.*finalizada"):
            practica.registrar_evaluacion(90)
        self.assertEqual(practica.entregables, [])
        self.assertEqual(practica.evaluaciones, [])

    def test_eliminar_entregable_existente_en_curso(self):
        entregable = Entregable(id=3, archivo="informe.pdf")
        practica = Practica(entregables=[entregable])
        self.assertIs(practica.eliminar_entregable(3), entregable)
        self.assertEqual(practica.entregables, [])

    def test_eliminar_evaluacion_existente_en_curso(self):
        evaluacion = Evaluacion(id=4, puntaje=80)
        practica = Practica(evaluaciones=[evaluacion])
        self.assertIs(practica.eliminar_evaluacion(4), evaluacion)
        self.assertEqual(practica.evaluaciones, [])

    def test_eliminar_rechaza_un_registro_inexistente(self):
        casos = (
            ("eliminar_entregable", "Entregable no encontrado"),
            ("eliminar_evaluacion", "Evaluación no encontrada"),
        )
        for metodo, mensaje in casos:
            with self.subTest(metodo=metodo):
                with self.assertRaisesRegex(ValueError, mensaje):
                    getattr(Practica(), metodo)(999)

    def test_finalizada_no_admite_eliminaciones(self):
        for metodo in ("eliminar_entregable", "eliminar_evaluacion"):
            with self.subTest(metodo=metodo):
                practica = Practica(estado=Practica.ESTADO_FINALIZADA)
                with self.assertRaisesRegex(ValueError, "práctica finalizada"):
                    getattr(practica, metodo)(1)

    def test_historiales_se_ordenan_sin_alterar_las_colecciones(self):
        ahora = datetime.now(timezone.utc)
        entregable_reciente = Entregable(id=1, fecha_subida=ahora)
        entregable_antiguo = Entregable(id=2, fecha_subida=ahora - timedelta(days=1))
        evaluacion_reciente = Evaluacion(id=1, fecha_evaluacion=ahora)
        evaluacion_antigua = Evaluacion(id=2, fecha_evaluacion=ahora - timedelta(hours=1))
        practica = Practica(
            entregables=[entregable_reciente, entregable_antiguo],
            evaluaciones=[evaluacion_reciente, evaluacion_antigua],
        )

        self.assertEqual(
            practica.obtener_historial_entregables(),
            [entregable_antiguo, entregable_reciente],
        )
        self.assertEqual(
            practica.obtener_historial_evaluaciones(),
            [evaluacion_antigua, evaluacion_reciente],
        )
        self.assertEqual(practica.entregables, [entregable_reciente, entregable_antiguo])
        self.assertEqual(practica.evaluaciones, [evaluacion_reciente, evaluacion_antigua])


if __name__ == "__main__":
    unittest.main()
