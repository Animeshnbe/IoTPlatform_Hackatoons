from kafka import KafkaProducer
import json
import datetime
import os
from time import sleep

from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


kafka = os.getenv("KAFKA_URI")

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
