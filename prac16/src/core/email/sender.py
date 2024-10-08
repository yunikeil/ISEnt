from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
import logging
from pathlib import Path

import aiosmtplib
from jinja2 import Environment, FileSystemLoader

from core.settings import  config

logger = logging.getLogger("uvicorn")
templates = Path(__file__).parents[2] / "templates"

# Логику пуллов бы сюда, но да ладно
class AsyncEmailSender:
    def __init__(self, smtp_server, smtp_port, username, password):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.server = None

    async def connect(self):
        self.server: aiosmtplib.SMTP = aiosmtplib.SMTP()
        await self.server.connect(hostname=self.smtp_server, port=self.smtp_port, use_tls=True, timeout=2)
        await self.server.login(self.username, self.password)

    async def send_email(self, sender_name, receiver_email, subject, body):
        await self.connect()
        if not self.server:
            raise ValueError(f"SMTP server must be {type(aiosmtplib.SMTP)}, not N+one")
        message = MIMEMultipart("alternative")
        message["From"] = formataddr((str(Header(sender_name, "utf-8")), self.username))
        message["To"] = receiver_email
        message["Subject"] = subject
        message["X-Image-URL"] = "https://avatars.githubusercontent.com/u/151668482"
        message.attach(MIMEText(body, "html"))

        await self.server.sendmail(self.username, receiver_email, message.as_string())
        await self.disconnect()

    async def disconnect(self):
        if self.server.is_connected:
            await self.server.quit()


async def render_auth_template(template_file, data: dict, **kwargs):
    if not (path := kwargs.get("templates_path")):
        env = Environment(loader=FileSystemLoader(templates), enable_async=True)
    else:
        env = Environment(loader=FileSystemLoader(path), enable_async=True)

    template = env.get_template(template_file)
    rendered_html = await template.render_async(data)

    return rendered_html


user_auth_sender = AsyncEmailSender(
    config.SMTP_ADRESS,
    config.SMTP_SSL_PORT,
    config.USER_VERIFY_LOGIN,
    config.USER_VERIFY_PASSWORD.get_secret_value(),
)

password_reset_sender = AsyncEmailSender(
    config.SMTP_ADRESS,
    config.SMTP_SSL_PORT,
    config.PASSWORD_RESET_LOGIN,
    config.PASSWORD_RESET_PASSWORD.get_secret_value(),
)
