import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import click
from flask import current_app
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from werkzeug.security import generate_password_hash

from frameworks.sqlalchemy_orm.database import db
from frameworks.sqlalchemy_orm.models.convocatoria_model import ConvocatoriaModel
from frameworks.sqlalchemy_orm.models.empresa_model import EmpresaModel
from frameworks.sqlalchemy_orm.models.entregable_model import EntregableModel
from frameworks.sqlalchemy_orm.models.evaluacion_model import EvaluacionModel
from frameworks.sqlalchemy_orm.models.notificacion_model import NotificacionModel
from frameworks.sqlalchemy_orm.models.postulacion_model import PostulacionModel
from frameworks.sqlalchemy_orm.models.practicante_model import PracticanteModel
from frameworks.sqlalchemy_orm.models.practica_model import PracticaModel
from frameworks.sqlalchemy_orm.models.sugerencia_model import SugerenciaModel
from frameworks.sqlalchemy_orm.models.usuario_model import UsuarioModel


DEMO_PASSWORD = "Demo1234"
DEMO_PRACTITIONER_EMAIL = "practicante@demo.local"
DEMO_COMPANY_EMAIL = "empresa@demo.local"
DEMO_DELIVERABLE_NAME = "informe-avance-demo.pdf"


def _json_list(values):
    return json.dumps(values, ensure_ascii=False)


def _create_demo_pdf():
    upload_folder = Path(current_app.config["UPLOAD_FOLDER"])
    upload_folder.mkdir(parents=True, exist_ok=True)
    target = upload_folder / DEMO_DELIVERABLE_NAME
    if target.is_file():
        return

    pdf = canvas.Canvas(str(target), pagesize=A4)
    width, height = A4
    pdf.setTitle("Informe de avance de práctica")
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(72, height - 90, "Informe de avance de práctica")
    pdf.setFont("Helvetica", 11)
    text = pdf.beginText(72, height - 130)
    for line in (
        "Practicante: Andrea Quispe",
        "Actividad: Desarrollo de un módulo de reportes con Python y Flask.",
        "Estado: Entregable revisado para fines de demostración.",
    ):
        text.textLine(line)
    pdf.drawText(text)
    pdf.save()


