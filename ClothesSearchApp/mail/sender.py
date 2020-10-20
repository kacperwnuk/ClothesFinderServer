import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

port = 465  # For SSL
email = "clothes.search.app@gmail.com"
password = "clothessearchapp"

# Create a secure SSL context
context = ssl.create_default_context()


def create_message(body):
    message = MIMEMultipart()
    message["From"] = email
    message["To"] = email
    message["Subject"] = "Lista ulubionych ciuchów"

    # body = "Test message"

    message.attach(MIMEText(body, "plain"))
    return message


def send_mail(receiver_email, body):
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(email, password)

        message = create_message(body)
        server.sendmail(email, receiver_email, message.as_string())
