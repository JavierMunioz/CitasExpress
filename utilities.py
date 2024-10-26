import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv
from jinja2 import Template

load_dotenv()

def send_email(by, to, affair, text):
    # Configuración del servidor SMTP de Gmail
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    password = os.getenv('PASSWORD_EMAIL')  # Reemplaza con tu contraseña o contraseña de aplicación



    # Crear el objeto del mensaje
    msg = MIMEMultipart()
    msg['From'] = by
    msg['To'] = to
    msg['Subject'] = affair
    msg.attach(MIMEText(text, 'plain'))

    try:
        # Conectar al servidor SMTP y enviar el correo
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Iniciar TLS
        server.login(by, password)
        server.send_message(msg)
        print("Correo enviado con éxito.")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")
    finally:
        server.quit()


def send_code(by, to, affair, text):
    # Configuración del servidor SMTP de Gmail
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    password = os.getenv('PASSWORD_EMAIL')  # Reemplaza con tu contraseña o contraseña de aplicación

    with open('./static/code_verification.html', 'r', encoding='utf-8') as file:
        template =  Template(file.read())

    html = template.render(
        code = text
    )

    # Crear el objeto del mensaje
    msg = MIMEMultipart()
    msg['From'] = by
    msg['To'] = to
    msg['Subject'] = affair
    msg.attach(MIMEText(html, 'html',  'utf-8'))

    try:
        # Conectar al servidor SMTP y enviar el correo
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Iniciar TLS
        server.login(by, password)
        server.send_message(msg)
        print("Correo enviado con éxito.")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")
    finally:
        server.quit()
