#!/Users/imrp26/.pyenv/shims/python3


from json import loads
from kafka import KafkaConsumer


consumer = KafkaConsumer('foobar', bootstrap_servers=['localhost:29092'], api_version=(0, 10))

for message in consumer:
    print (message.value)
