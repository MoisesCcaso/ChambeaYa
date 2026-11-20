"""Pruebas unitarias para Parameter Objects (DTOs / Command Objects) en capa de aplicación (Issue #180)."""

import unittest
from unittest.mock import create_autospec

from application.convocatoria_application_service import ConvocatoriaApplicationService
from application.dtos import (
    ActualizarEmpresaDTO,
    ActualizarPracticanteDTO,
    ConvocatoriaCommand,
)
from application.empresa_application_service import EmpresaApplicationService
from application.practicante_application_service import PracticanteApplicationService
from domain.auth.i_usuario_repository import IUsuarioRepository
from domain.auth.usuario import Usuario
from domain.convocatorias.convocatoria import Convocatoria
from domain.convocatorias.i_convocatoria_repository import IConvocatoriaRepository
from domain.perfil.i_empresa_repository import IEmpresaRepository
from domain.perfil.i_practicante_repository import IPracticanteRepository
from domain.perfil.practicante import Practicante


class TestConvocatoriaCommandDTO(unittest.TestCase):
    """Pruebas unitarias del Parameter Object ConvocatoriaCommand."""

    def setUp(self):
        self.mock_repo = create_autospec(IConvocatoriaRepository, instance=True)
        self.service = ConvocatoriaApplicationService(convocatoria_repository=self.mock_repo)

    def test_from_dict_construye_command_tipado(self):
        cmd = ConvocatoriaCommand.from_dict({
            "titulo": "Backend Python",
            "descripcion": "Prácticas Flask",
            "habilidades_requeridas": ["Python", "SQL"],
            "beneficios": ["Remoto"],
        })
        self.assertIsInstance(cmd, ConvocatoriaCommand)
        self.assertEqual(cmd.titulo, "Backend Python")
        self.assertEqual(cmd.descripcion, "Prácticas Flask")
        self.assertEqual(cmd.habilidades_requeridas, ["Python", "SQL"])
        self.assertEqual(cmd.beneficios, ["Remoto"])

    def test_from_dict_retorna_misma_instancia_si_ya_es_command(self):
        cmd = ConvocatoriaCommand(titulo="QA")
        self.assertIs(ConvocatoriaCommand.from_dict(cmd), cmd)

    def test_create_convocatoria_acepta_convocatoria_command(self):
        cmd = ConvocatoriaCommand(
            titulo="Data Engineer",
            descripcion="ETL pipelines",
            habilidades_requeridas=["Python"],
            beneficios=["Certificado"],
        )
        self.mock_repo.save.side_effect = lambda c: c

        resultado = self.service.create_convocatoria(empresa_id=3, data=cmd)

        self.assertEqual(resultado.titulo, "Data Engineer")
        self.assertEqual(resultado.descripcion, "ETL pipelines")
        self.assertEqual(resultado.habilidades_requeridas, ["Python"])
        self.assertEqual(resultado.beneficios, ["Certificado"])

    def test_update_convocatoria_acepta_convocatoria_command(self):
        existente = Convocatoria(
            id=10,
            empresa_id=3,
            titulo="Original",
            descripcion="Desc",
            estado=Convocatoria.ESTADO_BORRADOR,
        )
        self.mock_repo.find_by_id.return_value = existente
        self.mock_repo.save.side_effect = lambda c: c

        cmd = ConvocatoriaCommand(
            titulo="Actualizado con DTO",
            descripcion="Nueva Desc",
            habilidades_requeridas=["Flask"],
            beneficios=["Mentoría"],
        )
        resultado = self.service.update(empresa_id=3, convocatoria_id=10, data=cmd)

        self.assertEqual(resultado.titulo, "Actualizado con DTO")
        self.assertEqual(resultado.habilidades_requeridas, ["Flask"])


class TestPerfilParameterObjectsDTO(unittest.TestCase):
    """Pruebas unitarias de ActualizarPracticanteDTO y ActualizarEmpresaDTO."""

    def setUp(self):
        self.practicante_repo = create_autospec(IPracticanteRepository, instance=True, spec_set=True)
        self.empresa_repo = create_autospec(IEmpresaRepository, instance=True, spec_set=True)
        self.usuario_repo = create_autospec(IUsuarioRepository, instance=True, spec_set=True)
        self.practicante_service = PracticanteApplicationService(
            practicante_repository=self.practicante_repo,
            usuario_repository=self.usuario_repo,
        )
        self.empresa_service = EmpresaApplicationService(
            empresa_repository=self.empresa_repo,
            usuario_repository=self.usuario_repo,
        )

    def test_update_practicante_acepta_dto_tipado(self):
        self.usuario_repo.find_by_id.return_value = Usuario(
            id=10,
            email="alumno@unsa.edu.pe",
            password_hash="h",
            tipo=Usuario.TIPO_PRACTICANTE,
            estado=Usuario.ESTADO_ACTIVO,
        )
        self.practicante_repo.find_practicante_by_user_id.return_value = None
        self.practicante_repo.save_practicante.side_effect = lambda p: p

        dto = ActualizarPracticanteDTO(
            nombres="Omar",
            apellidos="Rivera",
            dni="12345678",
            carnet_universitario="20210001",
            habilidades=["Python", "Clean Architecture"],
            formacion_educativa=["UNSA"],
        )
        practicante = self.practicante_service.update_practicante(10, dto)

        self.assertEqual(practicante.nombres, "Omar")
        self.assertEqual(practicante.apellidos, "Rivera")
        self.assertTrue(practicante.identidad_verificada)
        self.assertEqual(practicante.habilidades, ["Python", "Clean Architecture"])

    def test_actualizar_practicante_dto_distingue_campos_omitidos(self):
        existente = Practicante(
            id=1,
            usuario_id=10,
            nombres="Omar",
            apellidos="Rivera",
            dni="12345678",
            identidad_verificada=True,
        )
        self.usuario_repo.find_by_id.return_value = Usuario(
            id=10,
            email="alumno@unsa.edu.pe",
            password_hash="h",
            tipo=Usuario.TIPO_PRACTICANTE,
            estado=Usuario.ESTADO_ACTIVO,
        )
        self.practicante_repo.find_practicante_by_user_id.return_value = existente
        self.practicante_repo.save_practicante.side_effect = lambda p: p

        dto = ActualizarPracticanteDTO.from_dict({"nombres": "Omar Joaquin", "apellidos": "Rivera"})
        actualizado = self.practicante_service.update_practicante(10, dto)

        self.assertEqual(actualizado.nombres, "Omar Joaquin")
        self.assertEqual(actualizado.dni, "12345678")
        self.assertTrue(actualizado.identidad_verificada)

    def test_update_empresa_acepta_dto_tipado(self):
        self.usuario_repo.find_by_id.return_value = Usuario(
            id=20,
            email="rrhh@empresa.pe",
            password_hash="h",
            tipo=Usuario.TIPO_EMPRESA,
            estado=Usuario.ESTADO_ACTIVO,
        )
        self.empresa_repo.find_empresa_by_user_id.return_value = None
        self.empresa_repo.save_empresa.side_effect = lambda e: e

        dto = ActualizarEmpresaDTO(razon_social="Tech Peru SAC", ruc="20100070970")
        empresa = self.empresa_service.update_empresa(20, dto)

        self.assertEqual(empresa.razon_social, "Tech Peru SAC")
        self.assertEqual(empresa.ruc.numero, "20100070970")
        self.assertTrue(empresa.verificada)


if __name__ == "__main__":
    unittest.main()
