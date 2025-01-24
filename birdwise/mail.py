from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from flask import url_for
from models import User
from sendmail import send_email
from app import app

from dotenv import load_dotenv
from email.message import EmailMessage
import os
import smtplib
mail_username = os.getenv("MAIL_USERNAME")
mail_password = os.getenv("MAIL_PASSWORD")
mail_server = os.getenv("MAIL_SERVER")
mail_port = os.getenv("MAIL_PORT")

def send_email(to_email, subject, body):
    # Create the email
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = mail_username
    msg['To'] = to_email
    msg.set_content(body)

    # Connect to SMTP server and send email
    with smtplib.SMTP(mail_server, mail_port) as server:
        server.starttls()  # Upgrade the connection to secure
        server.login(mail_username, mail_password)
        server.send_message(msg)

mail = Mail(app)
# created an instance of the Mail