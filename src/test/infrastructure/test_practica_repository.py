"""Pruebas de integración del repositorio SQLAlchemy de prácticas."""

from datetime import datetime, timezone

import pytest

from domain.practica_evaluacion.entregable import Entregable
from domain.practica_evaluacion.evaluacion import Evaluacion
from domain.practica_evaluacion.practica import Practica
from shared.database import db
from recruitment.infrastructure.models.job_posting_model import JobPostingModel
from profiles.infrastructure.models.company_model import CompanyModel
from frameworks.sqlalchemy_orm.models.entregable_model import EntregableModel
from frameworks.sqlalchemy_orm.models.evaluacion_model import EvaluacionModel
from recruitment.infrastructure.models.job_application_model import JobApplicationModel
from frameworks.sqlalchemy_orm.models.practica_model import PracticaModel
from profiles.infrastructure.models.intern_model import InternModel
from identity.infrastructure.models.user_model import UserModel
from infrastructure.sqlalchemy_practica_repository import SqlAlchemyPracticaRepository


@pytest.fixture
def datos_practica(app_context):
    """Persiste las relaciones requeridas por las claves foráneas de una práctica."""
    intern_user = UserModel(
        email="practicante-repository@test.local",
        password_hash="hash",
        role="practicante",
        status="activo",
    )
    intern = InternModel(user=intern_user)
    company_user = UserModel(
        email="empresa-repository@test.local",
        password_hash="hash",
        role="empresa",
        status="activo",
    )
    company = CompanyModel(
        user=company_user,
        legal_name="Empresa de prueba",
        ruc="20123456789",
    )
    job_posting = JobPostingModel(
        company=company,
        title="Prácticas de desarrollo",
        status="publicada",
    )
    db.session.add_all([intern, job_posting])
    db.session.flush()

    job_application = JobApplicationModel(
        job_posting_id=job_posting.id,
        intern_id=intern.id,
        status="seleccionada",
    )
    db.session.add(job_application)
    db.session.commit()

    return {
        "postulacion_id": job_application.id,
        "practicante_id": intern.id,
    }


@pytest.fixture
def repository():
    return SqlAlchemyPracticaRepository()


def crear_practica(datos_practica, *, entregables=None, evaluaciones=None):
    return Practica(
        job_application_id=datos_practica["postulacion_id"],
        intern_id=datos_practica["practicante_id"],
        entregables=entregables,
        evaluaciones=evaluaciones,
    )


def test_usa_sqlite_en_memoria(app):
    assert app.config["SQLALCHEMY_DATABASE_URI"] == "sqlite:///:memory:"


def test_save_persiste_practica_entregable_y_evaluacion(
    app_context,
    repository,
    datos_practica,
):
    moment = datetime(2026, 10, 28, 15, 30, tzinfo=timezone.utc)
    practica = crear_practica(
        datos_practica,
        entregables=[Entregable(archivo="informe.pdf", fecha_subida=moment)],
        evaluaciones=[Evaluacion(score=85, fecha_evaluacion=moment)],
    )

    saved = repository.save(practica)
    db.session.expire_all()

    modelo = db.session.get(PracticaModel, saved.id)
    assert modelo is not None
    assert modelo.job_application_id == datos_practica["postulacion_id"]
    assert modelo.intern_id == datos_practica["practicante_id"]
    assert modelo.status == Practica.ESTADO_EN_CURSO
    assert len(modelo.entregables) == 1
    assert modelo.entregables[0].archivo == "informe.pdf"
    assert len(modelo.evaluaciones) == 1
    assert modelo.evaluaciones[0].score == 85

    assert saved.id is not None
    assert saved.entregables[0].id is not None
    assert saved.entregables[0].practica_id == saved.id
    assert saved.evaluaciones[0].id is not None
    assert saved.evaluaciones[0].practica_id == saved.id


def test_find_by_id_reconstruye_el_agregado_completo(
    app_context,
    repository,
    datos_practica,
):
    practica = crear_practica(datos_practica)
    practica.subir_entregable("evidencia.zip")
    practica.registrar_evaluacion(72)
    saved = repository.save(practica)

    found = repository.find_by_id(saved.id)

    assert isinstance(found, Practica)
    assert found.id == saved.id
    assert found.job_application_id == datos_practica["postulacion_id"]
    assert found.intern_id == datos_practica["practicante_id"]
    assert found.status == Practica.ESTADO_EN_CURSO
    assert [item.archivo for item in found.entregables] == ["evidencia.zip"]
    assert [item.score for item in found.evaluaciones] == [72]


def test_consultas_por_practicante_y_postulacion(
    app_context,
    repository,
    datos_practica,
):
    saved = repository.save(crear_practica(datos_practica))

    por_practicante = repository.find_by_intern_id(
        datos_practica["practicante_id"]
    )
    por_postulacion = repository.find_by_job_application_id(
        datos_practica["postulacion_id"]
    )

    assert [practica.id for practica in por_practicante] == [saved.id]
    assert por_postulacion.id == saved.id


def test_consultas_inexistentes_devuelven_resultados_vacios(app_context, repository):
    assert repository.find_by_id(9999) is None
    assert repository.find_by_job_application_id(9999) is None
    assert repository.find_by_intern_id(9999) == []


def test_save_actualiza_estado_y_agrega_nuevos_hijos_sin_duplicar_existentes(
    app_context,
    repository,
    datos_practica,
):
    practica = crear_practica(datos_practica)
    practica.subir_entregable("primer-informe.pdf")
    practica.registrar_evaluacion(65)
    practica = repository.save(practica)

    practica.subir_entregable("informe-final.pdf")
    practica.registrar_evaluacion(90)
    practica.status = Practica.ESTADO_FINALIZADA
    updated = repository.save(practica)

    assert updated.status == Practica.ESTADO_FINALIZADA
    assert [item.archivo for item in updated.entregables] == [
        "primer-informe.pdf",
        "informe-final.pdf",
    ]
    assert [item.score for item in updated.evaluaciones] == [65, 90]
    assert PracticaModel.query.count() == 1
    assert EntregableModel.query.count() == 2
    assert EvaluacionModel.query.count() == 2


def test_save_elimina_hijos_retirados_del_agregado(
    app_context,
    repository,
    datos_practica,
):
    practica = crear_practica(datos_practica)
    practica.subir_entregable("informe-1.pdf")
    practica.subir_entregable("informe-2.pdf")
    practica.registrar_evaluacion(55)
    practica.registrar_evaluacion(95)
    practica = repository.save(practica)

    entregable_eliminado_id = practica.entregables.pop(0).id
    evaluacion_eliminada_id = practica.evaluaciones.pop(0).id
    updated = repository.save(practica)

    assert [item.archivo for item in updated.entregables] == ["informe-2.pdf"]
    assert [item.score for item in updated.evaluaciones] == [95]
    assert db.session.get(EntregableModel, entregable_eliminado_id) is None
    assert db.session.get(EvaluacionModel, evaluacion_eliminada_id) is None


def test_find_by_empresa_id_retorna_practicas_asociadas_via_join(
    app_context,
    repository,
    datos_practica,
):
    job_application = db.session.get(JobApplicationModel, datos_practica["postulacion_id"])
    job_posting = db.session.get(JobPostingModel, job_application.job_posting_id)
    company_id = job_posting.company_id

    practica = crear_practica(datos_practica)
    saved = repository.save(practica)

    result = repository.find_by_company_id(company_id)
    assert len(result) == 1
    assert result[0].id == saved.id

    assert repository.find_by_company_id(99999) == []
