from kafka import KafkaConsumer
import json
import time
from mongo_utility import MongoUtility

kafkaPort = "9092"
kafkaAddress = "192.168.43.219:{}".format(kafkaPort)  # ProducerIP : ProducerPort

collection_name = "nodeCollection"
database_name = "iot"

mongo_port = 27017
mongo_host = "localhost"


def fetch_nodes_status():
    try:
        kafka_consumer = KafkaConsumer(bootstrap_servers=[kafkaAddress], auto_offset_reset='latest',
                                       enable_auto_commit=True, value_deserializer=lambda x: x.decode('utf-8'))
        kafka_consumer.subscribe(topics=["nodestats"])
        print(kafka_consumer.subscription())
        mongo_utility = MongoUtility(_mongo_port=mongo_port, _mongo_host=mongo_host)
        for stats in kafka_consumer:
            print("Stats : ", stats.value)
            # mongo_utility = MongoUtility(_mongo_port=mongo_port, _mongo_host=mongo_host)
            node_details = dict()
            # print(type(stats))
            # print(stats.value)
            data = stats.value
            # print(type(data))
            stats = json.loads(data)
            # print("statsData : ", stats)
            # stats = json.loads(stats)
            # print("statsDataLatest : ", stats)
            # print("Stats : ", type(stats))
            node_details['nodeID'] = stats["nodeID"]
            print("nodeID : ", node_details['nodeID'])
            node_details["username"] = stats["username"]
            node_details["password"] = stats["password"]
            node_details["free_cpu"] = float(stats["free_cpu"])
            node_details["free_memory"] = float(stats["free_memory"])
            node_details["number_of_events_per_sec"] = int(stats["number_of_events_per_sec"])
            node_details["free_RAM"] = float(stats["free_RAM"])
            node_details["temperature"] = float(stats["temperature"])
            node_details["n_cores"] = int(stats["n_cores"])
            node_details["timestamp"] = time.time()
            json_data = {'nodeID': node_details['nodeID']}
            if mongo_utility.check_document(database_name, json_data, collection_name):
                mongo_utility.update_one(json_data, node_details, database_name, collection_name)
                print(node_details['nodeID'], '- updated record into registry.')
            else:
                rec = mongo_utility.insert_one(node_details, database_name, collection_name)
                print(node_details['nodeID'], '- new record inserted into registry with id :', rec)

    except Exception as e:
        print(e)


def send_node_modules():
    mongo_utility = MongoUtility(_mongo_port=mongo_port, _mongo_host=mongo_host)
    record = mongo_utility.find_all(database_name, collection_name)
    print(record)
    dd = [{'machineID': '192.0.0.0.1:1920', 'username': 'priyanshu94', 'password': '1234', 'free_cpu': '123',
           'free_mem': '123', 'timestamp': 1678611000.130538},
          {'machineID': '192.0.0.0.1:8080', 'username': 'aman', 'password': '123', 'free_cpu': '456', 'free_mem': '456',
           'timestamp': 1678608095.275329}]
    dd1 = []
    print(time.time())
    for x in dd:
        if time.time() - x['timestamp'] <= 15:
            dd1.append(x)
            continue
    print(dd1)

    data = {}
    server_load = []

    for x in dd1:
        if time.time() - x['timestamp'] < 3:
            x["ip"] = x['machineID'].split(':')[0]
            x["port"] = int(x['machineID'].split(':')[1])
            x.pop('machineID')
            x.pop('timestamp')
            # x.pop('_id')
            server_load.append(x)

    data["n_servers"] = len(server_load)
    data["server_load"] = server_load
    res = json.dumps(data)
    print(res)
