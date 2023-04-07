from kafka import KafkaConsumer
import json
import time
import threading
from mongo_utility import MongoUtility
from bson import json_util
from kafka import KafkaProducer
from kafka import KafkaConsumer
from notificationUtility import send_email
import configparser

# Config file parser
parser = configparser.RawConfigParser(allow_no_value=True)
CONFIGURATION_FILE = "settings.conf"
parser.read([CONFIGURATION_FILE])


mongo_port = int(parser.get("MONGO", "mongo_port"))
mongo_host = parser.get("MONGO", "mongo_host")

kafka_port = parser.get("KAFKA", "kafka_port")
kafka_ip = parser.get("KAFKA", "kafka_ip")
# kafkaPort = "9092"
# kafkaAddress = "192.168.43.219:{}".format(kafkaPort)  # ProducerIP : ProducerPort
kafkaAddress = kafka_ip + ":" + kafka_port


def email_handler(to, subject, content):
    response = {}
    try:
        result = send_email(subject, content, to)
        if result == "Success":
            response["status"] = "OK"
            response["message"] = "Message sent successfully"
            return response
        else:
            response["status"] = "Fail"
            response["message"] = "Message not sent successfully"
            return response
    except Exception as e:
        print(e)
        response["status"] = "Fail"
        response["message"] = "Message not sent successfully"
        return response


def send_data_to_sensor(host_topic, message):
    for i in host_topic:
        temp = i.split(' ')
        ip = temp[0]
        topic = temp[1]
        producer = KafkaProducer(bootstrap_servers=[ip])
        producer.send(topic, bytes(message, "utf-8"))
        producer.flush()
        time.sleep(1)


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
