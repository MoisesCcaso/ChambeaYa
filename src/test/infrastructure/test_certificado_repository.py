"""Pruebas del repositorio SQLAlchemy de certificados con SQLite en memoria."""

import pytest

from domain.certificacion.archivo_pdf import ArchivoPDF
from domain.certificacion.certificado import Certificado
from domain.certificacion.codigo_qr import CodigoQR
from frameworks.sqlalchemy_orm.database import db
from frameworks.sqlalchemy_orm.models.certificado_model import CertificadoModel
from frameworks.sqlalchemy_orm.models.convocatoria_model import ConvocatoriaModel
from frameworks.sqlalchemy_orm.models.empresa_model import EmpresaModel
from frameworks.sqlalchemy_orm.models.postulacion_model import PostulacionModel
from frameworks.sqlalchemy_orm.models.practica_model import PracticaModel
from frameworks.sqlalchemy_orm.models.practicante_model import PracticanteModel
from frameworks.sqlalchemy_orm.models.usuario_model import UsuarioModel
from infrastructure.sqlalchemy_certificado_repository import (
    SqlAlchemyCertificadoRepository,
)


@pytest.fixture
def practica_id(app_context):
    """Crea con modelos reales todas las relaciones requeridas por un certificado."""
    usuario_practicante = UsuarioModel(
        email="practicante-certificado@test.local",
        password_hash="hash",
        tipo="practicante",
        estado="activo",
    )
    practicante = PracticanteModel(usuario=usuario_practicante)
    usuario_empresa = UsuarioModel(
        email="empresa-certificado@test.local",
        password_hash="hash",
        tipo="empresa",
        estado="activo",
    )
    empresa = EmpresaModel(
        usuario=usuario_empresa,
        razon_social="Empresa Certificadora",
        ruc="20987654321",
    )
    convocatoria = ConvocatoriaModel(
        empresa=empresa,
        titulo="Prácticas certificadas",
        estado="publicada",
    )
    db.session.add_all([practicante, convocatoria])
    db.session.flush()

    postulacion = PostulacionModel(
        convocatoria_id=convocatoria.id,
        practicante_id=practicante.id,
        estado="seleccionada",
    )
    db.session.add(postulacion)
    db.session.flush()

    practica = PracticaModel(
        postulacion_id=postulacion.id,
        practicante_id=practicante.id,
        estado="FINALIZADA",
    )
    db.session.add(practica)
    db.session.commit()
    return practica.id


@pytest.fixture
def repository():
    return SqlAlchemyCertificadoRepository()


def crear_certificado(practica_id, *, codigo="CERT-PRUEBA-001", contenido="Certificado"):
    return Certificado(
        practica_id=practica_id,
        codigo_qr=CodigoQR(
            valor=codigo,
            url_verificacion=f"/certificados/verificar/{codigo}",
            hash_integridad="a" * 64,
        ),
        documento=ArchivoPDF(
            url=f"/certificados/practica/{practica_id}/pdf",
            hash_integridad="b" * 64,
            contenido=contenido,
        ),
    )


def test_usa_sqlite_en_memoria(app):
    assert app.config["SQLALCHEMY_DATABASE_URI"] == "sqlite:///:memory:"


def test_save_persiste_certificado_codigo_qr_y_documento(
    app_context,
    repository,
    practica_id,
):
    guardado = repository.save(crear_certificado(practica_id))
    db.session.expire_all()

    modelo = db.session.get(CertificadoModel, guardado.id)
    assert modelo is not None
    assert modelo.practica_id == practica_id
    assert modelo.codigo_qr_valor == "CERT-PRUEBA-001"
    assert modelo.codigo_qr_url_verificacion == (
        "/certificados/verificar/CERT-PRUEBA-001"
    )
    assert modelo.codigo_qr_hash == "a" * 64
    assert modelo.documento_url == f"/certificados/practica/{practica_id}/pdf"
    assert modelo.documento_hash == "b" * 64
    assert modelo.documento_contenido == "Certificado"

    assert guardado.id is not None
    assert guardado.practica_id == practica_id
    assert guardado.codigo_qr.valor == "CERT-PRUEBA-001"
    assert guardado.documento.contenido == "Certificado"


def test_find_by_id_reconstruye_el_certificado_completo(
    app_context,
    repository,
    practica_id,
):
    guardado = repository.save(crear_certificado(practica_id))

    encontrado = repository.find_by_id(guardado.id)

    assert isinstance(encontrado, Certificado)
    assert encontrado.id == guardado.id
    assert encontrado.practica_id == practica_id
    assert isinstance(encontrado.codigo_qr, CodigoQR)
    assert encontrado.codigo_qr.valor == "CERT-PRUEBA-001"
    assert encontrado.codigo_qr.hash_integridad == "a" * 64
    assert isinstance(encontrado.documento, ArchivoPDF)
    assert encontrado.documento.hash_integridad == "b" * 64
    assert encontrado.documento.contenido == "Certificado"


def test_consulta_por_codigo(repository, practica_id):
    guardado = repository.save(crear_certificado(practica_id))

    encontrado = repository.find_by_codigo("CERT-PRUEBA-001")

    assert encontrado.id == guardado.id
    assert encontrado.codigo_qr.valor == "CERT-PRUEBA-001"


def test_consulta_por_practica(repository, practica_id):
    guardado = repository.save(crear_certificado(practica_id))

    encontrado = repository.find_by_practica_id(practica_id)

    assert encontrado.id == guardado.id
    assert encontrado.practica_id == practica_id


def test_consultas_inexistentes_devuelven_none(app_context, repository):
    assert repository.find_by_id(9999) is None
    assert repository.find_by_codigo("CODIGO-INEXISTENTE") is None
    assert repository.find_by_practica_id(9999) is None


def test_save_actualiza_un_certificado_existente_sin_duplicarlo(
    app_context,
    repository,
    practica_id,
):
    certificado = repository.save(crear_certificado(practica_id))
    certificado.codigo_qr = CodigoQR(
        valor="CERT-ACTUALIZADO-002",
        url_verificacion="/certificados/verificar/CERT-ACTUALIZADO-002",
        hash_integridad="c" * 64,
    )
    certificado.documento = ArchivoPDF(
        url=f"/certificados/practica/{practica_id}/pdf",
        hash_integridad="d" * 64,
        contenido="Contenido actualizado",
    )

    actualizado = repository.save(certificado)

    assert actualizado.id == certificado.id
    assert actualizado.codigo_qr.valor == "CERT-ACTUALIZADO-002"
    assert actualizado.codigo_qr.hash_integridad == "c" * 64
    assert actualizado.documento.hash_integridad == "d" * 64
    assert actualizado.documento.contenido == "Contenido actualizado"
    assert CertificadoModel.query.count() == 1


def test_save_y_consulta_certificado_sin_codigo_ni_documento(
    app_context,
    repository,
    practica_id,
):
    guardado = repository.save(Certificado(practica_id=practica_id))

    encontrado = repository.find_by_id(guardado.id)

    assert encontrado.practica_id == practica_id
    assert encontrado.codigo_qr is None
    assert encontrado.documento is None
