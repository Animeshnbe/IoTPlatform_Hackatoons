import requests
import json
import configparser
config = configparser.ConfigParser()
config.read('.env')
configs = config['local']

base_uri = configs["KAFKA_REST"]

def pretty(text):
  print(json.dumps(text, indent=2))
  
def check_request(worklist, consumer_group, name="test"):
  with open("kafka_rest.py","w") as f:
  
  # get_all_sensors()
  devices = 
  consume = False
  produce = []
  for item in worklist:
    if item["type"]=="controller":
      produce.append(item[''])

      

    # f.write(f'''
  # res = requests.get(f"{base_uri}/topics").json()
pretty(res)

# Register consumer
# res = requests.post(
#     url=f"{base_uri}/consumers/test_group",
#     data=json.dumps({
#         "name": "test_consumer2",
#         "format": "json",
#         "auto.offset.reset": "earliest",
#         "auto.commit.enable": "false",
#         "fetch.min.bytes": "1",
#         "consumer.request.timeout.ms": "10000"
#     }),
#     headers={"Content-Type": "application/vnd.kafka.v2+json"}).json()
# print(res)

# # Subscribe
# res = requests.post(
#     url=f"{base_uri}/consumers/test_group/instances/test_consumer2/subscription",
#     data=json.dumps({"topics": ["test"]}),
#     headers={"Content-Type": "application/vnd.kafka.v2+json"})

# # Consume
# res = requests.get(
#     url=f"{base_uri}/consumers/test_group/instances/test_consumer2/records",
#     params={"timeout":1000,"max_bytes":100000,"partition":0,"offset":1,},
#     headers={"Accept": "application/vnd.kafka.json.v2+json"}).json()
# print(res)

# # Commit
# res = requests.post(
#     url=f"{base_uri}/consumers/test_group/instances/test_consumer/offsets",
#     data=json.dumps(
#         dict(partitions=[
#             dict(topic="test_topic", partition=p, offset=0) for p in [0, 1, 2]
#         ])),
#     headers={"Content-Type": "application/vnd.kafka.v2+json"})

# delete consumer
# res = requests.delete(
#     url=f"{base_uri}/consumers/test_group/instances/test_consumer",
#     headers={"Content-Type": "application/vnd.kafka.v2+json"})

# print(res.json())