import pandas as pd
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

def produce(sensor,rate,instance=None):
    df = pd.read_csv("../data/"+sensor+".csv")

    for _,row in df.iterrows():
        if instance is None:
            # call_sensor_instance
            producer.send(sensor, key=None,value=row.to_dict())
        else:
            producer.send(sensor, key=instance,value=row.to_dict())
        sleep(rate)

if __name__=='__main__':
    produce("pressure",5)