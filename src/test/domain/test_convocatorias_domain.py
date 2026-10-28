"""Pruebas unitarias de dominio para Convocatoria, ConvocatoriaFabrica y Postulacion."""

import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from domain.convocatorias.convocatoria import Convocatoria
from domain.convocatorias.convocatoria_fabrica import ConvocatoriaFabrica
from domain.convocatorias.postulacion import Postulacion


class TestConvocatoriaDomain(unittest.TestCase):
    """Pruebas del ciclo de vida y reglas de negocio de Convocatoria."""

    def setUp(self):
        self.convocatoria = Convocatoria(
            id=1,
            empresa_id=10,
            titulo="Practicante Backend Python",
            descripcion="Desarrollo de APIs REST",
            estado=Convocatoria.ESTADO_BORRADOR,
            habilidades_requeridas=["Python", "SQLAlchemy"],
            beneficios=["Seguro", "Remoto"],
        )

    def test_publicar_desde_borrador_asigna_estado_y_fecha_utc(self):
        fecha_fija = datetime(2026, 10, 28, 12, 0, 0, tzinfo=timezone.utc)
        with patch("domain.convocatorias.convocatoria.datetime") as mock_dt:
            mock_dt.now.return_value = fecha_fija
            resultado = self.convocatoria.publicar()

        self.assertIs(resultado, self.convocatoria)
        self.assertEqual(self.convocatoria.estado, Convocatoria.ESTADO_PUBLICADA)
        self.assertEqual(self.convocatoria.fecha_publicacion, fecha_fija)

    def test_publicar_desde_estado_no_borrador_lanza_error(self):
        self.convocatoria.estado = Convocatoria.ESTADO_PUBLICADA
        with self.assertRaises(ValueError) as ctx:
            self.convocatoria.publicar()
        self.assertIn("Solo una convocatoria en borrador puede publicarse", str(ctx.exception))

        self.convocatoria.estado = Convocatoria.ESTADO_CERRADA
        with self.assertRaises(ValueError):
            self.convocatoria.publicar()

    def test_cerrar_desde_publicada_asigna_estado_y_fecha_cierre(self):
        self.convocatoria.estado = Convocatoria.ESTADO_PUBLICADA
        fecha_cierre = datetime(2026, 11, 1, 18, 0, 0, tzinfo=timezone.utc)
        with patch("domain.convocatorias.convocatoria.datetime") as mock_dt:
            mock_dt.now.return_value = fecha_cierre
            resultado = self.convocatoria.cerrar()

        self.assertIs(resultado, self.convocatoria)
        self.assertEqual(self.convocatoria.estado, Convocatoria.ESTADO_CERRADA)
        self.assertEqual(self.convocatoria.fecha_cierre, fecha_cierre)

    def test_cerrar_desde_estado_no_publicada_lanza_error(self):
        self.convocatoria.estado = Convocatoria.ESTADO_BORRADOR
        with self.assertRaises(ValueError) as ctx:
            self.convocatoria.cerrar()
        self.assertIn("Solo una convocatoria publicada puede cerrarse", str(ctx.exception))

        self.convocatoria.estado = Convocatoria.ESTADO_CERRADA
        with self.assertRaises(ValueError):
            self.convocatoria.cerrar()

    def test_reabrir_desde_cerrada_asigna_estado_publicada_y_limpia_cierre(self):
        self.convocatoria.estado = Convocatoria.ESTADO_CERRADA
        self.convocatoria.fecha_cierre = datetime(2026, 11, 1, tzinfo=timezone.utc)
        fecha_reapertura = datetime(2026, 11, 5, 10, 0, 0, tzinfo=timezone.utc)

        with patch("domain.convocatorias.convocatoria.datetime") as mock_dt:
            mock_dt.now.return_value = fecha_reapertura
            resultado = self.convocatoria.reabrir()

        self.assertIs(resultado, self.convocatoria)
        self.assertEqual(self.convocatoria.estado, Convocatoria.ESTADO_PUBLICADA)
        self.assertEqual(self.convocatoria.fecha_publicacion, fecha_reapertura)
        self.assertIsNone(self.convocatoria.fecha_cierre)

    def test_reabrir_desde_estado_no_cerrada_lanza_error(self):
        self.convocatoria.estado = Convocatoria.ESTADO_BORRADOR
        with self.assertRaises(ValueError) as ctx:
            self.convocatoria.reabrir()
        self.assertIn("Solo una convocatoria cerrada puede reabrirse", str(ctx.exception))

        self.convocatoria.estado = Convocatoria.ESTADO_PUBLICADA
        with self.assertRaises(ValueError):
            self.convocatoria.reabrir()

    def test_actualizar_en_borrador_modifica_campos_y_normaliza_textos(self):
        resultado = self.convocatoria.actualizar(
            titulo="  Nuevo Título Backend  ",
            descripcion="  Nueva descripción  ",
            habilidades_requeridas=["  Python  ", "Docker", "Python"],
            beneficios=["  Home Office  ", "Bono", None],
        )

        self.assertIs(resultado, self.convocatoria)
        self.assertEqual(self.convocatoria.titulo, "Nuevo Título Backend")
        self.assertEqual(self.convocatoria.descripcion, "Nueva descripción")
        self.assertEqual(self.convocatoria.habilidades_requeridas, ["Python", "Docker"])
        self.assertEqual(self.convocatoria.beneficios, ["Home Office", "Bono"])

    def test_actualizar_en_estado_no_borrador_lanza_error(self):
        self.convocatoria.estado = Convocatoria.ESTADO_PUBLICADA
        with self.assertRaises(ValueError) as ctx:
            self.convocatoria.actualizar(titulo="Intento")
        self.assertIn("Solo una convocatoria en borrador puede editarse", str(ctx.exception))

    def test_actualizar_con_titulo_vacio_lanza_error(self):
        with self.assertRaises(ValueError) as ctx:
            self.convocatoria.actualizar(titulo="   ")
        self.assertIn("El título es obligatorio", str(ctx.exception))

    def test_actualizar_con_listas_no_validas_lanza_error(self):
        with self.assertRaises(ValueError) as ctx:
            self.convocatoria.actualizar(habilidades_requeridas="no es lista")
        self.assertIn("Las habilidades requeridas deben ser una lista", str(ctx.exception))

        with self.assertRaises(ValueError) as ctx2:
            self.convocatoria.actualizar(beneficios="no es lista")
        self.assertIn("Los beneficios deben ser una lista", str(ctx2.exception))

    def test_validar_eliminacion_en_borrador_retorna_self(self):
        self.convocatoria.estado = Convocatoria.ESTADO_BORRADOR
        self.assertIs(self.convocatoria.validar_eliminacion(), self.convocatoria)

    def test_validar_eliminacion_en_no_borrador_lanza_error(self):
        for estado in [Convocatoria.ESTADO_PUBLICADA, Convocatoria.ESTADO_CERRADA]:
            self.convocatoria.estado = estado
            with self.assertRaises(ValueError) as ctx:
                self.convocatoria.validar_eliminacion()
            self.assertIn("Solo una convocatoria en borrador puede eliminarse", str(ctx.exception))


