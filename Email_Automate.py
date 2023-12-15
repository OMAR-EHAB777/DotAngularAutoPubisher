import smtplib
from email.message import EmailMessage
from pathlib import Path
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def send_email(subject, body, recipient_emails, sender, sender_password, image_path):
    """
    Sends an email with an attached image and HTML body to a list of recipients.

    Parameters:
    subject (str): The subject of the email.
    body (str): The HTML body of the email.
    recipient_emails (list): A list of recipient email addresses.
    sender (str): The sender's email address.
    sender_password (str): The sender's email password.
    image_path (str): Path to the image to be attached.
    """
    # Create the email message
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipient_emails)

    # Attach the body as HTML
    msg.add_alternative(body, subtype='html')

    # Attach the image
    if os.path.exists(image_path):
         with open(image_path, 'rb') as img:
             msg.get_payload()[0].add_related(img.read(), 'image', 'gif', cid=Path(image_path).stem)
    else:
        logging.warning(f"Image not found at {image_path}, sending email without image.")

    # Send the email
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender, sender_password)
        server.send_message(msg)
        server.quit()
    except smtplib.SMTPException as e:
        logging.error(f"Error sending email: {e}")
