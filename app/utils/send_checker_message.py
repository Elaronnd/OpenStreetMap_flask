import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv


def send_msg(imsg: str, email: str):
    load_dotenv()
    password = os.getenv("PASSWORD")
    from_email = os.getenv("EMAIL")
    msg = EmailMessage()
    msg['Subject'] = "Confirm password change "
    # also we can hide it in yaml or whatever is comfortable ↓
    msg['From'] = from_email
    msg['To'] = email
    msg.set_content(imsg)
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(from_email, password)
        server.send_message(msg)
