import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
RESET_PASSWORD_URL = os.getenv("RESET_PASSWORD_URL", "http://localhost:5173/reset-password")

def send_reset_password_email(to_email: str, token: str):
    reset_link = f"{RESET_PASSWORD_URL}?token={token}"

    subject = "Réinitialisation de votre mot de passe"
    body = f"""
    Bonjour,

    Vous avez demandé à réinitialiser votre mot de passe. Cliquez sur le lien ci-dessous pour continuer :

    {reset_link}

    Si vous n'avez pas fait cette demande, ignorez cet e-mail.

    Cordialement,
    L'équipe Support de SUPRSS
    """

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = SMTP_USERNAME
    msg["To"] = to_email
    msg.set_content(body)

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'e-mail : {e}")
