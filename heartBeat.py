from kafka import KafkaProducer
import json
import datetime
from time import sleep
import threading


kafkaIPPort = '10.2.135.69:9092'
producer = KafkaProducer(bootstrap_servers=[kafkaIPPort],
                         value_serializer=lambda v: json.dumps(v).encode('utf-8'))


def heart_beat(module_name):
    while True:
        curr_time = str(datetime.datetime.utcnow())
        message = {
            'moduleName': module_name,
            'currentTime': curr_time
        }
        print("message : ", message)
        producer.send('module_heart_rate', message)
        sleep(5)


def monitor_thread(module_name):
    t = threading.Thread(target=heart_beat, args=(module_name,))
    t.daemon = True
    t.start()
