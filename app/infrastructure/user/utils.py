import logging
import smtplib
import ssl
from email.message import EmailMessage

from flask import current_app
from flask_babel import _
from flask_mail import Message

logger = logging.getLogger(__name__)


def _send_smtp(app, msg: Message) -> None:
    """Send a Flask-Mail Message via raw SMTP (no debug output)."""
    em = EmailMessage()
    em.set_content(msg.body)
    em["To"] = ", ".join(msg.recipients)
    em["From"] = msg.sender
    em["Subject"] = msg.subject

    port = app.config["MAIL_PORT"]
    smtp_server = app.config["MAIL_SERVER"]
    sender_email = app.config["MAIL_USERNAME"]
    password = app.config["MAIL_PASSWORD"]

    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, port) as server:
        server.starttls(context=context)
        server.login(sender_email, password)
        server.send_message(em)

    logger.info("Email sent to %s", msg.recipients)


def send_password_mail(name: str, mail: str, username: str, password: str) -> None:
    subject = "{} {}".format(_("Correo de envío de credenciais de"), current_app.config["APP_TITLE"])
    mail_username = current_app.config["MAIL_USERNAME"].lower()
    response_address = current_app.config["MAIL_RESPONSE_ADDRESS"].lower()
    # Use MAIL_USERNAME as sender only if it looks like an email, otherwise use MAIL_RESPONSE_ADDRESS
    sender = mail_username if "@" in mail_username else response_address
    recipients = [mail]
    body_header = _("Adxúntanse as credenciais para que poida facer uso da aplicación dende os seus dispositivos.")
    body_footer = _(
        "Este correo foi enviado de modo automático e o "
        "enderezo do remitente non pode recibir respostas, se "
        "ten algunha duda o petición, póñase en "
        "contacto connosco no enderezo"
    )
    body = "{} {}:\n\n{}\n{}: {}\n{}: {}\n\n{} {}".format(
        _("Saudos"),
        name,
        body_header,
        _("Usuario"),
        username,
        _("Contrasinal"),
        password,
        body_footer,
        response_address,
    )

    msg = Message(subject=subject, sender=sender, recipients=recipients, body=body)

    # Rewrite Message-ID domain to match the response address
    aux_st = current_app.config["MAIL_RESPONSE_ADDRESS"].lower().split("@")[1]
    msg.msgId = "{}@{}".format(msg.msgId.split("@")[0], aux_st)

    if recipients:
        app = current_app._get_current_object()
        _send_smtp(app, msg)
