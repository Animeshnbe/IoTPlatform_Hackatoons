import numpy as np
import pandas as pd
import csv
import random
import json
from time import sleep,time
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers=['localhost:19092'],
    value_serializer=lambda m: json.dumps(m).encode('ascii'))

# def produce(sensor,rate):
#     bootstrap_servers = ['localhost:19092']  # replace with your broker address
#     topic_name = 'ac_service'

#     while True:
#         data = {
#             'timestamp': int(time()),
#             'value': random.uniform(0, 100)
#         }
#         producer.send(topic_name, value=data)
#         sleep(1)

def produce(sensor,rate):
    df = pd.read_csv("../data/"+sensor+".csv")

    for _,row in df.iterrows():
        producer.send(sensor, value=row.to_dict())
        sleep(rate)
