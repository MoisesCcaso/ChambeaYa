import click
from flask import current_app

from application.email_delivery_error import EmailDeliveryError
from infrastructure.smtp_auth_email_sender import SmtpAuthEmailSender


def register_email_commands(app):
    @app.cli.command("test-email")
    @click.option(
        "--to",
        "recipient",
        required=True,
        help="Dirección que recibirá el correo de prueba.",
    )
    def test_email(recipient):
        """Comprueba la configuración SMTP enviando un correo real."""
        if current_app.config.get("MAIL_DELIVERY_MODE") != "smtp":
            raise click.ClickException(
                "MAIL_DELIVERY_MODE debe ser smtp para realizar una prueba real."
            )
        sender = SmtpAuthEmailSender.from_config(current_app.config)
        try:
            sender.send_test(recipient)
        except EmailDeliveryError as exc:
            raise click.ClickException(str(exc)) from exc
        click.echo(f"Correo de prueba enviado a {recipient}.")
