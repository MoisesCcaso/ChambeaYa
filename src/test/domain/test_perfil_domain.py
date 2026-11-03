"""I-04 - Pruebas unitarias de las reglas del dominio de perfil.

Código bajo prueba:
- src/main/domain/perfil/practicante.py
- src/main/domain/perfil/empresa.py
- src/main/domain/perfil/ruc.py
- src/main/domain/perfil/nombre_completo.py
"""

import unittest

from domain.perfil.empresa import Empresa
from domain.perfil.nombre_completo import NombreCompleto
from domain.perfil.practicante import Practicante
from domain.perfil.ruc import RUC


class PracticanteTest(unittest.TestCase):
    def test_verificar_identidad_acepta_dni_de_exactamente_8_digitos(self):
        practicante = Practicante(dni="71234567")

        resultado = practicante.verificar_identidad()

        self.assertIs(resultado, practicante)
        self.assertTrue(practicante.identidad_verificada)

    def test_verificar_identidad_rechaza_dni_con_longitud_distinta_o_no_numerico(self):
        dnis_invalidos = ("1234567", "123456789", "1234567A", "abcdefgh")

        for dni in dnis_invalidos:
            with self.subTest(dni=dni):
                practicante = Practicante(dni=dni)
                with self.assertRaisesRegex(
                    ValueError, "El DNI debe contener exactamente 8 dígitos"
                ):
                    practicante.verificar_identidad()
                self.assertFalse(practicante.identidad_verificada)

    def test_verificar_identidad_acepta_carnet_recortado_de_al_menos_4_caracteres(self):
        practicante = Practicante(carnet_universitario="  A123  ")

        resultado = practicante.verificar_identidad()

        self.assertIs(resultado, practicante)
        self.assertTrue(practicante.identidad_verificada)

    def test_verificar_identidad_rechaza_carnet_recortado_menor_a_4_caracteres(self):
        carnets_invalidos = ("123", "  AB1  ", "   x   ")

        for carnet in carnets_invalidos:
            with self.subTest(carnet=carnet):
                practicante = Practicante(carnet_universitario=carnet)
                with self.assertRaisesRegex(
                    ValueError, "El carnet universitario no es válido"
                ):
                    practicante.verificar_identidad()
                self.assertFalse(practicante.identidad_verificada)

    def test_verificar_identidad_rechaza_cuando_faltan_dni_y_carnet(self):
        practicante = Practicante()

        with self.assertRaisesRegex(
            ValueError, "Se requiere DNI o carnet universitario"
        ):
            practicante.verificar_identidad()

    def test_calcular_score_suma_habilidades_formacion_identidad_y_respeta_topes(self):
        # Sin habilidades, formación ni identidad verificada -> 0.0
        vacio = Practicante()
        self.assertEqual(vacio.calcular_score(), 0.0)
        self.assertEqual(vacio.score_reputacion, 0.0)

        # 3 habilidades (15) + 2 formaciones (10) + identidad verificada (25) = 50.0
        parcial = Practicante(
            habilidades=["Python", "SQL", "Git"],
            formacion_educativa=["UNSA", "Inglés"],
            identidad_verificada=True,
        )
        self.assertEqual(parcial.calcular_score(), 50.0)
        self.assertEqual(parcial.score_reputacion, 50.0)

        # Tope de habilidades: hasta 10 (12 habilidades -> cuenta 10 * 5 = 50.0)
        tope_habilidades = Practicante(
            habilidades=[f"Habilidad {i}" for i in range(12)],
            identidad_verificada=False,
        )
        self.assertEqual(tope_habilidades.calcular_score(), 50.0)

        # Tope de formación: hasta 5 (7 formaciones -> cuenta 5 * 5 = 25.0)
        tope_formacion = Practicante(
            formacion_educativa=[f"Formacion {i}" for i in range(7)],
            identidad_verificada=False,
        )
        self.assertEqual(tope_formacion.calcular_score(), 25.0)

        # Tope total 100: 10 habs (50) + 5 formaciones (25) + verificada (25) = 100.0
        maximo = Practicante(
            habilidades=[f"Habilidad {i}" for i in range(15)],
            formacion_educativa=[f"Formacion {i}" for i in range(8)],
            identidad_verificada=True,
        )
        self.assertEqual(maximo.calcular_score(), 100.0)
        self.assertEqual(maximo.score_reputacion, 100.0)

    def test_actualizar_datos_modifica_solo_campos_provistos(self):
        practicante = Practicante(
            nombres="Juan",
            apellidos="Pérez",
            dni="70000001",
            carnet_universitario="20201234",
        )

        resultado = practicante.actualizar_datos(
            nombres="Carlos",
            apellidos="Gómez",
            dni="70000002",
            carnet_universitario="20209999",
        )

        self.assertIs(resultado, practicante)
        self.assertEqual(practicante.nombres, "Carlos")
        self.assertEqual(practicante.apellidos, "Gómez")
        self.assertEqual(practicante.dni, "70000002")
        self.assertEqual(practicante.carnet_universitario, "20209999")

        practicante.actualizar_datos()
        self.assertEqual(practicante.nombres, "Carlos")

    def test_agregar_y_reemplazar_habilidades_y_formacion_normaliza_y_evita_duplicados(self):
        practicante = Practicante()

        practicante.agregar_habilidad("  Python  ")
        practicante.agregar_habilidad("Python")
        practicante.agregar_habilidad("   ")
        practicante.agregar_habilidad(None)
        self.assertEqual(practicante.habilidades, ["Python"])

        practicante.agregar_formacion("  Ingeniería de Software  ")
        practicante.agregar_formacion("Ingeniería de Software")
        practicante.agregar_formacion("")
        practicante.agregar_formacion(None)
        self.assertEqual(practicante.formacion_educativa, ["Ingeniería de Software"])

        practicante.reemplazar_habilidades([" Flask ", "SQL", "Flask"])
        self.assertEqual(practicante.habilidades, ["Flask", "SQL"])

        practicante.reemplazar_formacion([" UNSA ", "Certificación AWS", "UNSA"])
        self.assertEqual(practicante.formacion_educativa, ["UNSA", "Certificación AWS"])

    def test_reemplazar_habilidades_y_formacion_rechaza_valores_que_no_son_lista(self):
        practicante = Practicante()

        with self.assertRaisesRegex(ValueError, "Las habilidades deben ser una lista"):
            practicante.reemplazar_habilidades("Python")

        with self.assertRaisesRegex(
            ValueError, "La formación educativa debe ser una lista"
        ):
            practicante.reemplazar_formacion(("UNSA",))


