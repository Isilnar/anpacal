"""FlaskMailService — implementación de MailService usando Flask-Mail + SMTP directo."""

from app.domain.user.services import MailService
from app.infrastructure.user.utils import send_password_mail


class FlaskMailService(MailService):
    def send_credentials(self, email: str, username: str, password: str) -> None:
        """
        Envía credenciales al usuario.
        send_password_mail espera (name, mail, username, password) —
        usamos username como name cuando no tenemos el nombre disponible.
        """
        send_password_mail(name=username, mail=email, username=username, password=password)
