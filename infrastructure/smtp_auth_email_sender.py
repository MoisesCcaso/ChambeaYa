import logging
import smtplib
import ssl
from email.message import EmailMessage
from html import escape
from urllib.parse import urlencode

from application.email_delivery_error import EmailDeliveryError
from domain.auth.i_auth_email_sender import IAuthEmailSender


logger = logging.getLogger(__name__)


class SmtpAuthEmailSender(IAuthEmailSender):
    def __init__(
        self,
        *,
        delivery_mode="console",
        app_url="http://127.0.0.1:5000",
        server=None,
        port=587,
        username=None,
        password=None,
        use_tls=True,
        use_ssl=False,
        sender="ChambeaYa <no-reply@chambeaya.local>",
        timeout=15,
    ):
        self.delivery_mode = str(delivery_mode or "console").strip().lower()
        self.app_url = str(app_url).rstrip("/")
        self.server = server
        self.port = int(port)
        self.username = username
        self.password = password
        self.use_tls = bool(use_tls)
        self.use_ssl = bool(use_ssl)
        self.sender = sender
        self.timeout = int(timeout)

    @classmethod
    def from_config(cls, config):
        return cls(
            delivery_mode=config.get("MAIL_DELIVERY_MODE", "console"),
            app_url=config.get("APP_URL", "http://127.0.0.1:5000"),
            server=config.get("MAIL_SERVER"),
            port=config.get("MAIL_PORT", 587),
            username=config.get("MAIL_USERNAME"),
            password=config.get("MAIL_PASSWORD"),
            use_tls=config.get("MAIL_USE_TLS", True),
            use_ssl=config.get("MAIL_USE_SSL", False),
            sender=config.get(
                "MAIL_SENDER",
                "ChambeaYa <no-reply@chambeaya.local>",
            ),
            timeout=config.get("MAIL_TIMEOUT", 15),
        )

    def send_activation(self, recipient, token):
        link = self._build_link("/activar", token)
        self._send(
            recipient=recipient,
            subject="Activa tu cuenta de ChambeaYa",
            text=(
                "Gracias por registrarte en ChambeaYa.\n\n"
                f"Activa tu cuenta desde este enlace: {link}\n\n"
                "El enlace vence en 48 horas. Si no creaste esta cuenta, "
                "puedes ignorar este mensaje."
            ),
            heading="Activa tu cuenta",
            description=(
                "Confirma que esta dirección de correo te pertenece para "
                "comenzar a usar ChambeaYa."
            ),
            button_label="Activar mi cuenta",
            link=link,
            footer="Este enlace vence en 48 horas.",
        )

    def send_password_reset(self, recipient, token):
        link = self._build_link("/restablecer", token)
        self._send(
            recipient=recipient,
            subject="Restablece tu contraseña de ChambeaYa",
            text=(
                "Recibimos una solicitud para cambiar tu contraseña.\n\n"
                f"Continúa desde este enlace: {link}\n\n"
                "El enlace vence en 2 horas. Si no solicitaste el cambio, "
                "puedes ignorar este mensaje."
            ),
            heading="Restablece tu contraseña",
            description=(
                "Utiliza el siguiente enlace para definir una nueva contraseña."
            ),
            button_label="Cambiar contraseña",
            link=link,
            footer="Este enlace vence en 2 horas.",
        )

    def send_test(self, recipient):
        link = self.app_url
        self._send(
            recipient=recipient,
            subject="Prueba de correo de ChambeaYa",
            text=(
                "La conexión SMTP de ChambeaYa funciona correctamente.\n\n"
                f"Aplicación: {link}"
            ),
            heading="Configuración completada",
            description=(
                "ChambeaYa pudo conectarse con Gmail y entregar este correo."
            ),
            button_label="Abrir ChambeaYa",
            link=link,
            footer="Este es un mensaje de prueba; no necesitas realizar ninguna acción.",
        )

    def _build_link(self, path, token):
        return f"{self.app_url}{path}?{urlencode({'token': token})}"

    def _send(
        self,
        *,
        recipient,
        subject,
        text,
        heading,
        description,
        button_label,
        link,
        footer,
    ):
        if self.delivery_mode == "console":
            logger.info("Correo simulado para %s: %s", recipient, link)
            return
        if self.delivery_mode != "smtp":
            raise EmailDeliveryError("El modo de envío de correo no es válido")
        self._validate_smtp_config()

        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = self.sender
        message["To"] = recipient
        message.set_content(text)
        message.add_alternative(
            self._html_message(
                heading=heading,
                description=description,
                button_label=button_label,
                link=link,
                footer=footer,
            ),
            subtype="html",
        )

        try:
            if self.use_ssl:
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL(
                    self.server,
                    self.port,
                    timeout=self.timeout,
                    context=context,
                ) as smtp:
                    self._authenticate(smtp)
                    smtp.send_message(message)
                return

            with smtplib.SMTP(
                self.server,
                self.port,
                timeout=self.timeout,
            ) as smtp:
                smtp.ehlo()
                if self.use_tls:
                    smtp.starttls(context=ssl.create_default_context())
                    smtp.ehlo()
                self._authenticate(smtp)
                smtp.send_message(message)
        except (OSError, smtplib.SMTPException) as exc:
            logger.exception("No se pudo entregar un correo de autenticación")
            raise EmailDeliveryError(
                "No pudimos enviar el correo. Intenta reenviarlo en unos minutos."
            ) from exc

    def _authenticate(self, smtp):
        if self.username:
            smtp.login(self.username, self.password or "")

    def _validate_smtp_config(self):
        if not self.server:
            raise EmailDeliveryError(
                "El servidor SMTP no está configurado. Revisa las variables MAIL_*."
            )
        if any(
            "REEMPLAZA_CON_" in str(value or "")
            for value in (self.username, self.password, self.sender)
        ):
            raise EmailDeliveryError(
                "Completa MAIL_USERNAME, MAIL_PASSWORD y MAIL_SENDER en el archivo .env."
            )
        if self.username and not self.password:
            raise EmailDeliveryError(
                "La contraseña SMTP no está configurada."
            )

    def _html_message(
        self,
        *,
        heading,
        description,
        button_label,
        link,
        footer,
    ):
        safe_link = escape(link, quote=True)
        return f"""\
<!doctype html>
<html lang="es">
<body style="margin:0;padding:0;background:#f4f7fb;color:#102a43;font-family:Arial,sans-serif">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="padding:32px 16px">
    <tr>
      <td align="center">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width:560px;background:#ffffff;border:1px solid #d9e2ec">
          <tr>
            <td style="padding:26px 32px;border-bottom:3px solid #0062fc">
              <strong style="font-size:22px;color:#0062fc">ChambeaYa</strong>
            </td>
          </tr>
          <tr>
            <td style="padding:34px 32px">
              <h1 style="margin:0 0 14px;font-size:25px">{escape(heading)}</h1>
              <p style="margin:0 0 26px;line-height:1.65;color:#486581">{escape(description)}</p>
              <a href="{safe_link}" style="display:inline-block;padding:13px 20px;background:#0062fc;color:#ffffff;text-decoration:none;font-weight:700">{escape(button_label)}</a>
              <p style="margin:28px 0 0;font-size:13px;line-height:1.6;color:#829ab1">{escape(footer)}</p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""