class RucYEmpresaTest(unittest.TestCase):
    def test_ruc_valido_segun_prefijo_y_digito_verificador(self):
        # Cubre prefijos 10, 15, 17, 20 y ramas del módulo 11 (10->0, 11->1 y resto normal)
        rucs_validos = (
            "20100070970",  # 11 - resto == 10 -> dígito 0
            "20100090971",  # 11 - resto == 11 -> dígito 1
            "20100070988",  # 11 - resto == 8  -> dígito 8
            "10100070974",  # prefijo 10 válido
            "15100070976",  # prefijo 15 válido
            "17100070979",  # prefijo 17 válido
        )

        for numero in rucs_validos:
            with self.subTest(ruc=numero):
                self.assertTrue(RUC(numero).es_valido())

    def test_ruc_invalido_por_formato_prefijo_o_digito_verificador(self):
        rucs_invalidos = (
            None,
            "",
            12345678901,
            "2010007097",    # 10 dígitos
            "201000709701",  # 12 dígitos
            "2010007097A",   # no numérico
            "11100070971",   # prefijo 11 inválido
            "99100070970",   # prefijo 99 inválido
            "20100070975",   # dígito verificador incorrecto
            "10100070970",   # dígito verificador incorrecto
        )

        for numero in rucs_invalidos:
            with self.subTest(ruc=numero):
                self.assertFalse(RUC(numero).es_valido())

    def test_empresa_verificar_ruc_actualiza_bandera_verificada(self):
        empresa_valida = Empresa(
            razon_social="Tech SAC",
            ruc=RUC("20100070970"),
        )
        self.assertTrue(empresa_valida.verificar_ruc())
        self.assertTrue(empresa_valida.verificada)

        empresa_ruc_invalido = Empresa(
            razon_social="Tech SAC",
            ruc=RUC("20100070975"),
            verificada=True,
        )
        self.assertFalse(empresa_ruc_invalido.verificar_ruc())
        self.assertFalse(empresa_ruc_invalido.verificada)

        empresa_sin_ruc = Empresa(razon_social="Sin RUC", ruc=None, verificada=True)
        self.assertFalse(empresa_sin_ruc.verificar_ruc())
        self.assertFalse(empresa_sin_ruc.verificada)


class NombreCompletoTest(unittest.TestCase):
    def test_validar_recorta_ambos_campos_y_formatea_cadena(self):
        nombre = NombreCompleto(nombres="  Ana María  ", apellidos="  Torres Díaz  ")

        resultado = nombre.validar()

        self.assertIs(resultado, nombre)
        self.assertEqual(nombre.nombres, "Ana María")
        self.assertEqual(nombre.apellidos, "Torres Díaz")
        self.assertEqual(str(nombre), "Ana María Torres Díaz")

    def test_validar_rechaza_nombre_o_apellido_faltante_o_en_blanco(self):
        casos_invalidos = (
            (None, "Torres"),
            ("", "Torres"),
            ("   ", "Torres"),
            ("Ana", None),
            ("Ana", ""),
            ("Ana", "   "),
            (None, None),
        )

        for nombres, apellidos in casos_invalidos:
            with self.subTest(nombres=nombres, apellidos=apellidos):
                nombre = NombreCompleto(nombres=nombres, apellidos=apellidos)
                with self.assertRaisesRegex(
                    ValueError, "Nombres y apellidos son obligatorios"
                ):
                    nombre.validar()


if __name__ == "__main__":
    unittest.main()
