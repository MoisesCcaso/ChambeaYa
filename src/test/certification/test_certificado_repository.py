"""Pruebas del repositorio SQLAlchemy de certificados con SQLite en memoria."""

import pytest

from certification.domain.archivo_pdf import ArchivoPDF
from certification.domain.certificado import Certificado
from certification.domain.codigo_qr import CodigoQR
from shared.database import db
from certification.infrastructure.models.certificado_model import CertificadoModel
from recruitment.infrastructure.models.job_posting_model import JobPostingModel
from profiles.infrastructure.models.company_model import CompanyModel
from recruitment.infrastructure.models.job_application_model import JobApplicationModel
from internships.infrastructure.models.internship_model import InternshipModel
from profiles.infrastructure.models.intern_model import InternModel
from identity.infrastructure.models.user_model import UserModel
from certification.infrastructure.sqlalchemy_certificado_repository import (
    SqlAlchemyCertificadoRepository,
)


@pytest.fixture
def internship_id(app_context):
    """Crea con modelos reales todas las relaciones requeridas por un certificado."""
    intern_user = UserModel(
        email="practicante-certificado@test.local",
        password_hash="hash",
        role="practicante",
        status="activo",
    )
    intern = InternModel(user=intern_user)
    company_user = UserModel(
        email="empresa-certificado@test.local",
        password_hash="hash",
        role="empresa",
        status="activo",
    )
    company = CompanyModel(
        user=company_user,
        legal_name="Empresa Certificadora",
        ruc="20987654321",
    )
    job_posting = JobPostingModel(
        company=company,
        title="Prácticas certificadas",
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
    db.session.flush()

    internship = InternshipModel(
        job_application_id=job_application.id,
        intern_id=intern.id,
        status="FINALIZADA",
    )
    db.session.add(internship)
    db.session.commit()
    return internship.id


@pytest.fixture
def repository():
    return SqlAlchemyCertificadoRepository()


def crear_certificado(internship_id, *, codigo="CERT-PRUEBA-001", contenido="Certificado"):
    return Certificado(
        internship_id=internship_id,
        codigo_qr=CodigoQR(
            value=codigo,
            url_verificacion=f"/certificados/verificar/{codigo}",
            hash_integridad="a" * 64,
        ),
        documento=ArchivoPDF(
            url=f"/certificados/practica/{internship_id}/pdf",
            hash_integridad="b" * 64,
            contenido=contenido,
        ),
    )


def test_uses_in_memory_sqlite(app):
    assert app.config["SQLALCHEMY_DATABASE_URI"] == "sqlite:///:memory:"


def test_save_persiste_certificado_codigo_qr_y_documento(
    app_context,
    repository,
    internship_id,
):
    saved = repository.save(crear_certificado(internship_id))
    db.session.expire_all()

    orm_model = db.session.get(CertificadoModel, saved.id)
    assert orm_model is not None
    assert orm_model.internship_id == internship_id
    assert orm_model.codigo_qr_valor == "CERT-PRUEBA-001"
    assert orm_model.codigo_qr_url_verificacion == (
        "/certificados/verificar/CERT-PRUEBA-001"
    )
    assert orm_model.codigo_qr_hash == "a" * 64
    assert orm_model.documento_url == f"/certificados/practica/{internship_id}/pdf"
    assert orm_model.documento_hash == "b" * 64
    assert orm_model.documento_contenido == "Certificado"

    assert saved.id is not None
    assert saved.internship_id == internship_id
    assert saved.codigo_qr.value == "CERT-PRUEBA-001"
    assert saved.documento.contenido == "Certificado"


def test_find_by_id_reconstruye_el_certificado_completo(
    app_context,
    repository,
    internship_id,
):
    saved = repository.save(crear_certificado(internship_id))

    found = repository.find_by_id(saved.id)

    assert isinstance(found, Certificado)
    assert found.id == saved.id
    assert found.internship_id == internship_id
    assert isinstance(found.codigo_qr, CodigoQR)
    assert found.codigo_qr.value == "CERT-PRUEBA-001"
    assert found.codigo_qr.hash_integridad == "a" * 64
    assert isinstance(found.documento, ArchivoPDF)
    assert found.documento.hash_integridad == "b" * 64
    assert found.documento.contenido == "Certificado"


def test_consulta_por_codigo(repository, internship_id):
    saved = repository.save(crear_certificado(internship_id))

    found = repository.find_by_codigo("CERT-PRUEBA-001")

    assert found.id == saved.id
    assert found.codigo_qr.value == "CERT-PRUEBA-001"


def test_consulta_por_practica(repository, internship_id):
    saved = repository.save(crear_certificado(internship_id))

    found = repository.find_by_practica_id(internship_id)

    assert found.id == saved.id
    assert found.internship_id == internship_id


def test_consultas_inexistentes_devuelven_none(app_context, repository):
    assert repository.find_by_id(9999) is None
    assert repository.find_by_codigo("CODIGO-INEXISTENTE") is None
    assert repository.find_by_practica_id(9999) is None


def test_save_actualiza_un_certificado_existente_sin_duplicarlo(
    app_context,
    repository,
    internship_id,
):
    certificado = repository.save(crear_certificado(internship_id))
    certificado.codigo_qr = CodigoQR(
        value="CERT-ACTUALIZADO-002",
        url_verificacion="/certificados/verificar/CERT-ACTUALIZADO-002",
        hash_integridad="c" * 64,
    )
    certificado.documento = ArchivoPDF(
        url=f"/certificados/practica/{internship_id}/pdf",
        hash_integridad="d" * 64,
        contenido="Contenido actualizado",
    )

    actualizado = repository.save(certificado)

    assert actualizado.id == certificado.id
    assert actualizado.codigo_qr.value == "CERT-ACTUALIZADO-002"
    assert actualizado.codigo_qr.hash_integridad == "c" * 64
    assert actualizado.documento.hash_integridad == "d" * 64
    assert actualizado.documento.contenido == "Contenido actualizado"
    assert CertificadoModel.query.count() == 1


def test_save_y_consulta_certificado_sin_codigo_ni_documento(
    app_context,
    repository,
    internship_id,
):
    saved = repository.save(Certificado(internship_id=internship_id))

    found = repository.find_by_id(saved.id)

    assert found.internship_id == internship_id
    assert found.codigo_qr is None
    assert found.documento is None
