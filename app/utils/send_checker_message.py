import smtplib
from email.message import EmailMessage
from app.config.read_config import EMAIL, TOKEN_EMAIL


def send_msg(imsg: str, email: str):
    password = TOKEN_EMAIL
    from_email = EMAIL
    msg = EmailMessage()
    msg['Subject'] = "Confirm password change "
    msg['From'] = from_email
    msg['To'] = email
    msg.set_content(imsg)
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(from_email, password)
        server.send_message(msg)
