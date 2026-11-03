"""I-02 - Pruebas del repositorio SQLAlchemy de usuarios con SQLite en memoria.

Código bajo prueba: infrastructure/sqlalchemy_usuario_repository.py
"""
from datetime import datetime, timedelta, timezone

from domain.auth.token_recuperacion import TokenRecuperacion
from domain.auth.usuario import Usuario
from infrastructure.sqlalchemy_usuario_repository import SqlAlchemyUsuarioRepository


def usuario_de_prueba(*, email="usuario@test.local", tipo=Usuario.TIPO_PRACTICANTE):
    return Usuario(
        email=email,
        password_hash="hash-prueba",
        tipo=tipo,
        estado=Usuario.ESTADO_PENDIENTE,
    )


def test_guardar_y_buscar_usuario_por_email(app_context):
    repository = SqlAlchemyUsuarioRepository()
    usuario = repository.save(usuario_de_prueba(email="ana@test.local"))

    encontrado = repository.find_by_email("ana@test.local")

    assert encontrado is not None
    assert encontrado.id == usuario.id
    assert encontrado.email == "ana@test.local"
    assert encontrado.tipo == Usuario.TIPO_PRACTICANTE
    assert encontrado.estado == Usuario.ESTADO_PENDIENTE


def test_guardar_y_buscar_usuario_por_identificador(app_context):
    repository = SqlAlchemyUsuarioRepository()
    usuario = repository.save(usuario_de_prueba(email="juan@test.local"))

    encontrado = repository.find_by_id(usuario.id)

    assert encontrado is not None
    assert encontrado.id == usuario.id
    assert encontrado.email == "juan@test.local"


def test_buscar_email_inexistente_devuelve_none(app_context):
    repository = SqlAlchemyUsuarioRepository()

    assert repository.find_by_email("no-existe@test.local") is None
    assert repository.find_by_id(99999) is None


def test_guardar_y_consultar_token_de_activacion(app_context):
    repository = SqlAlchemyUsuarioRepository()
    expiracion = datetime.now(timezone.utc) + timedelta(hours=48)
    usuario = usuario_de_prueba(email="activar@test.local")
    usuario.asignar_token_activacion(TokenRecuperacion("tok-activar", expiracion))
    guardado = repository.save(usuario)

    encontrado = repository.find_by_activation_token("tok-activar")

    assert encontrado is not None
    assert encontrado.id == guardado.id
    assert encontrado.activation_token == "tok-activar"
    assert encontrado.activation_token_expires_at == expiracion.replace(tzinfo=None)


def test_token_de_activacion_inexistente_devuelve_none(app_context):
    repository = SqlAlchemyUsuarioRepository()

    assert repository.find_by_activation_token("token-inexistente") is None


def test_guardar_y_consultar_token_de_recuperacion(app_context):
    repository = SqlAlchemyUsuarioRepository()
    expiracion = datetime.now(timezone.utc) + timedelta(hours=2)
    usuario = usuario_de_prueba(email="recuperar@test.local")
    usuario.asignar_token_recuperacion(TokenRecuperacion("tok-recuperar", expiracion))
    guardado = repository.save(usuario)

    encontrado = repository.find_by_password_reset_token("tok-recuperar")

    assert encontrado is not None
    assert encontrado.id == guardado.id
    assert encontrado.password_reset_token == "tok-recuperar"
    assert encontrado.password_reset_expires_at == expiracion.replace(tzinfo=None)


def test_token_de_recuperacion_inexistente_devuelve_none(app_context):
    repository = SqlAlchemyUsuarioRepository()

    assert repository.find_by_password_reset_token("token-inexistente") is None
