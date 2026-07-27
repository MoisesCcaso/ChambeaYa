# application/notificacion_application_service.py
from typing import List, Dict, Optional
from datetime import datetime
from domain.notificacion.i_notificacion_repository import Notificacion, INotificacionRepository
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging

logger = logging.getLogger(__name__)

class NotificacionApplicationService:
    """Servicio de aplicación para la gestión de notificaciones."""

    def __init__(self, notificacion_repo: INotificacionRepository):
        self.notificacion_repo = notificacion_repo

    def enviar_correo(self, destino: str, asunto: str, mensaje: str, html: str = None) -> bool:
        """Envía un correo electrónico."""
        try:
            smtp_server = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
            smtp_port = int(os.getenv('MAIL_PORT', 587))
            smtp_user = os.getenv('MAIL_USERNAME')
            smtp_password = os.getenv('MAIL_PASSWORD')

            if not smtp_user or not smtp_password:
                logger.warning("Credenciales de correo no configuradas")
                return False

            msg = MIMEMultipart('alternative')
            msg['Subject'] = asunto
            msg['From'] = smtp_user
            msg['To'] = destino

            # Parte en texto plano
            msg.attach(MIMEText(mensaje, 'plain'))

            # Parte en HTML
            if html:
                msg.attach(MIMEText(html, 'html'))

            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.sendmail(smtp_user, [destino], msg.as_string())

            return True
        except Exception as e:
            logger.error(f"Error al enviar correo: {str(e)}")
            return False

    def crear_notificacion(self, usuario_id: int, canal: str, asunto: str,
                           mensaje: str, mensaje_html: str = None,
                           metadata: Dict = None) -> Notificacion:
        """Crea una notificación in-app."""
        notificacion = Notificacion(
            id=None,
            usuario_id=usuario_id,
            tipo='in-app',
            canal=canal,
            asunto=asunto,
            mensaje=mensaje,
            mensaje_html=mensaje_html,
            leida=False,
            fecha_envio=datetime.utcnow(),
            fecha_lectura=None,
            metadata=metadata or {}
        )
        return self.notificacion_repo.guardar(notificacion)

    def enviar_notificacion(self, usuario_id: int, email: str, canal: str,
                            asunto: str, mensaje: str, mensaje_html: str = None,
                            metadata: Dict = None) -> Optional[Notificacion]:
        """Envía una notificación (correo + in-app)."""
        # 1. Crear notificación in-app
        notificacion = self.crear_notificacion(
            usuario_id=usuario_id,
            canal=canal,
            asunto=asunto,
            mensaje=mensaje,
            mensaje_html=mensaje_html,
            metadata=metadata
        )

        # 2. Enviar correo
        self.enviar_correo(email, asunto, mensaje, mensaje_html)

        return notificacion

    def obtener_notificaciones(self, usuario_id: int, limit: int = 50) -> List[Dict]:
        """Obtiene las notificaciones de un usuario."""
        notificaciones = self.notificacion_repo.obtener_por_usuario(usuario_id, limit)
        return [n.to_dict() for n in notificaciones]

    def obtener_no_leidas(self, usuario_id: int) -> List[Dict]:
        """Obtiene las notificaciones no leídas de un usuario."""
        notificaciones = self.notificacion_repo.obtener_no_leidas(usuario_id)
        return [n.to_dict() for n in notificaciones]

    def marcar_como_leida(self, notificacion_id: int, usuario_id: int) -> Dict:
        """Marca una notificación como leída."""
        notificacion = self.notificacion_repo.marcar_como_leida(notificacion_id)
        if not notificacion:
            raise ValueError("Notificación no encontrada")
        if notificacion.usuario_id != usuario_id:
            raise PermissionError("No tienes permiso para modificar esta notificación")
        return notificacion.to_dict()

    def marcar_todas_como_leidas(self, usuario_id: int) -> int:
        """Marca todas las notificaciones de un usuario como leídas."""
        return self.notificacion_repo.marcar_todas_como_leidas(usuario_id)

    # Métodos específicos para diferentes tipos de notificaciones

    def notificar_postulacion_creada(self, practicante_id: int, email: str,
                                     convocatoria_titulo: str, postulacion_id: int) -> None:
        """Notifica que se ha creado una postulación."""
        asunto = f"Postulación creada: {convocatoria_titulo}"
        mensaje = f"Te has postulado exitosamente a la convocatoria '{convocatoria_titulo}'."
        html = f"""
        <h2>¡Postulación exitosa!</h2>
        <p>Te has postulado a la convocatoria <strong>{convocatoria_titulo}</strong>.</p>
        <p>La empresa revisará tu perfil y te contactará.</p>
        """
        self.enviar_notificacion(
            usuario_id=practicante_id,
            email=email,
            canal='postulacion',
            asunto=asunto,
            mensaje=mensaje,
            mensaje_html=html,
            metadata={"postulacion_id": postulacion_id}
        )

    def notificar_postulacion_aceptada(self, practicante_id: int, email: str,
                                       convocatoria_titulo: str, postulacion_id: int) -> None:
        """Notifica que una postulación ha sido aceptada."""
        asunto = f"¡Postulación aceptada! - {convocatoria_titulo}"
        mensaje = f"Tu postulación a '{convocatoria_titulo}' ha sido aceptada. ¡Felicidades!"
        html = f"""
        <h2>¡Postulación aceptada!</h2>
        <p>Tu postulación a <strong>{convocatoria_titulo}</strong> ha sido <strong>aceptada</strong>.</p>
        <p>Pronto recibirás más información sobre el inicio de tu práctica.</p>
        """
        self.enviar_notificacion(
            usuario_id=practicante_id,
            email=email,
            canal='postulacion',
            asunto=asunto,
            mensaje=mensaje,
            mensaje_html=html,
            metadata={"postulacion_id": postulacion_id}
        )

    def notificar_postulacion_rechazada(self, practicante_id: int, email: str,
                                        convocatoria_titulo: str, postulacion_id: int) -> None:
        """Notifica que una postulación ha sido rechazada."""
        asunto = f"Actualización de postulación - {convocatoria_titulo}"
        mensaje = f"Tu postulación a '{convocatoria_titulo}' ha sido rechazada."
        html = f"""
        <h2>Postulación rechazada</h2>
        <p>Tu postulación a <strong>{convocatoria_titulo}</strong> ha sido <strong>rechazada</strong>.</p>
        <p>No te desanimes, sigue postulando a otras convocatorias.</p>
        """
        self.enviar_notificacion(
            usuario_id=practicante_id,
            email=email,
            canal='postulacion',
            asunto=asunto,
            mensaje=mensaje,
            mensaje_html=html,
            metadata={"postulacion_id": postulacion_id}
        )

    def notificar_nueva_convocatoria(self, practicantes: List[Dict],
                                     convocatoria_titulo: str, convocatoria_id: int) -> None:
        """Notifica a practicantes sobre una nueva convocatoria."""
        for p in practicantes:
            asunto = f"Nueva convocatoria: {convocatoria_titulo}"
            mensaje = f"Se ha publicado una nueva convocatoria: '{convocatoria_titulo}'"
            html = f"""
            <h2>¡Nueva convocatoria disponible!</h2>
            <p>Se ha publicado la convocatoria <strong>{convocatoria_titulo}</strong>.</p>
            <p>Revisa si coincide con tu perfil y postula.</p>
            """
            self.enviar_notificacion(
                usuario_id=p['id'],
                email=p['email'],
                canal='convocatoria',
                asunto=asunto,
                mensaje=mensaje,
                mensaje_html=html,
                metadata={"convocatoria_id": convocatoria_id}
            )

    def notificar_certificado_generado(self, practicante_id: int, email: str,
                                       certificado_codigo: str, practica_titulo: str) -> None:
        """Notifica que se ha generado un certificado."""
        asunto = f"Tu certificado de práctica está listo"
        mensaje = f"Se ha generado tu certificado para '{practica_titulo}'."
        html = f"""
        <h2>¡Certificado generado!</h2>
        <p>Se ha generado tu certificado para <strong>{practica_titulo}</strong>.</p>
        <p>Código: <strong>{certificado_codigo}</strong></p>
        <p>Puedes verificarlo en cualquier momento.</p>
        """
        self.enviar_notificacion(
            usuario_id=practicante_id,
            email=email,
            canal='sistema',
            asunto=asunto,
            mensaje=mensaje,
            mensaje_html=html,
            metadata={"certificado_codigo": certificado_codigo}
        )

    def notificar_recordatorio_entrega(self, practicante_id: int, email: str,
                                       entregable_titulo: str, fecha_limite: str,
                                       entregable_id: int) -> None:
        """Notifica un recordatorio de entrega de documento."""
        asunto = f"Recordatorio: {entregable_titulo} - {fecha_limite}"
        mensaje = f"Recuerda entregar '{entregable_titulo}' antes del {fecha_limite}."
        html = f"""
        <h2>Recordatorio de entrega</h2>
        <p>Recuerda entregar <strong>{entregable_titulo}</strong>.</p>
        <p>Fecha límite: <strong>{fecha_limite}</strong></p>
        <p>¡No olvides subir tu documento!</p>
        """
        self.enviar_notificacion(
            usuario_id=practicante_id,
            email=email,
            canal='recordatorio',
            asunto=asunto,
            mensaje=mensaje,
            mensaje_html=html,
            metadata={"entregable_id": entregable_id}
        )