from kafka import KafkaConsumer
import json
import time
import threading
import smtplib
from mongo_utility import MongoUtility
from bson import json_util
from kafka import KafkaProducer
from kafka import KafkaConsumer

mongo_port = 27017
mongo_host = "localhost"
mongo_username = "root"
mongo_password = "dQFdN+kPl+I+hLKQEivugHTuzjgpERepxmUt6qMu3I51Kjljv9qGTeMgobr724dg"

kafkaPort = "9092"
kafkaAddress = "192.168.43.219:{}".format(kafkaPort)  # ProducerIP : ProducerPort


def send_data_to_sensor(host_topic, message):
    for i in host_topic:
        temp = i.split(' ')
        ip = temp[0]
        topic = temp[1]
        producer = KafkaProducer(bootstrap_servers=[ip])
        producer.send(topic, bytes(message, "utf-8"))
        producer.flush()
        time.sleep(1)


## https://myaccount.google.com/u/0/apppasswords
## https://myaccount.google.com/signinoptions/two-step-verification/enroll-welcome
def send_email(to, subject, text, receiver_email):
    gmail_user = 'nikhil.180410107039@gmail.com'
    gmail_app_password = 'oheowxctqofjxznn'

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
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_app_password)
        server.sendmail(sent_from, sent_to, email_text)
        server.close()

        print('Email sent!')
    except Exception as exception:
        print("Error: %s!\n\n" % exception)


def action_manager_request_handler(input_json):
    try:
        user_id = input_json["username"]
        service_name = input_json['servicename']
        application_config_file = input_json['application_config_file']
        service_id = input_json['service_id']
        host_topic = input_json['sensor_host']

        config_file_keys = application_config_file['Application']['services'].keys()
        for keys in config_file_keys:
            if application_config_file['Application']['services'][keys]['servicename'] == service_name:
                service_details = application_config_file['Application']['services'][keys]['action']
                break

        for i in application_config_file:
            sensor_host = []
            if i == 'send_output_to_sensor' and application_config_file[i]['value'] != "None":
                mongo_utility = MongoUtility(_mongo_port=mongo_port, _mongo_host=mongo_host)
                query_json = {"sensor_name": application_config_file[i]['sensor']}
                sensor_record = mongo_utility.find_json(query_json, "iot", "sensor")
                sensor_host.append(
                    str(sensor_record['sensor_host']['kafka']['kafka_broker_ip']) + " " + str(
                        sensor_record['sensor_host']['kafka']['kafka_topic']))

                # t = threading.Thread(target=send_data_to_sensor, args=(sensor_host, "message",))
                # t.start()
                send_data_to_sensor(sensor_host, "message")

            if i == 'Send_Email' and config_file_keys[i]['From'] != "None":
                to = application_config_file['Send_Email']['To']
                subject = application_config_file['Send_Email']['Subject']
                text = application_config_file['Send_Email']['Text']
                receiver_email = "amankhandelwaljuly@gmail.com"
                t = threading.Thread(target=send_email, args=(to, subject, text, receiver_email,))
                t.start()

            temp = {'ack': 'OK'}
            return temp

    except Exception as e:
        print(e)
