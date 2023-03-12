import socket

from kafka import KafkaAdminClient, KafkaProducer, KafkaConsumer
from kafka.admin import NewTopic
from kafka.errors import TopicAlreadyExistsError, KafkaError
import json


def create_topic(name,part=1):
    admin = KafkaAdminClient(bootstrap_servers="localhost:9092")
    try:
        demo_topic = NewTopic(name=name, num_partitions=part, replication_factor=1)
        admin.create_topics(new_topics=[demo_topic])
        print("Created topic")
    except TopicAlreadyExistsError as e:
        print("Topic already exists")
    finally:
        admin.close()

def on_success(metadata):
    print(f"Sent to topic '{metadata.topic}' at offset {metadata.offset}")
def on_error(e):
    print(f"Error sending message: {e}")

def produce(is_async=True):  
    producer = KafkaProducer(bootstrap_servers=" 10.2.132.235:9092")
    hostname = str.encode(socket.gethostname())

    # # Produce asynchronously
    # for i in range(100):
    #     msg = f"message #{i}"
    #     producer.send(
    #         "demo",
    #         key=hostname,
    #         value=str.encode(msg)
    #     )
    # producer.flush()

    # Produce asynchronously with callbacks
    if is_async:
        for i in range(100, 200):
            msg = f"message with callbacks #{i}"
            future = producer.send(
                "demo",
                key=hostname,
                value=str.encode(msg)
            )
            future.add_callback(on_success)
            future.add_errback(on_error)
        producer.flush()

    # Wait for every future to produce synchronously
    else:
        for i in range(200, 300):
            msg = f"synchronous message #{i}"
            future = producer.send(
                "demo",
                key=hostname,
                value=str.encode(msg)
            )
            try:
                metadata = future.get(timeout=5)
                print(f"Sent to topic '{metadata.topic}' at offset {metadata.offset}")
            except KafkaError as e:        
                print(f"Error sending message: {e}")
                pass

def new_consumer(name):
    consumer = KafkaConsumer(
        bootstrap_servers=["localhost:19092"],
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        consumer_timeout_ms=1000
    )
    consumer.subscribe(name)

    # consumer.seek(0,0)
    print("Waiting...")
    for message in consumer:
        topic_info = f"topic: {message.topic} ({message.partition}|{message.offset})"
        data = json.loads(message.value.decode('utf-8'))
        message_info = f"key: {message.key}, {data}"
        print(f"{topic_info}, {message_info}")
        print(data["timestamp"])

new_consumer('ac_service')