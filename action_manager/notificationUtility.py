import sys
import smtplib
import configparser
import json
from twilio.rest import Client
from dotenv import load_dotenv
import os

# account_sid = 'AC1380002ba0e2b44a4e373592ae725925'
# auth_token = 'da0da81c06f4c2b6775f0744016b95a4'

# Config file parser
# parser = configparser.RawConfigParser(allow_no_value=True)
# CONFIGURATION_FILE = "settings.conf"
# parser.read([CONFIGURATION_FILE])
load_dotenv()


def send_email(subject, text, receiver_email):
    '''
    Sends email
    https://myaccount.google.com/u/0/apppasswords
    https://myaccount.google.com/signinoptions/two-step-verification/enroll-welcome
    :param subject: string
    :param text: string
    :param receiver_email: string
    :return: response
    '''
    gmail_user = os.getenv("email_sender")
    # gmail_user = parser.get("EMAIL", "email_sender")
    # gmail_app_password = parser.get("EMAIL", "email_password")
    gmail_app_password = os.getenv("email_password")

    sent_from = gmail_user
    sent_to = [receiver_email]
    sent_subject = subject
    sent_body = text

    email_text = """\
    From: %s
    To: %s

    %s
    """ % (sent_from, ", ".join(sent_to), sent_body)

    message = 'Subject: {}\n\n{}'.format(sent_subject, email_text)
    try:
        # smtp_host = parser.get("EMAIL", "smtp_host")
        smtp_host = os.getenv("smtp_host")
        # smtp_port = int(parser.get("EMAIL", "smtp_port"))
        smtp_port = os.getenv("smtp_port")
        server = smtplib.SMTP_SSL(smtp_host, smtp_port)
        server.ehlo()
        server.login(gmail_user, gmail_app_password)
        server.sendmail(sent_from, sent_to, message)
        server.close()

        print('Email sent!')
        return "Success"
    except Exception as exception:
        print("Error: %s!\n\n" % exception)
        return "Error"


# from_number = 15076323386
# to_number = 919898604066
def send_sms(to_number, message):
    try:
        account_sid = os.getenv("account_sid")
        auth_token = os.getenv("auth_token")
        from_number = os.getenv("from_number")
        client = Client(account_sid, auth_token)
        message = client.messages.create(body=message, from_=from_number, to=int(to_number))
        print(message.sid)
        return "Success"
    except Exception as exception:
        print("Error: %s!\n\n" % exception)
        return "Error"
# send_sms(919898604066,"Hi Nikhil Khemchandani,From Hackatoons")
# send_email("Hackatoons","Hi Nikhil Khemchandani,From Hackatoons","nikhilkhemchandani5@gmail.com")
