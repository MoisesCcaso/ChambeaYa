"""Pruebas unitarias de persistencia y consultas para SqlAlchemyConvocatoriaRepository."""

import unittest
from datetime import datetime, timezone

from domain.convocatorias.convocatoria import Convocatoria
from frameworks.flask_mvc.app import create_app
from frameworks.sqlalchemy_orm.database import db
from frameworks.sqlalchemy_orm.models.empresa_model import EmpresaModel
from frameworks.sqlalchemy_orm.models.usuario_model import UsuarioModel
from infrastructure.sqlalchemy_convocatoria_repository import SqlAlchemyConvocatoriaRepository


class TestConvocatoriaRepository(unittest.TestCase):
    """Pruebas del repositorio de convocatorias con SQLite en memoria sin dobles."""

    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.repository = SqlAlchemyConvocatoriaRepository()

        # Crear empresas base para cumplir con la integridad referencial (FK)
        self.empresa_1 = self._crear_empresa_en_db(email="empresa1@test.com", ruc="20123456789")
        self.empresa_2 = self._crear_empresa_en_db(email="empresa2@test.com", ruc="20987654321")

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def _crear_empresa_en_db(self, email, ruc):
        usuario = UsuarioModel(
            email=email,
            password_hash="hash_test",
            tipo="empresa",
            estado="activo",
        )
        db.session.add(usuario)
        db.session.flush()

        empresa = EmpresaModel(
            usuario_id=usuario.id,
            razon_social="Empresa Test",
            ruc=ruc,
            verificada=True,
        )
        db.session.add(empresa)
        db.session.commit()
        return empresa

    def test_save_crea_nueva_convocatoria_y_asigna_id(self):
        convocatoria = Convocatoria(
            empresa_id=self.empresa_1.id,
            titulo="Practicante Python",
            descripcion="Desarrollo backend con Flask",
            estado=Convocatoria.ESTADO_BORRADOR,
            habilidades_requeridas=["Python", "SQLAlchemy"],
            beneficios=["Seguro", "Remoto"],
            fecha_publicacion=None,
            fecha_cierre=None,
        )

        guardada = self.repository.save(convocatoria)

        self.assertIsNotNone(guardada.id)
        self.assertEqual(guardada.empresa_id, self.empresa_1.id)
        self.assertEqual(guardada.titulo, "Practicante Python")
        self.assertEqual(guardada.descripcion, "Desarrollo backend con Flask")
        self.assertEqual(guardada.estado, Convocatoria.ESTADO_BORRADOR)
        self.assertEqual(guardada.habilidades_requeridas, ["Python", "SQLAlchemy"])
        self.assertEqual(guardada.beneficios, ["Seguro", "Remoto"])

    def test_save_actualiza_convocatoria_existente(self):
        convocatoria = Convocatoria(
            empresa_id=self.empresa_1.id,
            titulo="Practicante QA",
            descripcion="Pruebas de software",
            estado=Convocatoria.ESTADO_BORRADOR,
            habilidades_requeridas=["Pytest"],
            beneficios=["Capacitación"],
        )
        guardada = self.repository.save(convocatoria)

        guardada.titulo = "Practicante QA Automation"
        guardada.estado = Convocatoria.ESTADO_PUBLICADA
        guardada.fecha_publicacion = datetime(2026, 10, 28, 12, 0, 0, tzinfo=timezone.utc)
        guardada.habilidades_requeridas = ["Pytest", "Selenium"]

        actualizada = self.repository.save(guardada)

        self.assertEqual(actualizada.id, guardada.id)
        self.assertEqual(actualizada.titulo, "Practicante QA Automation")
        self.assertEqual(actualizada.estado, Convocatoria.ESTADO_PUBLICADA)
        self.assertEqual(actualizada.habilidades_requeridas, ["Pytest", "Selenium"])

    def test_find_by_id_existente_e_inexistente(self):
        convocatoria = Convocatoria(
            empresa_id=self.empresa_1.id,
            titulo="Practicante Frontend",
            descripcion="React UI",
            estado=Convocatoria.ESTADO_PUBLICADA,
            habilidades_requeridas=["React"],
            beneficios=["Remoto"],
        )
        guardada = self.repository.save(convocatoria)

        recuperada = self.repository.find_by_id(guardada.id)
        self.assertIsNotNone(recuperada)
        self.assertEqual(recuperada.id, guardada.id)
        self.assertEqual(recuperada.titulo, "Practicante Frontend")
        self.assertEqual(recuperada.habilidades_requeridas, ["React"])

        self.assertIsNone(self.repository.find_by_id(99999))

    def test_find_all_y_find_by_empresa_id(self):
        c1 = Convocatoria(empresa_id=self.empresa_1.id, titulo="Dev Ops", estado=Convocatoria.ESTADO_BORRADOR)
        c2 = Convocatoria(empresa_id=self.empresa_1.id, titulo="Data Analyst", estado=Convocatoria.ESTADO_PUBLICADA)
        c3 = Convocatoria(empresa_id=self.empresa_2.id, titulo="Mobile Dev", estado=Convocatoria.ESTADO_BORRADOR)

        self.repository.save(c1)
        self.repository.save(c2)
        self.repository.save(c3)

        todas = self.repository.find_all()
        self.assertEqual(len(todas), 3)

        de_empresa_1 = self.repository.find_by_empresa_id(self.empresa_1.id)
        self.assertEqual(len(de_empresa_1), 2)
        titulos_empresa_1 = {c.titulo for c in de_empresa_1}
        self.assertEqual(titulos_empresa_1, {"Dev Ops", "Data Analyst"})

        de_empresa_vacia = self.repository.find_by_empresa_id(99999)
        self.assertEqual(de_empresa_vacia, [])

    def test_delete_existente_retorna_true_e_inexistente_retorna_false(self):
        convocatoria = Convocatoria(
            empresa_id=self.empresa_1.id,
            titulo="Temporal",
            estado=Convocatoria.ESTADO_BORRADOR,
        )
        guardada = self.repository.save(convocatoria)

        borrado = self.repository.delete(guardada.id)
        self.assertTrue(borrado)
        self.assertIsNone(self.repository.find_by_id(guardada.id))

        borrado_inexistente = self.repository.delete(99999)
        self.assertFalse(borrado_inexistente)

    def test_search_por_estado_y_coincidencia_texto(self):
        c1 = Convocatoria(
            empresa_id=self.empresa_1.id,
            titulo="Desarrollador Django",
            descripcion="Backend robusto",
            estado=Convocatoria.ESTADO_PUBLICADA,
            habilidades_requeridas=["Python", "Django"],
        )
        c2 = Convocatoria(
            empresa_id=self.empresa_1.id,
            titulo="Desarrollador React",
            descripcion="Frontend con Next.js",
            estado=Convocatoria.ESTADO_PUBLICADA,
            habilidades_requeridas=["JavaScript", "React"],
        )
        c3 = Convocatoria(
            empresa_id=self.empresa_2.id,
            titulo="Ingeniero Django Borrador",
            descripcion="En revisión",
            estado=Convocatoria.ESTADO_BORRADOR,
            habilidades_requeridas=["Django"],
        )
        self.repository.save(c1)
        self.repository.save(c2)
        self.repository.save(c3)

        # Filtro por estado
        publicadas = self.repository.search(estado=Convocatoria.ESTADO_PUBLICADA)
        self.assertEqual(len(publicadas), 2)

        # Filtro por texto en título
        resultados_django = self.repository.search(query="Django")
        self.assertEqual(len(resultados_django), 2)

        # Filtro combinado (query y estado)
        django_publicada = self.repository.search(query="Django", estado=Convocatoria.ESTADO_PUBLICADA)
        self.assertEqual(len(django_publicada), 1)
        self.assertEqual(django_publicada[0].titulo, "Desarrollador Django")

        # Filtro por habilidad requerida
        resultados_react = self.repository.search(query="React")
        self.assertEqual(len(resultados_react), 1)
        self.assertEqual(resultados_react[0].titulo, "Desarrollador React")

    def test_load_list_casos_borde(self):
        self.assertEqual(self.repository._load_list(None), [])
        self.assertEqual(self.repository._load_list(""), [])
        self.assertEqual(self.repository._load_list("no-json-valido"), [])
        self.assertEqual(self.repository._load_list('{"objeto": "no lista"}'), [])