class TestConvocatoriaFabrica(unittest.TestCase):
    """Pruebas de la factoría ConvocatoriaFabrica."""

    def setUp(self):
        self.fabrica = ConvocatoriaFabrica()

    def test_crear_convocatoria_con_datos_validos(self):
        convocatoria = self.fabrica.crear_convocatoria(
            empresa_id=42,
            titulo="  Practicante Fullstack  ",
            habilidades_requeridas=[" React ", " Node "],
            descripcion="  Búsqueda de practicante proactivo  ",
            beneficios=["  Almuerzo  "],
        )

        self.assertEqual(convocatoria.empresa_id, 42)
        self.assertEqual(convocatoria.titulo, "Practicante Fullstack")
        self.assertEqual(convocatoria.descripcion, "Búsqueda de practicante proactivo")
        self.assertEqual(convocatoria.estado, Convocatoria.ESTADO_BORRADOR)
        self.assertEqual(convocatoria.habilidades_requeridas, ["React", "Node"])
        self.assertEqual(convocatoria.beneficios, ["Almuerzo"])

    def test_crear_convocatoria_sin_empresa_lanza_error(self):
        with self.assertRaises(ValueError) as ctx:
            self.fabrica.crear_convocatoria(empresa_id=None, titulo="Titulo Valido")
        self.assertIn("La empresa es obligatoria", str(ctx.exception))

    def test_crear_convocatoria_sin_titulo_o_vacio_lanza_error(self):
        with self.assertRaises(ValueError) as ctx:
            self.fabrica.crear_convocatoria(empresa_id=1, titulo="   ")
        self.assertIn("El título es obligatorio", str(ctx.exception))

    def test_crear_convocatoria_con_tipos_invalidos_en_listas_lanza_error(self):
        with self.assertRaises(ValueError) as ctx:
            self.fabrica.crear_convocatoria(
                empresa_id=1, titulo="Valido", habilidades_requeridas="string_no_lista"
            )
        self.assertIn("Las habilidades requeridas deben ser una lista", str(ctx.exception))

        with self.assertRaises(ValueError) as ctx2:
            self.fabrica.crear_convocatoria(
                empresa_id=1, titulo="Valido", beneficios="string_no_lista"
            )
        self.assertIn("Los beneficios deben ser una lista", str(ctx2.exception))


