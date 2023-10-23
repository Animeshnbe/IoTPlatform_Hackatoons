from kafka import KafkaProducer
import json
import datetime
from time import sleep
import threading
from dotenv import load_dotenv
import os
load_dotenv()
# from kafkautilities import kafka_consume, kafka_produce

kafkaIPPort = os.getenv('kafka_host')
producer = KafkaProducer(bootstrap_servers=['10.2.135.69:9092'],
                         value_serializer=lambda v: json.dumps(v).encode('utf-8')
                         )

# kafka_ip = "192.168.43.219"
# kafka_port = "9092"


def heart_beat(module_name):
    while True:
        curr_time = str(datetime.datetime.utcnow())
        message = {
            'moduleName': module_name,
            'currentTime': curr_time
        }
        print("message : ", message)
        # kafka_produce(kafka_ip, kafka_port, "module_heart_rate", message)
        producer.send('module_heart_rate', message)
        sleep(5)


def monitor_thread(module_name):
    t = threading.Thread(target=heart_beat, args=(module_name,))
    t.daemon = True
    t.start()
