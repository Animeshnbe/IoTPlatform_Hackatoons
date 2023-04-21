from kafka import KafkaProducer
import json
import datetime
import os
from time import sleep

import configparser
config = configparser.ConfigParser()
config_file_path = os.path.join(os.path.dirname(__file__), 'config.ini')
config.read(config_file_path)
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
        sleep(5)
