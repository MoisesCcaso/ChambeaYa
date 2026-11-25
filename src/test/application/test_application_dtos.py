"""Pruebas unitarias para Parameter Objects (DTOs / Command Objects) en capa de aplicación (Issue #180)."""

import unittest
from unittest.mock import create_autospec

from application.convocatoria_application_service import ConvocatoriaApplicationService
from application.dtos import (
    ConvocatoriaCommand,
)
from domain.convocatorias.convocatoria import Convocatoria
from domain.convocatorias.i_convocatoria_repository import IConvocatoriaRepository


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

        result = self.service.create_convocatoria(company_id=3, data=cmd)

        self.assertEqual(result.titulo, "Data Engineer")
        self.assertEqual(result.descripcion, "ETL pipelines")
        self.assertEqual(result.habilidades_requeridas, ["Python"])
        self.assertEqual(result.beneficios, ["Certificado"])

    def test_update_convocatoria_acepta_convocatoria_command(self):
        existing = Convocatoria(
            id=10,
            company_id=3,
            titulo="Original",
            descripcion="Desc",
            status=Convocatoria.ESTADO_BORRADOR,
        )
        self.mock_repo.find_by_id.return_value = existing
        self.mock_repo.save.side_effect = lambda c: c

        cmd = ConvocatoriaCommand(
            titulo="Actualizado con DTO",
            descripcion="Nueva Desc",
            habilidades_requeridas=["Flask"],
            beneficios=["Mentoría"],
        )
        result = self.service.update(company_id=3, convocatoria_id=10, data=cmd)

        self.assertEqual(result.titulo, "Actualizado con DTO")
        self.assertEqual(result.habilidades_requeridas, ["Flask"])


if __name__ == "__main__":
    unittest.main()
