import sys
import smtplib
import configparser
import json

# Config file parser
parser = configparser.RawConfigParser(allow_no_value=True)
CONFIGURATION_FILE = "settings.conf"
parser.read([CONFIGURATION_FILE])


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
    # gmail_user = 'nikhil.180410107039@gmail.com'
    gmail_user = parser.get("EMAIL", "email_sender")
    gmail_app_password = parser.get("EMAIL", "email_password")
    # gmail_app_password = 'oheowxctqofjxznn'

    sent_from = gmail_user
    sent_to = [receiver_email]
    sent_subject = subject
    sent_body = text

    email_text = """\
    From: %s
    To: %s
    Subject: %s

    %s
    """ % (sent_from, ", ".join(sent_to), sent_subject, sent_body)

    try:
        smtp_host = parser.get("EMAIL", "smtp_host")
        smtp_port = int(parser.get("EMAIL", "smtp_port"))
        server = smtplib.SMTP_SSL(smtp_host, smtp_port)
        server.ehlo()
        server.login(gmail_user, gmail_app_password)
        server.sendmail(sent_from, sent_to, email_text)
        server.close()

        print('Email sent!')
        return "Success"
    except Exception as exception:
        print("Error: %s!\n\n" % exception)
        return "Error"
