import requests
import json
import time
import threading
from mongo_utility import MongoUtility
from bson import json_util
from datetime import datetime
from kafka import KafkaProducer
from notificationUtility import send_email
import configparser
from kafkautilities import kafka_consume, kafka_produce
from mongo_utility import MongoUtility

# Config file parser
parser = configparser.RawConfigParser(allow_no_value=True)
CONFIGURATION_FILE = "settings.conf"
parser.read([CONFIGURATION_FILE])

result = []
# mongo_port = int(parser.get("MONGO", "mongo_port"))
# mongo_host = parser.get("MONGO", "mongo_host")
mongo_port = 27017
mongo_host = "localhost"
#
# kafka_port = parser.get("KAFKA", "kafka_port")
# kafka_ip = parser.get("KAFKA", "kafka_ip")
# kafka_ip = "redpanda-0"
kafka_ip = "10.1.38.226"
kafka_port = "9092"
# kafkaPort = "9092"
# kafkaAddress = "192.168.43.219:{}".format(kafkaPort)  # ProducerIP : ProducerPort
kafkaAddress = kafka_ip + ":" + kafka_port
sensor_response_topic = "sensor_response"


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


def helper_function(user_id, device_id, new_value):
    try:
        # mongo_utility = MongoUtility(_mongo_port=mongo_port, _mongo_host=mongo_host)
        message = dict(user_id=user_id, device_id=device_id, new_value = new_value)
        topic = "action_device"
        # print("kafka_ip : ", kafka_ip)
        # print("kafka_port : ", kafka_port)
        # print("topic : ", topic)
        # print("message : ", message)
        kafka_produce(kafka_ip, kafka_port, topic, message)
        current_timestamp = datetime.now()
        message["current_timestamp"] = current_timestamp
        mongo_utility = MongoUtility(_mongo_port=mongo_port, _mongo_host=mongo_host)
        user_data = mongo_utility.insert_one(message, "iot", "action_logs")

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


def listening_to_sensor_manager():
    # response = kafka_consume(kafka_ip, kafka_port, "latest", [sensor_response_topic])
    res = requests.get(
        url=f"/consumers/test_group/instances/test_consumer2/records",
        params={"timeout": 1000, "max_bytes": 100000, "partition": 0, "offset": 1, },
        headers={"Accept": "application/vnd.kafka.json.v2+json"}).json()
    return res


def action_manager_request_handler(input_json):
    try:
        print(input_json)
        user_id = input_json.get("user_id", "")
        new_value = input_json.get("new_value", "None")
        device_id = input_json.get("device_id", "")
        th = threading.Thread(target=helper_function,
                              args=(user_id, device_id,new_value))
        th.start()
        # res = threading.Thread(target=listening_to_sensor_manager, args=(result,))
        # res.start()
        # res.join()
    except Exception as e:
        print(e)
