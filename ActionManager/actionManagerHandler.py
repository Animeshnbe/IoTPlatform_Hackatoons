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
from kafkautilities import kafka_consume, kafka_produce

# Config file parser
parser = configparser.RawConfigParser(allow_no_value=True)
CONFIGURATION_FILE = "settings.conf"
parser.read([CONFIGURATION_FILE])

# mongo_port = int(parser.get("MONGO", "mongo_port"))
# mongo_host = parser.get("MONGO", "mongo_host")
#
# kafka_port = parser.get("KAFKA", "kafka_port")
# kafka_ip = parser.get("KAFKA", "kafka_ip")
# kafka_ip = "redpanda-0"
kafka_ip = "10.2.136.148"
kafka_port = "9092"
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


def helper_function(location_id, user_id, device_id, device_type, device_command):
    try:
        # mongo_utility = MongoUtility(_mongo_port=mongo_port, _mongo_host=mongo_host)
        message = dict(location_id=location_id, user_id=user_id, device_id=device_id, device_type=device_type,
                       device_command=device_command)
        topic = "action_device"
        # print("kafka_ip : ", kafka_ip)
        # print("kafka_port : ", kafka_port)
        # print("topic : ", topic)
        # print("message : ", message)
        kafka_produce(kafka_ip, kafka_port, topic, message)
    except Exception as e:
        print(e)


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
        print(input_json)
        location_id = input_json.get("location_id", "")
        user_id = input_json.get("user_id", "")
        device_id = input_json.get("device_id", "")
        device_type = input_json.get("device_type", "")
        device_command = input_json.get("device_command", "")
        th = threading.Thread(target=helper_function,
                              args=(location_id, user_id, device_id, device_type, device_command,))
        th.start()
        return {"response": "success"}
    except Exception as e:
        print(e)
