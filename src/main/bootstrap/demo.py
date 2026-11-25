import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import click
from flask import current_app
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from werkzeug.security import generate_password_hash

from shared.database import db
from recruitment.infrastructure.models.job_posting_model import JobPostingModel
from profiles.infrastructure.models.company_model import CompanyModel
from frameworks.sqlalchemy_orm.models.entregable_model import EntregableModel
from frameworks.sqlalchemy_orm.models.evaluacion_model import EvaluacionModel
from notifications.infrastructure.models.notification_model import NotificationModel
from recruitment.infrastructure.models.job_application_model import JobApplicationModel
from profiles.infrastructure.models.intern_model import InternModel
from frameworks.sqlalchemy_orm.models.practica_model import PracticaModel
from frameworks.sqlalchemy_orm.models.sugerencia_model import SugerenciaModel
from identity.infrastructure.models.user_model import UserModel


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
    _, height = A4
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


def seed_demo_data(password):
    existing = UserModel.query.filter(
        UserModel.email.in_(
            [DEMO_PRACTITIONER_EMAIL, DEMO_COMPANY_EMAIL]
        )
    ).count()
    if existing:
        _create_demo_pdf()
        return False

    now = datetime.now(timezone.utc)
    password_hash = generate_password_hash(password)
    practitioner_user = UserModel(
        email=DEMO_PRACTITIONER_EMAIL,
        password_hash=password_hash,
        role="practicante",
        status="activo",
    )
    company_user = UserModel(
        email=DEMO_COMPANY_EMAIL,
        password_hash=password_hash,
        role="empresa",
        status="activo",
    )
    db.session.add_all([practitioner_user, company_user])
    db.session.flush()

    practitioner = InternModel(
        user_id=practitioner_user.id,
        first_names="Andrea",
        last_names="Quispe",
        dni="72483915",
        university_id_card="202612345",
        skills=_json_list(["Python", "Flask", "SQL", "Git", "Análisis de datos"]),
        education=_json_list(
            ["Ingeniería de Sistemas · Universidad Nacional de San Agustín"]
        ),
        reputation_score=75.0,
        identity_verified=True,
    )
    company = CompanyModel(
        user_id=company_user.id,
        legal_name="Innovación Andina S.A.C.",
        ruc="20100070970",
        verified=True,
    )
    db.session.add_all([practitioner, company])
    db.session.flush()

    backend_opening = JobPostingModel(
        company_id=company.id,
        title="Practicante de desarrollo backend",
        description=(
            "Apoyo en el desarrollo de servicios web, pruebas y documentación "
            "de una plataforma empresarial."
        ),
        required_skills=_json_list(["Python", "Flask", "SQL"]),
        benefits=_json_list(["Mentoría técnica", "Horario flexible", "Constancia"]),
        status="publicada",
        published_at=now - timedelta(days=12),
    )
    data_opening = JobPostingModel(
        company_id=company.id,
        title="Practicante de análisis de datos",
        description=(
            "Preparación de datos, consultas SQL y elaboración de reportes "
            "para apoyar decisiones operativas."
        ),
        required_skills=_json_list(["SQL", "Python", "Análisis de datos"]),
        benefits=_json_list(["Capacitación", "Modalidad híbrida"]),
        status="publicada",
        published_at=now - timedelta(days=5),
    )
    qa_opening = JobPostingModel(
        company_id=company.id,
        title="Practicante de aseguramiento de calidad",
        description=(
            "Ejecución de pruebas funcionales y documentación de incidencias "
            "en aplicaciones web."
        ),
        required_skills=_json_list(["Git", "SQL"]),
        benefits=_json_list(["Mentoría", "Horario flexible"]),
        status="publicada",
        published_at=now - timedelta(days=2),
    )
    draft_opening = JobPostingModel(
        company_id=company.id,
        title="Practicante de soporte de productos digitales",
        description="Borrador preparado para demostrar la edición y publicación.",
        required_skills=_json_list(["Comunicación", "Git"]),
        benefits=_json_list(["Capacitación"]),
        status="borrador",
    )
    db.session.add_all(
        [backend_opening, data_opening, qa_opening, draft_opening]
    )
    db.session.flush()

    selected_application = JobApplicationModel(
        job_posting_id=backend_opening.id,
        intern_id=practitioner.id,
        status="seleccionada",
    )
    pending_application = JobApplicationModel(
        job_posting_id=qa_opening.id,
        intern_id=practitioner.id,
        status="pendiente",
    )
    db.session.add_all([selected_application, pending_application])
    db.session.flush()

    practice = PracticaModel(
        job_application_id=selected_application.id,
        intern_id=practitioner.id,
        status="EN_CURSO",
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
                intern_id=practitioner.id,
                job_posting_id=data_opening.id,
                puntaje_match=100.0,
                habilidades_coincidentes=_json_list(
                    ["python", "sql", "análisis de datos"]
                ),
            ),
            SugerenciaModel(
                intern_id=practitioner.id,
                job_posting_id=qa_opening.id,
                puntaje_match=100.0,
                habilidades_coincidentes=_json_list(["git", "sql"]),
            ),
            NotificationModel(
                recipient_user_id=practitioner_user.id,
                notification_type="EVALUACION_DISPONIBLE",
                message="Tu práctica tiene una evaluación aprobada de 85 puntos",
                metadata_json=json.dumps({"practica_id": practice.id}),
                is_read=False,
            ),
            NotificationModel(
                recipient_user_id=practitioner_user.id,
                notification_type="NUEVAS_SUGERENCIAS",
                message="Encontramos nuevas oportunidades compatibles con tu perfil",
                metadata_json=json.dumps({"cantidad": 2}),
                is_read=False,
            ),
            NotificationModel(
                recipient_user_id=company_user.id,
                notification_type="NUEVA_POSTULACION",
                message="Tienes una postulación pendiente por revisar",
                metadata_json=json.dumps({"convocatoria_id": qa_opening.id}),
                is_read=False,
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
        password = current_app.config.get("DEMO_PASSWORD")
        if not password:
            raise click.ClickException(
                "Define DEMO_PASSWORD en tu .env (ver .env.example)."
            )
        created = seed_demo_data(password)
        if created:
            click.secho("Datos de demostración creados correctamente.", fg="green")
        else:
            click.secho(
                "La demostración ya estaba preparada; no se duplicaron datos.",
                fg="yellow",
            )
        click.echo(f"Practicante: {DEMO_PRACTITIONER_EMAIL} / {password}")
        click.echo(f"Empresa:      {DEMO_COMPANY_EMAIL} / {password}")
