from pathlib import  Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

from worker.config import celery
from core.email.sender import user_auth_sender, render_auth_template


@celery.task()
def send_user_verify_message(email: str, code: str):
    import asyncio

    async def wrapper():
        await user_auth_sender.connect()
        body = await render_auth_template("code_send.html", {"code": code})
        await user_auth_sender.send_email(
            sender_name="prac16 verifier",
            receiver_email=email,
            subject="Verify your email",
            body=body,
        )
        await user_auth_sender.disconnect()

    asyncio.run(wrapper())
