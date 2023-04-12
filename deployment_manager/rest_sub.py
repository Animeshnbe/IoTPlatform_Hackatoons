import requests
import json

base_uri = "http://192.168.137.51:18082"
def pretty(text):
  print(json.dumps(text, indent=2))
  
res = requests.get(f"{base_uri}/topics").json()
pretty(res)

# Register consumer
res = requests.post(
    url=f"{base_uri}/consumers/test_group",
    data=json.dumps({
        "name": "test_consumer2",
        "format": "json",
        "auto.offset.reset": "earliest",
        "auto.commit.enable": "false",
        "fetch.min.bytes": "1",
        "consumer.request.timeout.ms": "100"
    }),
    headers={"Content-Type": "application/vnd.kafka.v2+json"}).json()
print(res)

# Subscribe
res = requests.post(
    url=f"{base_uri}/consumers/test_group/instances/test_consumer2/subscription",
    data=json.dumps({"topics": ["neuter"]}),
    headers={"Content-Type": "application/vnd.kafka.v2+json"})

# Consume
while True:
  res = requests.get(
      url=f"{base_uri}/consumers/test_group/instances/test_consumer2/records",
      params={"timeout":1000,"max_bytes":1000,"partition":0,"offset":1,},
      headers={"Accept": "application/vnd.kafka.json.v2+json"}).json()
  if res:
    print(res)

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