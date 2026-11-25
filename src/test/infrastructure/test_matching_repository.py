"""I-12 - Pruebas del repositorio de matching con SQLite en memoria, sin dobles."""

import unittest

from domain.matching.sugerencia import Sugerencia
from bootstrap.app import create_app
from shared.database import db
from recruitment.infrastructure.models.convocatoria_model import ConvocatoriaModel
from profiles.infrastructure.models.company_model import CompanyModel
from profiles.infrastructure.models.intern_model import InternModel
from frameworks.sqlalchemy_orm.models.sugerencia_model import SugerenciaModel
from identity.infrastructure.models.user_model import UserModel
from infrastructure.sqlalchemy_matching_repository import SqlAlchemyMatchingRepository


class TestMatchingRepository(unittest.TestCase):
    """Verifica guardado, lectura y actualización usando los modelos ORM reales."""

    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.repository = SqlAlchemyMatchingRepository()
        self.intern_id, self.convocatoria_id = self._crear_entidades_relacionadas()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def _crear_entidades_relacionadas(self):
        intern_user = UserModel(
            email="practicante_matching@test.com",
            password_hash="hash_test",
            role="practicante",
            status="activo",
        )
        company_user = UserModel(
            email="empresa_matching@test.com",
            password_hash="hash_test",
            role="empresa",
            status="activo",
        )
        db.session.add_all([intern_user, company_user])
        db.session.flush()

        intern = InternModel(
            user_id=intern_user.id,
            first_names="Ana",
            last_names="Pérez",
            dni="71112233",
        )
        company = CompanyModel(
            user_id=company_user.id,
            legal_name="Empresa Matching",
            ruc="20111222333",
            verified=True,
        )
        db.session.add_all([intern, company])
        db.session.flush()

        convocatoria = ConvocatoriaModel(
            company_id=company.id,
            titulo="Prácticas de desarrollo",
            status="publicada",
        )
        db.session.add(convocatoria)
        db.session.commit()
        return intern.id, convocatoria.id

    def _crear_sugerencia(self, puntaje=75.0, skills=None, sugerencia_id=None):
        return Sugerencia(
            id=sugerencia_id,
            intern_id=self.intern_id,
            convocatoria_id=self.convocatoria_id,
            puntaje_match=puntaje,
            habilidades_coincidentes=skills or ["python", "sql"],
        )

    def test_save_guarda_sugerencia_y_asigna_id(self):
        saved = self.repository.save(self._crear_sugerencia())

        self.assertIsNotNone(saved.id)
        self.assertEqual(self.intern_id, saved.intern_id)
        self.assertEqual(self.convocatoria_id, saved.convocatoria_id)
        self.assertEqual(75.0, saved.puntaje_match)
        self.assertEqual({"python", "sql"}, set(saved.habilidades_coincidentes))
        self.assertEqual(1, SugerenciaModel.query.count())

    def test_find_by_practicante_id_devuelve_sus_sugerencias(self):
        saved = self.repository.save(self._crear_sugerencia())

        encontradas = self.repository.find_by_practicante_id(self.intern_id)

        self.assertEqual(1, len(encontradas))
        self.assertEqual(saved.id, encontradas[0].id)
        self.assertEqual(75.0, encontradas[0].puntaje_match)
        self.assertEqual({"python", "sql"}, set(encontradas[0].habilidades_coincidentes))
        self.assertEqual([], self.repository.find_by_practicante_id(99999))

    def test_save_actualiza_sugerencia_existente(self):
        saved = self.repository.save(self._crear_sugerencia())
        actualizada = self.repository.save(
            self._crear_sugerencia(
                puntaje=100.0,
                skills=["python", "sql", "git"],
                sugerencia_id=saved.id,
            )
        )

        self.assertEqual(saved.id, actualizada.id)
        self.assertEqual(100.0, actualizada.puntaje_match)
        self.assertEqual({"python", "sql", "git"}, set(actualizada.habilidades_coincidentes))
        self.assertEqual(1, SugerenciaModel.query.count())

        reloaded = self.repository.find_by_practicante_id(self.intern_id)[0]
        self.assertEqual(100.0, reloaded.puntaje_match)
        self.assertEqual({"python", "sql", "git"}, set(reloaded.habilidades_coincidentes))

    def test_save_mismo_par_practicante_convocatoria_no_crea_duplicado(self):
        primera = self.repository.save(self._crear_sugerencia())
        segunda = self.repository.save(
            self._crear_sugerencia(puntaje=50.0, skills=["python"])
        )

        self.assertEqual(primera.id, segunda.id)
        self.assertEqual(50.0, segunda.puntaje_match)
        self.assertEqual(["python"], segunda.habilidades_coincidentes)
        self.assertEqual(1, SugerenciaModel.query.count())


if __name__ == "__main__":
    unittest.main()
