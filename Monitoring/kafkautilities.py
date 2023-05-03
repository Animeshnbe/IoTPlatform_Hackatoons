from kafka import KafkaProducer
import json
from kafka import KafkaConsumer


def kafka_produce(kafka_url, topic, message):
    try:
        producer = KafkaProducer(bootstrap_servers=[kafka_url])
        producer.send(topic, value=json.dumps(message).encode('utf-8'))
        print("Topic sent")
    except Exception as e:
        print(e)


def kafka_consume(ip, port, offset, topiclist):
    try:
        consumer = KafkaConsumer(bootstrap_servers=[ip + ":" + port], auto_offset_reset=offset, enable_auto_commit=True,
                                 value_deserializer=lambda x: x.decode('utf-8'))
        consumer.subscribe(topics=topiclist)
        responses = []
        for message in consumer:
            responses.append(message.value)
            break
        consumer.close()
        return responses
    except Exception as e:
        print(e)
        return "error"
