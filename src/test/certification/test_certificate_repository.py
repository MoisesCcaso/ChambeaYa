"""SQLAlchemy certificate repository tests with in-memory SQLite."""

import pytest

from certification.domain.pdf_file import PdfFile
from certification.domain.certificate import Certificate
from certification.domain.qr_code import QrCode
from shared.database import db
from certification.infrastructure.models.certificate_model import CertificateModel
from recruitment.infrastructure.models.job_posting_model import JobPostingModel
from profiles.infrastructure.models.company_model import CompanyModel
from recruitment.infrastructure.models.job_application_model import JobApplicationModel
from internships.infrastructure.models.internship_model import InternshipModel
from profiles.infrastructure.models.intern_model import InternModel
from identity.infrastructure.models.user_model import UserModel
from certification.infrastructure.sqlalchemy_certificate_repository import (
    SqlAlchemyCertificateRepository,
)


@pytest.fixture
def internship_id(app_context):
    """Creates, with real models, every row a certificate depends on."""
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
    return SqlAlchemyCertificateRepository()


def create_certificate(internship_id, *, code="CERT-PRUEBA-001", content="Certificado"):
    return Certificate(
        internship_id=internship_id,
        qr_code=QrCode(
            value=code,
            verification_url=f"/certificados/verificar/{code}",
            integrity_hash="a" * 64,
        ),
        document=PdfFile(
            url=f"/certificados/practica/{internship_id}/pdf",
            integrity_hash="b" * 64,
            content=content,
        ),
    )


def test_uses_in_memory_sqlite(app):
    assert app.config["SQLALCHEMY_DATABASE_URI"] == "sqlite:///:memory:"


def test_save_persists_certificate_qr_code_and_document(
    app_context,
    repository,
    internship_id,
):
    saved = repository.save(create_certificate(internship_id))
    db.session.expire_all()

    orm_model = db.session.get(CertificateModel, saved.id)
    assert orm_model is not None
    assert orm_model.internship_id == internship_id
    assert orm_model.qr_code_value == "CERT-PRUEBA-001"
    assert orm_model.qr_code_verification_url == (
        "/certificados/verificar/CERT-PRUEBA-001"
    )
    assert orm_model.qr_code_hash == "a" * 64
    assert orm_model.document_url == f"/certificados/practica/{internship_id}/pdf"
    assert orm_model.document_hash == "b" * 64
    assert orm_model.document_content == "Certificado"

    assert saved.id is not None
    assert saved.internship_id == internship_id
    assert saved.qr_code.value == "CERT-PRUEBA-001"
    assert saved.document.content == "Certificado"


def test_find_by_id_rebuilds_the_full_certificate(
    app_context,
    repository,
    internship_id,
):
    saved = repository.save(create_certificate(internship_id))

    found = repository.find_by_id(saved.id)

    assert isinstance(found, Certificate)
    assert found.id == saved.id
    assert found.internship_id == internship_id
    assert isinstance(found.qr_code, QrCode)
    assert found.qr_code.value == "CERT-PRUEBA-001"
    assert found.qr_code.integrity_hash == "a" * 64
    assert isinstance(found.document, PdfFile)
    assert found.document.integrity_hash == "b" * 64
    assert found.document.content == "Certificado"


def test_query_by_code(repository, internship_id):
    saved = repository.save(create_certificate(internship_id))

    found = repository.find_by_code("CERT-PRUEBA-001")

    assert found.id == saved.id
    assert found.qr_code.value == "CERT-PRUEBA-001"


def test_query_by_internship(repository, internship_id):
    saved = repository.save(create_certificate(internship_id))

    found = repository.find_by_internship_id(internship_id)

    assert found.id == saved.id
    assert found.internship_id == internship_id


def test_missing_queries_return_none(app_context, repository):
    assert repository.find_by_id(9999) is None
    assert repository.find_by_code("CODIGO-INEXISTENTE") is None
    assert repository.find_by_internship_id(9999) is None


def test_save_updates_an_existing_certificate_without_duplicating_it(
    app_context,
    repository,
    internship_id,
):
    certificate = repository.save(create_certificate(internship_id))
    certificate.qr_code = QrCode(
        value="CERT-ACTUALIZADO-002",
        verification_url="/certificados/verificar/CERT-ACTUALIZADO-002",
        integrity_hash="c" * 64,
    )
    certificate.document = PdfFile(
        url=f"/certificados/practica/{internship_id}/pdf",
        integrity_hash="d" * 64,
        content="Contenido actualizado",
    )

    updated_certificate = repository.save(certificate)

    assert updated_certificate.id == certificate.id
    assert updated_certificate.qr_code.value == "CERT-ACTUALIZADO-002"
    assert updated_certificate.qr_code.integrity_hash == "c" * 64
    assert updated_certificate.document.integrity_hash == "d" * 64
    assert updated_certificate.document.content == "Contenido actualizado"
    assert CertificateModel.query.count() == 1


def test_save_and_query_certificate_without_code_or_document(
    app_context,
    repository,
    internship_id,
):
    saved = repository.save(Certificate(internship_id=internship_id))

    found = repository.find_by_id(saved.id)

    assert found.internship_id == internship_id
    assert found.qr_code is None
    assert found.document is None
