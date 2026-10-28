"""Pruebas de integración del repositorio SQLAlchemy de prácticas."""

from datetime import datetime, timezone

import pytest

from domain.practica_evaluacion.entregable import Entregable
from domain.practica_evaluacion.evaluacion import Evaluacion
from domain.practica_evaluacion.practica import Practica
from frameworks.sqlalchemy_orm.database import db
from frameworks.sqlalchemy_orm.models.convocatoria_model import ConvocatoriaModel
from frameworks.sqlalchemy_orm.models.empresa_model import EmpresaModel
from frameworks.sqlalchemy_orm.models.entregable_model import EntregableModel
from frameworks.sqlalchemy_orm.models.evaluacion_model import EvaluacionModel
from frameworks.sqlalchemy_orm.models.postulacion_model import PostulacionModel
from frameworks.sqlalchemy_orm.models.practica_model import PracticaModel
from frameworks.sqlalchemy_orm.models.practicante_model import PracticanteModel
from frameworks.sqlalchemy_orm.models.usuario_model import UsuarioModel
from infrastructure.sqlalchemy_practica_repository import SqlAlchemyPracticaRepository


@pytest.fixture
def datos_practica(app_context):
    """Persiste las relaciones requeridas por las claves foráneas de una práctica."""
    usuario_practicante = UsuarioModel(
        email="practicante-repository@test.local",
        password_hash="hash",
        tipo="practicante",
        estado="activo",
    )
    practicante = PracticanteModel(usuario=usuario_practicante)
    usuario_empresa = UsuarioModel(
        email="empresa-repository@test.local",
        password_hash="hash",
        tipo="empresa",
        estado="activo",
    )
    empresa = EmpresaModel(
        usuario=usuario_empresa,
        razon_social="Empresa de prueba",
        ruc="20123456789",
    )
    convocatoria = ConvocatoriaModel(
        empresa=empresa,
        titulo="Prácticas de desarrollo",
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
    db.session.commit()

    return {
        "postulacion_id": postulacion.id,
        "practicante_id": practicante.id,
    }


@pytest.fixture
def repository():
    return SqlAlchemyPracticaRepository()


def crear_practica(datos_practica, *, entregables=None, evaluaciones=None):
    return Practica(
        postulacion_id=datos_practica["postulacion_id"],
        practicante_id=datos_practica["practicante_id"],
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
    fecha = datetime(2026, 10, 28, 15, 30, tzinfo=timezone.utc)
    practica = crear_practica(
        datos_practica,
        entregables=[Entregable(archivo="informe.pdf", fecha_subida=fecha)],
        evaluaciones=[Evaluacion(puntaje=85, fecha_evaluacion=fecha)],
    )

    guardada = repository.save(practica)
    db.session.expire_all()

    modelo = db.session.get(PracticaModel, guardada.id)
    assert modelo is not None
    assert modelo.postulacion_id == datos_practica["postulacion_id"]
    assert modelo.practicante_id == datos_practica["practicante_id"]
    assert modelo.estado == Practica.ESTADO_EN_CURSO
    assert len(modelo.entregables) == 1
    assert modelo.entregables[0].archivo == "informe.pdf"
    assert len(modelo.evaluaciones) == 1
    assert modelo.evaluaciones[0].puntaje == 85

    assert guardada.id is not None
    assert guardada.entregables[0].id is not None
    assert guardada.entregables[0].practica_id == guardada.id
    assert guardada.evaluaciones[0].id is not None
    assert guardada.evaluaciones[0].practica_id == guardada.id


def test_find_by_id_reconstruye_el_agregado_completo(
    app_context,
    repository,
    datos_practica,
):
    practica = crear_practica(datos_practica)
    practica.subir_entregable("evidencia.zip")
    practica.registrar_evaluacion(72)
    guardada = repository.save(practica)

    encontrada = repository.find_by_id(guardada.id)

    assert isinstance(encontrada, Practica)
    assert encontrada.id == guardada.id
    assert encontrada.postulacion_id == datos_practica["postulacion_id"]
    assert encontrada.practicante_id == datos_practica["practicante_id"]
    assert encontrada.estado == Practica.ESTADO_EN_CURSO
    assert [item.archivo for item in encontrada.entregables] == ["evidencia.zip"]
    assert [item.puntaje for item in encontrada.evaluaciones] == [72]


def test_consultas_por_practicante_y_postulacion(
    app_context,
    repository,
    datos_practica,
):
    guardada = repository.save(crear_practica(datos_practica))

    por_practicante = repository.find_by_practicante_id(
        datos_practica["practicante_id"]
    )
    por_postulacion = repository.find_by_postulacion_id(
        datos_practica["postulacion_id"]
    )

    assert [practica.id for practica in por_practicante] == [guardada.id]
    assert por_postulacion.id == guardada.id


def test_consultas_inexistentes_devuelven_resultados_vacios(app_context, repository):
    assert repository.find_by_id(9999) is None
    assert repository.find_by_postulacion_id(9999) is None
    assert repository.find_by_practicante_id(9999) == []


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
    practica.estado = Practica.ESTADO_FINALIZADA
    actualizada = repository.save(practica)

    assert actualizada.estado == Practica.ESTADO_FINALIZADA
    assert [item.archivo for item in actualizada.entregables] == [
        "primer-informe.pdf",
        "informe-final.pdf",
    ]
    assert [item.puntaje for item in actualizada.evaluaciones] == [65, 90]
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
    actualizada = repository.save(practica)

    assert [item.archivo for item in actualizada.entregables] == ["informe-2.pdf"]
    assert [item.puntaje for item in actualizada.evaluaciones] == [95]
    assert db.session.get(EntregableModel, entregable_eliminado_id) is None
    assert db.session.get(EvaluacionModel, evaluacion_eliminada_id) is None
