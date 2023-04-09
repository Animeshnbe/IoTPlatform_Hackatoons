from kafka import KafkaConsumer
import time
import json
from dotenv import load_dotenv
import os

load_dotenv()  # take environment variables from .env.

# kafkaIPPort = '52.15.89.83:9092'
kafkaPort = os.getenv("kafkaPort")
kafkaIP = os.getenv("kafkaAddress")
kafka_ip_port = kafkaIP + ":" + kafkaPort


# consumer_timeout_ms=10000 * 6 * 10

def monitor():
    consumer = KafkaConsumer(bootstrap_servers=[kafka_ip_port],
                             value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                             auto_offset_reset="latest", enable_auto_commit=True, consumer_timeout_ms=10000 * 6 * 10)
    consumer.subscribe(topics=['module_heart_rate'])
    print("kafka : ", kafka_ip_port)
    print("consumer : ", consumer)
    for message in consumer:
        # print(message.value)
        yield message.value
    print("outside")
