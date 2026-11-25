"""Pruebas unitarias de persistencia y consultas para SqlAlchemyPostulacionRepository."""

import unittest

from domain.convocatorias.postulacion import Postulacion
from bootstrap.app import create_app
from shared.database import db
from frameworks.sqlalchemy_orm.models.convocatoria_model import ConvocatoriaModel
from profiles.infrastructure.models.company_model import CompanyModel
from profiles.infrastructure.models.intern_model import InternModel
from identity.infrastructure.models.user_model import UserModel
from infrastructure.sqlalchemy_postulacion_repository import SqlAlchemyPostulacionRepository


class TestPostulacionRepository(unittest.TestCase):
    """Pruebas del repositorio de postulaciones con SQLite en memoria sin dobles."""

    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.repository = SqlAlchemyPostulacionRepository()

        # Preparar entidades base para cumplir con integridad referencial (FKs)
        self.company = self._crear_empresa(email="empresa_post@test.com", ruc="20111222333")
        self.convocatoria_1 = self._crear_convocatoria(self.company.id, titulo="Backend Python")
        self.convocatoria_2 = self._crear_convocatoria(self.company.id, titulo="Frontend React")

        self.practicante_1 = self._crear_practicante(email="pract1@test.com", dni="71112233")
        self.practicante_2 = self._crear_practicante(email="pract2@test.com", dni="72223344")

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def _crear_empresa(self, email, ruc):
        user = UserModel(
            email=email,
            password_hash="hash_test",
            role="empresa",
            status="activo",
        )
        db.session.add(user)
        db.session.flush()

        company = CompanyModel(
            user_id=user.id,
            legal_name="Empresa Postulaciones",
            ruc=ruc,
            verified=True,
        )
        db.session.add(company)
        db.session.commit()
        return company

    def _crear_convocatoria(self, company_id, titulo):
        convocatoria = ConvocatoriaModel(
            company_id=company_id,
            titulo=titulo,
            status="publicada",
        )
        db.session.add(convocatoria)
        db.session.commit()
        return convocatoria

    def _crear_practicante(self, email, dni):
        user = UserModel(
            email=email,
            password_hash="hash_test",
            role="practicante",
            status="activo",
        )
        db.session.add(user)
        db.session.flush()

        intern = InternModel(
            user_id=user.id,
            first_names="Juan",
            last_names="Pérez",
            dni=dni,
        )
        db.session.add(intern)
        db.session.commit()
        return intern

    def test_save_crea_nueva_postulacion_y_asigna_id(self):
        postulacion = Postulacion(
            convocatoria_id=self.convocatoria_1.id,
            intern_id=self.practicante_1.id,
            status=Postulacion.STATUS_PENDING,
        )

        saved = self.repository.save(postulacion)

        self.assertIsNotNone(saved.id)
        self.assertEqual(saved.convocatoria_id, self.convocatoria_1.id)
        self.assertEqual(saved.intern_id, self.practicante_1.id)
        self.assertEqual(saved.status, Postulacion.STATUS_PENDING)

    def test_save_actualiza_estado_de_postulacion_existente(self):
        postulacion = Postulacion(
            convocatoria_id=self.convocatoria_1.id,
            intern_id=self.practicante_1.id,
            status=Postulacion.STATUS_PENDING,
        )
        saved = self.repository.save(postulacion)

        saved.status = Postulacion.ESTADO_SELECCIONADA
        actualizada = self.repository.save(saved)

        self.assertEqual(actualizada.id, saved.id)
        self.assertEqual(actualizada.status, Postulacion.ESTADO_SELECCIONADA)

        # Confirmar persistencia en BD
        reloaded = self.repository.find_by_id(saved.id)
        self.assertEqual(reloaded.status, Postulacion.ESTADO_SELECCIONADA)

    def test_save_all_persiste_varias_postulaciones_en_una_transaccion(self):
        p1 = self.repository.save(Postulacion(
            convocatoria_id=self.convocatoria_1.id,
            intern_id=self.practicante_1.id,
            status=Postulacion.STATUS_PENDING,
        ))
        p2 = self.repository.save(Postulacion(
            convocatoria_id=self.convocatoria_1.id,
            intern_id=self.practicante_2.id,
            status=Postulacion.STATUS_PENDING,
        ))
        p1.status = Postulacion.ESTADO_SELECCIONADA
        p2.status = Postulacion.ESTADO_RECHAZADA

        guardadas = self.repository.save_all([p1, p2])

        self.assertEqual([g.status for g in guardadas], ["seleccionada", "rechazada"])
        self.assertEqual(self.repository.find_by_id(p1.id).status, Postulacion.ESTADO_SELECCIONADA)
        self.assertEqual(self.repository.find_by_id(p2.id).status, Postulacion.ESTADO_RECHAZADA)

    def test_save_all_hace_rollback_si_falla_el_commit(self):
        p1 = self.repository.save(Postulacion(
            convocatoria_id=self.convocatoria_1.id,
            intern_id=self.practicante_1.id,
            status=Postulacion.STATUS_PENDING,
        ))
        p1.status = Postulacion.ESTADO_SELECCIONADA
        invalida = Postulacion(
            convocatoria_id=99999,
            intern_id=self.practicante_2.id,
            status=Postulacion.STATUS_PENDING,
        )

        with self.assertRaises(Exception):
            self.repository.save_all([p1, invalida])

        self.assertEqual(self.repository.find_by_id(p1.id).status, Postulacion.STATUS_PENDING)

    def test_find_by_id_existente_e_inexistente(self):
        postulacion = Postulacion(
            convocatoria_id=self.convocatoria_1.id,
            intern_id=self.practicante_1.id,
            status=Postulacion.STATUS_PENDING,
        )
        saved = self.repository.save(postulacion)

        reloaded = self.repository.find_by_id(saved.id)
        self.assertIsNotNone(reloaded)
        self.assertEqual(reloaded.id, saved.id)
        self.assertEqual(reloaded.convocatoria_id, self.convocatoria_1.id)
        self.assertEqual(reloaded.intern_id, self.practicante_1.id)

        self.assertIsNone(self.repository.find_by_id(99999))

    def test_find_by_practicante_id(self):
        p1 = Postulacion(
            convocatoria_id=self.convocatoria_1.id,
            intern_id=self.practicante_1.id,
        )
        p2 = Postulacion(
            convocatoria_id=self.convocatoria_2.id,
            intern_id=self.practicante_1.id,
        )
        p3 = Postulacion(
            convocatoria_id=self.convocatoria_1.id,
            intern_id=self.practicante_2.id,
        )
        self.repository.save(p1)
        self.repository.save(p2)
        self.repository.save(p3)

        postulaciones_pract1 = self.repository.find_by_practicante_id(self.practicante_1.id)
        self.assertEqual(len(postulaciones_pract1), 2)
        convocatorias_pract1 = {p.convocatoria_id for p in postulaciones_pract1}
        self.assertEqual(convocatorias_pract1, {self.convocatoria_1.id, self.convocatoria_2.id})

        postulaciones_vacio = self.repository.find_by_practicante_id(99999)
        self.assertEqual(postulaciones_vacio, [])

    def test_find_by_convocatoria_id(self):
        p1 = Postulacion(
            convocatoria_id=self.convocatoria_1.id,
            intern_id=self.practicante_1.id,
        )
        p2 = Postulacion(
            convocatoria_id=self.convocatoria_1.id,
            intern_id=self.practicante_2.id,
        )
        self.repository.save(p1)
        self.repository.save(p2)

        postulaciones_conv1 = self.repository.find_by_convocatoria_id(self.convocatoria_1.id)
        self.assertEqual(len(postulaciones_conv1), 2)

        postulaciones_vacio = self.repository.find_by_convocatoria_id(99999)
        self.assertEqual(postulaciones_vacio, [])

    def test_find_by_convocatoria_and_practicante(self):
        postulacion = Postulacion(
            convocatoria_id=self.convocatoria_1.id,
            intern_id=self.practicante_1.id,
            status=Postulacion.STATUS_PENDING,
        )
        self.repository.save(postulacion)

        encontrada = self.repository.find_by_convocatoria_and_practicante(
            self.convocatoria_1.id, self.practicante_1.id
        )
        self.assertIsNotNone(encontrada)
        self.assertEqual(encontrada.convocatoria_id, self.convocatoria_1.id)
        self.assertEqual(encontrada.intern_id, self.practicante_1.id)

        inexistente = self.repository.find_by_convocatoria_and_practicante(
            self.convocatoria_2.id, self.practicante_1.id
        )
        self.assertIsNone(inexistente)

    def test_to_postulacion_domain_con_none(self):
        self.assertIsNone(self.repository._to_postulacion_domain(None))
