import unittest
from unittest.mock import MagicMock

from bootstrap.dependencies import DependencyContainer


class TestDependencyContainer(unittest.TestCase):
    def setUp(self):
        self.container = DependencyContainer()

    def test_container_provides_repositories(self):
        self.assertIsNotNone(self.container.get_user_repository())
        self.assertIsNotNone(self.container.get_profile_repository())
        self.assertIsNotNone(self.container.get_convocatoria_repository())
        self.assertIsNotNone(self.container.get_postulacion_repository())
        self.assertIsNotNone(self.container.get_practica_repository())
        self.assertIsNotNone(self.container.get_certificado_repository())
        self.assertIsNotNone(self.container.get_notification_repository())
        self.assertIsNotNone(self.container.get_matching_repository())

    def test_container_provides_services(self):
        self.assertIsNotNone(self.container.get_user_service())
        self.assertIsNotNone(self.container.get_convocatoria_service())
        self.assertIsNotNone(self.container.get_practica_service())
        self.assertIsNotNone(self.container.get_postulacion_service())
        self.assertIsNotNone(self.container.get_matching_service())
        self.assertIsNotNone(self.container.get_notification_service())
        self.assertIsNotNone(self.container.get_certificacion_service())
        self.assertIsNotNone(self.container.get_intern_service())
        self.assertIsNotNone(self.container.get_company_service())

    def test_container_allows_overriding_repositories(self):
        mock_repo = MagicMock()
        self.container.override_repository("profile", mock_repo)
        self.assertIs(self.container.get_profile_repository(), mock_repo)

        self.container.reset()
        self.assertIsNot(self.container.get_profile_repository(), mock_repo)

    def test_container_allows_overriding_services(self):
        mock_service = MagicMock()
        self.container.override_service("practica_service", mock_service)
        self.assertIs(self.container.get_practica_service(), mock_service)

        self.container.reset()
        self.assertIsNot(self.container.get_practica_service(), mock_service)
