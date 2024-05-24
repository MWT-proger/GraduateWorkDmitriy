from email.message import EmailMessage
from typing import List

import aiosmtplib
from jinja2 import Environment, FileSystemLoader

from core.config import settings


class EmailService:
    def __init__(self):
        return

    async def get_server(self):
        server = aiosmtplib.SMTP(
            hostname=settings.EMAIL.HOST,
            port=settings.EMAIL.PORT,
            use_tls=True,
        )
        await server.connect()
        await server.login(
            settings.EMAIL.HOST_USER, settings.EMAIL.HOST_PASSWORD
        )
        return server

    def get_template(self, path_template: str):
        current_path = settings.EMAIL.TEMPLATES
        loader = FileSystemLoader(current_path)
        env = Environment(loader=loader)
        template = env.get_template(path_template)
        return template

    async def send_email(
        self, to: List[str], subject, payload_email: dict, path_template: str
    ):
        message = EmailMessage()
        message["From"] = settings.EMAIL.DEFAULT_FROM_EMAIL
        message["To"] = ", ".join(to)
        message["Subject"] = subject
        template = self.get_template(path_template)
        output = template.render(**payload_email)
        message.add_alternative(output, subtype="html")

        server = await self.get_server()
        try:
            await server.send_message(message)
        except aiosmtplib.SMTPException:
            return False
        finally:
            await server.quit()

        return True

    async def send_email_confirm(self, to: List[str], otp_code: str):
        subject = f"{otp_code} - подтверждение почты"
        payload_email = {"code": otp_code}
        path_template = "confirm_email.html"
        return await self.send_email(to, subject, payload_email, path_template)


def get_email_service() -> EmailService:
    return EmailService()
