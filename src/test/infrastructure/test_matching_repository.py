"""I-12 - Pruebas del repositorio de matching con SQLite en memoria, sin dobles."""

import unittest

from domain.matching.sugerencia import Sugerencia
from frameworks.flask_mvc.app import create_app
from frameworks.sqlalchemy_orm.database import db
from frameworks.sqlalchemy_orm.models.convocatoria_model import ConvocatoriaModel
from frameworks.sqlalchemy_orm.models.empresa_model import EmpresaModel
from frameworks.sqlalchemy_orm.models.practicante_model import PracticanteModel
from frameworks.sqlalchemy_orm.models.sugerencia_model import SugerenciaModel
from frameworks.sqlalchemy_orm.models.usuario_model import UsuarioModel
from infrastructure.sqlalchemy_matching_repository import SqlAlchemyMatchingRepository


class TestMatchingRepository(unittest.TestCase):
    """Verifica guardado, lectura y actualización usando los modelos ORM reales."""

    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.repository = SqlAlchemyMatchingRepository()
        self.practicante_id, self.convocatoria_id = self._crear_entidades_relacionadas()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def _crear_entidades_relacionadas(self):
        usuario_practicante = UsuarioModel(
            email="practicante_matching@test.com",
            password_hash="hash_test",
            tipo="practicante",
            estado="activo",
        )
        usuario_empresa = UsuarioModel(
            email="empresa_matching@test.com",
            password_hash="hash_test",
            tipo="empresa",
            estado="activo",
        )
        db.session.add_all([usuario_practicante, usuario_empresa])
        db.session.flush()

        practicante = PracticanteModel(
            usuario_id=usuario_practicante.id,
            nombres="Ana",
            apellidos="Pérez",
            dni="71112233",
        )
        empresa = EmpresaModel(
            usuario_id=usuario_empresa.id,
            razon_social="Empresa Matching",
            ruc="20111222333",
            verificada=True,
        )
        db.session.add_all([practicante, empresa])
        db.session.flush()

        convocatoria = ConvocatoriaModel(
            empresa_id=empresa.id,
            titulo="Prácticas de desarrollo",
            estado="publicada",
        )
        db.session.add(convocatoria)
        db.session.commit()
        return practicante.id, convocatoria.id

    def _crear_sugerencia(self, puntaje=75.0, habilidades=None, sugerencia_id=None):
        return Sugerencia(
            id=sugerencia_id,
            practicante_id=self.practicante_id,
            convocatoria_id=self.convocatoria_id,
            puntaje_match=puntaje,
            habilidades_coincidentes=habilidades or ["python", "sql"],
        )

    def test_save_guarda_sugerencia_y_asigna_id(self):
        guardada = self.repository.save(self._crear_sugerencia())

        self.assertIsNotNone(guardada.id)
        self.assertEqual(self.practicante_id, guardada.practicante_id)
        self.assertEqual(self.convocatoria_id, guardada.convocatoria_id)
        self.assertEqual(75.0, guardada.puntaje_match)
        self.assertEqual({"python", "sql"}, set(guardada.habilidades_coincidentes))
        self.assertEqual(1, SugerenciaModel.query.count())

    def test_find_by_practicante_id_devuelve_sus_sugerencias(self):
        guardada = self.repository.save(self._crear_sugerencia())

        encontradas = self.repository.find_by_practicante_id(self.practicante_id)

        self.assertEqual(1, len(encontradas))
        self.assertEqual(guardada.id, encontradas[0].id)
        self.assertEqual(75.0, encontradas[0].puntaje_match)
        self.assertEqual({"python", "sql"}, set(encontradas[0].habilidades_coincidentes))
        self.assertEqual([], self.repository.find_by_practicante_id(99999))

    def test_save_actualiza_sugerencia_existente(self):
        guardada = self.repository.save(self._crear_sugerencia())
        actualizada = self.repository.save(
            self._crear_sugerencia(
                puntaje=100.0,
                habilidades=["python", "sql", "git"],
                sugerencia_id=guardada.id,
            )
        )

        self.assertEqual(guardada.id, actualizada.id)
        self.assertEqual(100.0, actualizada.puntaje_match)
        self.assertEqual({"python", "sql", "git"}, set(actualizada.habilidades_coincidentes))
        self.assertEqual(1, SugerenciaModel.query.count())

        recuperada = self.repository.find_by_practicante_id(self.practicante_id)[0]
        self.assertEqual(100.0, recuperada.puntaje_match)
        self.assertEqual({"python", "sql", "git"}, set(recuperada.habilidades_coincidentes))

    def test_save_mismo_par_practicante_convocatoria_no_crea_duplicado(self):
        primera = self.repository.save(self._crear_sugerencia())
        segunda = self.repository.save(
            self._crear_sugerencia(puntaje=50.0, habilidades=["python"])
        )

        self.assertEqual(primera.id, segunda.id)
        self.assertEqual(50.0, segunda.puntaje_match)
        self.assertEqual(["python"], segunda.habilidades_coincidentes)
        self.assertEqual(1, SugerenciaModel.query.count())


if __name__ == "__main__":
    unittest.main()
