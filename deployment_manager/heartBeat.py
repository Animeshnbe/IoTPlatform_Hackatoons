from kafka import KafkaProducer
import json
import datetime
import threading

import configparser
config = configparser.ConfigParser()
config.read('.env')
configs = config['local']


kafka = configs["KAFKA_URI"]

def heart_beat(module_name):
    producer = KafkaProducer(
        bootstrap_servers=[kafka],
        value_serializer=lambda m: json.dumps(m).encode('ascii'))
    while True:
        curr_time = str(datetime.datetime.utcnow())
        message = {
            'moduleName': module_name,
            'currentTime': curr_time
        }
        producer.send('module_heart_rate', key=None,value=message)