class TestPostulacionDomain(unittest.TestCase):
    """Pruebas del ciclo de vida y reglas de negocio de Postulacion."""

    def setUp(self):
        self.postulacion = Postulacion(
            id=10,
            convocatoria_id=100,
            practicante_id=200,
            estado=Postulacion.ESTADO_PENDIENTE,
        )

    def test_estado_inicial_por_defecto_es_pendiente(self):
        postulacion = Postulacion(id=1, convocatoria_id=2, practicante_id=3)
        self.assertEqual(postulacion.estado, Postulacion.ESTADO_PENDIENTE)

    def test_seleccionar_desde_pendiente_cambia_a_seleccionada(self):
        resultado = self.postulacion.seleccionar()
        self.assertIs(resultado, self.postulacion)
        self.assertEqual(self.postulacion.estado, Postulacion.ESTADO_SELECCIONADA)

    def test_aceptar_como_alias_de_seleccionar(self):
        resultado = self.postulacion.aceptar()
        self.assertIs(resultado, self.postulacion)
        self.assertEqual(self.postulacion.estado, Postulacion.ESTADO_SELECCIONADA)

    def test_rechazar_desde_pendiente_cambia_a_rechazada(self):
        resultado = self.postulacion.rechazar()
        self.assertIs(resultado, self.postulacion)
        self.assertEqual(self.postulacion.estado, Postulacion.ESTADO_RECHAZADA)

    def test_cancelar_desde_pendiente_cambia_a_cancelada(self):
        resultado = self.postulacion.cancelar()
        self.assertIs(resultado, self.postulacion)
        self.assertEqual(self.postulacion.estado, Postulacion.ESTADO_CANCELADA)

    def test_reactivar_desde_cancelada_cambia_a_pendiente(self):
        self.postulacion.estado = Postulacion.ESTADO_CANCELADA
        resultado = self.postulacion.reactivar()
        self.assertIs(resultado, self.postulacion)
        self.assertEqual(self.postulacion.estado, Postulacion.ESTADO_PENDIENTE)

    def test_reactivar_desde_estado_no_cancelada_lanza_error(self):
        for estado in [Postulacion.ESTADO_PENDIENTE, Postulacion.ESTADO_SELECCIONADA, Postulacion.ESTADO_RECHAZADA]:
            self.postulacion.estado = estado
            with self.assertRaises(ValueError) as ctx:
                self.postulacion.reactivar()
            self.assertIn("Solo una postulación retirada puede reactivarse", str(ctx.exception))

    def test_reconsiderar_desde_seleccionada_o_rechazada_cambia_a_pendiente(self):
        for estado in [Postulacion.ESTADO_SELECCIONADA, Postulacion.ESTADO_RECHAZADA]:
            self.postulacion.estado = estado
            resultado = self.postulacion.reconsiderar()
            self.assertIs(resultado, self.postulacion)
            self.assertEqual(self.postulacion.estado, Postulacion.ESTADO_PENDIENTE)

    def test_reconsiderar_desde_estado_invalido_lanza_error(self):
        for estado in [Postulacion.ESTADO_PENDIENTE, Postulacion.ESTADO_CANCELADA]:
            self.postulacion.estado = estado
            with self.assertRaises(ValueError) as ctx:
                self.postulacion.reconsiderar()
            self.assertIn("Solo una postulación seleccionada o rechazada puede reconsiderarse", str(ctx.exception))

    def test_transiciones_invalidas_desde_no_pendiente_lanzan_error(self):
        estados_no_pendientes = [
            Postulacion.ESTADO_SELECCIONADA,
            Postulacion.ESTADO_RECHAZADA,
            Postulacion.ESTADO_CANCELADA,
        ]
        for estado in estados_no_pendientes:
            self.postulacion.estado = estado
            with self.assertRaises(ValueError):
                self.postulacion.seleccionar()
            with self.assertRaises(ValueError):
                self.postulacion.rechazar()
            with self.assertRaises(ValueError):
                self.postulacion.cancelar()
