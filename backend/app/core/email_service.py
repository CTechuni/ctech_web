import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader, select_autoescape
import os
from app.core.config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

class EmailService:
    def __init__(self):
        # Configuración de Jinja2 para las plantillas
        template_dir = os.path.join(os.path.dirname(__file__), "templates")
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = settings.GMAIL_USER
        self.sender_password = settings.GMAIL_PASSWORD

    def _send_email(self, recipient_email: str, subject: str, html_content: str):
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"CTech Platform <{self.sender_email}>"
            message["To"] = recipient_email

            part = MIMEText(html_content, "html")
            message.attach(part)

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, recipient_email, message.as_string())
            
            logger.info(f"Email enviado exitosamente a {recipient_email}")
            return True
        except Exception as e:
            logger.error(f"Error al enviar email a {recipient_email}: {str(e)}")
            return False

    def send_welcome_email(self, recipient_email: str, name_user: str, name_community: str):
        try:
            template = self.env.get_template("welcome.html")
            html_content = template.render(
                name_user=name_user,
                name_community=name_community,
                platform_url=settings.PLATFORM_URL
            )
            return self._send_email(recipient_email, "¡Bienvenido a CTech!", html_content)
        except Exception as e:
            logger.error(f"Error al renderizar plantilla de bienvenida: {str(e)}")
            return False



    def send_event_registration_email(self, recipient_email: str, name_user: str, event_name: str, event_date: str, event_time: str, event_type: str, name_community: str):
        try:
            template = self.env.get_template("event_registration.html")
            html_content = template.render(
                name_user=name_user,
                event_name=event_name,
                event_date=event_date,
                event_time=event_time,
                event_type=event_type,
                name_community=name_community,
                event_link=f"{settings.PLATFORM_URL}/user/events"
            )
            return self._send_email(recipient_email, f"Confirmación: Registro a {event_name}", html_content)
        except Exception as e:
            logger.error(f"Error al renderizar plantilla de registro a evento: {str(e)}")
            return False

    def send_reset_password_email(self, recipient_email: str, name_user: str, token: str):
        try:
            template = self.env.get_template("reset_password.html")
            reset_link = f"{settings.PLATFORM_URL}/reset-password?email={recipient_email}&token={token}"
            html_content = template.render(
                name_user=name_user,
                reset_link=reset_link,
                platform_url=settings.PLATFORM_URL
            )
            return self._send_email(recipient_email, "Recuperación de Contraseña - CTech", html_content)
        except Exception as e:
            logger.error(f"Error al renderizar plantilla de recuperación de contraseña: {str(e)}")
            return False

email_service = EmailService()
