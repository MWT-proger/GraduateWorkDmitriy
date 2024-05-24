import smtplib
from email.message import EmailMessage
from typing import List

from jinja2 import Environment, FileSystemLoader

from core.config import settings


class EmailService:
    def __init__(self):
        return

    def get_server(self):
        server = smtplib.SMTP_SSL(settings.EMAIL.HOST, settings.EMAIL.PORT)
        server.login(settings.EMAIL.HOST_USER, settings.EMAIL.HOST_PASSWORD)
        return server

    def get_template(self, path_template: str):
        current_path = settings.EMAIL.TEMPLATES
        loader = FileSystemLoader(current_path)
        env = Environment(loader=loader)
        template = env.get_template(path_template)
        return template

    def send_email(
        self, to: List[str], subject, payload_email: dict, path_template: str
    ):
        message = EmailMessage()
        message["From"] = settings.EMAIL.DEFAULT_FROM_EMAIL
        message["To"] = to
        message["Subject"] = subject
        template = self.get_template(path_template)
        output = template.render(**payload_email)
        message.add_alternative(output, subtype="html")

        server = self.get_server()
        try:
            server.sendmail(
                settings.EMAIL.DEFAULT_FROM_EMAIL, to, message.as_string()
            )
        except smtplib.SMTPException:
            return False
        else:
            pass
        finally:
            server.close()

        return True

    def send_email_confirm(self, to: List[str], otp_code: str):
        subject = f"{otp_code} - подтверждение почты"
        payload_email = {"code": otp_code}
        path_template = "confirm_email.html"
        return self.send_email(to, subject, payload_email, path_template)


def get_email_service() -> EmailService:
    return EmailService()
