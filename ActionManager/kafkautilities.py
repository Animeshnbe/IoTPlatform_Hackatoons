from kafka import KafkaProducer
import json
from kafka import KafkaConsumer

def Produce(ip,port,topic,message):
    producer = KafkaProducer(bootstrap_servers=[ip+":"+port])
    producer.send(topic,value = json.dumps(message).encode('utf-8'))
def Consume(ip,port,offset,topiclist):
    consumer = KafkaConsumer(bootstrap_servers=[ip+":"+port],auto_offset_reset=offset,enable_auto_commit=True,value_deserializer=lambda x: x.decode('utf-8'))
    consumer.subscribe(topics=topiclist)
    responses = []
    for message in consumer:
        responses.append(message.value)
    consumer.close()


