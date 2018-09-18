__author__ = "Akshen Doke"

import hashlib
import logging
import logging.config
import yaml
import re
from django.core.mail import send_mail
from textwrap import dedent
from random import randint
from smtplib import SMTP
from django.utils.crypto import get_random_string
from string import punctuation, digits
try:
    from string import letters
except ImportError:
    from string import ascii_letters as letters
from nccps2018.config import (
    EMAIL_HOST,
    EMAIL_PORT,
    EMAIL_HOST_USER,
    EMAIL_HOST_PASSWORD,
    EMAIL_USE_TLS,
    PRODUCTION_URL,
    SENDER_EMAIL,
    ADMIN_EMAIL
)
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from os import listdir, path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from time import sleep
from nccps2018.settings import LOG_FOLDER


def validateEmail(email):
    if len(email) > 7:
        if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$",
                    email) != None:
            return 1
        return 0


def generate_activation_key(username):
    """Generates hashed secret key for email activation"""
    chars = letters + digits + punctuation
    secret_key = get_random_string(randint(10, 40), chars)
    return hashlib.sha256((secret_key + username).encode('utf-8')).hexdigest()


def send_smtp_email(request=None, subject=None, message=None,
                    user_position=None, workshop_date=None,
                    workshop_title=None, user_name=None,
                    other_email=None, phone_number=None,
                    institute=None, attachment=None):
    '''
        Send email using SMTPLIB
    '''

    msg = MIMEMultipart()
    msg['From'] = EMAIL_HOST_USER
    msg['To'] = other_email
    msg['Subject'] = subject
    body = message
    msg.attach(MIMEText(body, 'plain'))

    if attachment:
        from django.conf import settings
        from os import listdir, path
        files = listdir(settings.MEDIA_ROOT)
        for f in files:
            attachment = open(path.join(settings.MEDIA_ROOT, f), 'rb')
            part = MIMEBase('application', 'octet-stream')
            part.set_payload((attachment).read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition',
                            "attachment; filename= %s " % f)
            msg.attach(part)

    server = SMTP(EMAIL_HOST, EMAIL_PORT)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.esmtp_features['auth'] = 'LOGIN DIGEST-MD5 PLAIN'
    server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
    text = msg.as_string()
    server.sendmail(EMAIL_HOST_USER, other_email, text)
    server.close()


def send_email(request, call_on,
               user_position=None, workshop_date=None,
               new_workshop_date=None,
               workshop_title=None, user_name=None,
               other_email=None, phone_number=None,
               institute=None, key=None
               ):
    '''
    Email sending function while registration and
    booking confirmation.
    '''
    try:
        with open(path.join(LOG_FOLDER, 'emailconfig.yaml'), 'r') as configfile:
            config_dict = yaml.load(configfile)
        logging.config.dictConfig(config_dict)
    except:
        print('File Not Found and Configuration Error')
        print(LOG_FOLDER)
    if call_on == "Registration":
        message = dedent("""\
                    Thank you for registering with us.

                    You can now proceed to propose a paper.

                    In case of queries regarding ticket booking and proposing a paper,
                    revert to this email.""".format(PRODUCTION_URL, key))
        try:
            send_mail(
                "NCCPS-2018 Registration at FOSSEE, IIT Bombay", message, SENDER_EMAIL,
                [request.user.email], fail_silently=True
            )

        except Exception:
            send_smtp_email(request=request,
                            subject="NCCPS-2018 Registration - FOSSEE, IIT Bombay",
                            message=message, other_email=request.user.email,
                            )