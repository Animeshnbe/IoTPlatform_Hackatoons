from kafka import KafkaProducer
import json
import datetime
from time import sleep
import threading
from kafkautilities import kafka_consume, kafka_produce
from dotenv import load_dotenv
import os
load_dotenv()
# kafkaIPPort = '52.15.89.83:9092'
# producer = KafkaProducer(bootstrap_servers=kafkaIPPort,
#                          value_serializer=lambda v: json.dumps(v).encode('utf-8')
#                          )

kafka_ip = os.getenv("kafka_ip")
kafka_port = os.getenv("kafka_port")


def heart_beat(module_name):
    while True:
        curr_time = str(datetime.datetime.utcnow())
        message = {
            'moduleName': module_name,
            'currentTime': curr_time
        }
        print("message : ", message)
        kafka_produce(kafka_ip, kafka_port, "module_heart_rate", message)
        # producer.send('monitor', message)
        sleep(5)


def monitor_thread(module_name):
    t = threading.Thread(target=heart_beat, args=(module_name,))
    t.daemon = True
    t.start()