def seed_demo_data():
    existing = UsuarioModel.query.filter(
        UsuarioModel.email.in_(
            [DEMO_PRACTITIONER_EMAIL, DEMO_COMPANY_EMAIL]
        )
    ).count()
    if existing:
        _create_demo_pdf()
        return False

    now = datetime.now(timezone.utc)
    password_hash = generate_password_hash(DEMO_PASSWORD)
    practitioner_user = UsuarioModel(
        email=DEMO_PRACTITIONER_EMAIL,
        password_hash=password_hash,
        tipo="practicante",
        estado="activo",
    )
    company_user = UsuarioModel(
        email=DEMO_COMPANY_EMAIL,
        password_hash=password_hash,
        tipo="empresa",
        estado="activo",
    )
    db.session.add_all([practitioner_user, company_user])
    db.session.flush()

    practitioner = PracticanteModel(
        usuario_id=practitioner_user.id,
        nombres="Andrea",
        apellidos="Quispe",
        dni="72483915",
        carnet_universitario="202612345",
        habilidades=_json_list(["Python", "Flask", "SQL", "Git", "Análisis de datos"]),
        formacion_educativa=_json_list(
            ["Ingeniería de Sistemas · Universidad Nacional de San Agustín"]
        ),
        score_reputacion=75.0,
        identidad_verificada=True,
    )
    company = EmpresaModel(
        usuario_id=company_user.id,
        razon_social="Innovación Andina S.A.C.",
        ruc="20100070970",
        verificada=True,
    )
    db.session.add_all([practitioner, company])
    db.session.flush()

    backend_opening = ConvocatoriaModel(
        empresa_id=company.id,
        titulo="Practicante de desarrollo backend",
        descripcion=(
            "Apoyo en el desarrollo de servicios web, pruebas y documentación "
            "de una plataforma empresarial."
        ),
        habilidades_requeridas=_json_list(["Python", "Flask", "SQL"]),
        beneficios=_json_list(["Mentoría técnica", "Horario flexible", "Constancia"]),
        estado="publicada",
        fecha_publicacion=now - timedelta(days=12),
    )
    data_opening = ConvocatoriaModel(
        empresa_id=company.id,
        titulo="Practicante de análisis de datos",
        descripcion=(
            "Preparación de datos, consultas SQL y elaboración de reportes "
            "para apoyar decisiones operativas."
        ),
        habilidades_requeridas=_json_list(["SQL", "Python", "Análisis de datos"]),
        beneficios=_json_list(["Capacitación", "Modalidad híbrida"]),
        estado="publicada",
        fecha_publicacion=now - timedelta(days=5),
    )
    qa_opening = ConvocatoriaModel(
        empresa_id=company.id,
        titulo="Practicante de aseguramiento de calidad",
        descripcion=(
            "Ejecución de pruebas funcionales y documentación de incidencias "
            "en aplicaciones web."
        ),
        habilidades_requeridas=_json_list(["Git", "SQL"]),
        beneficios=_json_list(["Mentoría", "Horario flexible"]),
        estado="publicada",
        fecha_publicacion=now - timedelta(days=2),
    )
    draft_opening = ConvocatoriaModel(
        empresa_id=company.id,
        titulo="Practicante de soporte de productos digitales",
        descripcion="Borrador preparado para demostrar la edición y publicación.",
        habilidades_requeridas=_json_list(["Comunicación", "Git"]),
        beneficios=_json_list(["Capacitación"]),
        estado="borrador",
    )
    db.session.add_all(
        [backend_opening, data_opening, qa_opening, draft_opening]
    )
    db.session.flush()

    selected_application = PostulacionModel(
        convocatoria_id=backend_opening.id,
        practicante_id=practitioner.id,
        estado="seleccionada",
    )
    pending_application = PostulacionModel(
        convocatoria_id=qa_opening.id,
        practicante_id=practitioner.id,
        estado="pendiente",
    )
    db.session.add_all([selected_application, pending_application])
    db.session.flush()

    practice = PracticaModel(
        postulacion_id=selected_application.id,
        practicante_id=practitioner.id,
        estado="EN_CURSO",
    )
    db.session.add(practice)
    db.session.flush()
    db.session.add_all(
        [
            EntregableModel(
                practica_id=practice.id,
                archivo=DEMO_DELIVERABLE_NAME,
                fecha_subida=now - timedelta(days=3),
            ),
            EvaluacionModel(
                practica_id=practice.id,
                puntaje=85.0,
                fecha_evaluacion=now - timedelta(days=1),
            ),
        ]
    )

    db.session.add_all(
        [
            SugerenciaModel(
                practicante_id=practitioner.id,
                convocatoria_id=data_opening.id,
                puntaje_match=100.0,
                habilidades_coincidentes=_json_list(
                    ["python", "sql", "análisis de datos"]
                ),
            ),
            SugerenciaModel(
                practicante_id=practitioner.id,
                convocatoria_id=qa_opening.id,
                puntaje_match=100.0,
                habilidades_coincidentes=_json_list(["git", "sql"]),
            ),
            NotificacionModel(
                usuario_destino_id=practitioner_user.id,
                tipo="EVALUACION_DISPONIBLE",
                mensaje="Tu práctica tiene una evaluación aprobada de 85 puntos",
                metadata_json=json.dumps({"practica_id": practice.id}),
                leida=False,
            ),
            NotificacionModel(
                usuario_destino_id=practitioner_user.id,
                tipo="NUEVAS_SUGERENCIAS",
                mensaje="Encontramos nuevas oportunidades compatibles con tu perfil",
                metadata_json=json.dumps({"cantidad": 2}),
                leida=False,
            ),
            NotificacionModel(
                usuario_destino_id=company_user.id,
                tipo="NUEVA_POSTULACION",
                mensaje="Tienes una postulación pendiente por revisar",
                metadata_json=json.dumps({"convocatoria_id": qa_opening.id}),
                leida=False,
            ),
        ]
    )

    db.session.commit()
    _create_demo_pdf()
    return True


def register_demo_commands(app):
    @app.cli.command("seed-demo")
    def seed_demo_command():
        """Carga cuentas y datos para la presentación local."""
        created = seed_demo_data()
        if created:
            click.secho("Datos de demostración creados correctamente.", fg="green")
        else:
            click.secho(
                "La demostración ya estaba preparada; no se duplicaron datos.",
                fg="yellow",
            )
        click.echo(f"Practicante: {DEMO_PRACTITIONER_EMAIL} / {DEMO_PASSWORD}")
        click.echo(f"Empresa:      {DEMO_COMPANY_EMAIL} / {DEMO_PASSWORD}")
