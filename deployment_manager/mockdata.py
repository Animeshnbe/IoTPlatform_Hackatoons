import pandas as pd
import random
import json
from time import sleep
from kafka import KafkaAdminClient, KafkaProducer
from kafka.admin import NewTopic
from kafka.errors import TopicAlreadyExistsError, KafkaError
import json
import configparser
config = configparser.ConfigParser()
config.read('.env')
configs = config['local']

IP = configs["KAFKA_URI"]

def create_topic(name,part=1):
    # print(IP)
    admin = KafkaAdminClient(bootstrap_servers=[IP])
    try:
        demo_topic = NewTopic(name=name, num_partitions=part, replication_factor=1)
        admin.create_topics(new_topics=[demo_topic])
        print("Created topic")
    except TopicAlreadyExistsError as e:
        print("Topic already exists")
    finally:
        admin.close()

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
    # df = pd.read_csv("../data/"+sensor+".csv")

    # create_topic(sensor)
    producer = KafkaProducer(
        bootstrap_servers=[IP],
        value_serializer=lambda m: json.dumps(m).encode('ascii'))
    # for _,row in df.iterrows():
    while True:
        if instance is None:
            # call_sensor_instance
            producer.send(sensor, key=None,value={"content":random.randint(1,100)})
        else:
            # producer.send(sensor, key=instance,value=row.to_dict())
            pass
        sleep(rate)

if __name__=='__main__':
    produce("neuter",0.1)