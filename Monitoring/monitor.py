from kafka import KafkaConsumer
import json
import time
from mongo_utility import MongoUtility
from bson import json_util


kafkaPort1 = "9092"
kafkaPort = "9092"

kafkaAddress = "192.168.43.219:{}".format(kafkaPort)  # ProducerIP : ProducerPort

kafkaAddress1 = "192.168.43.181:{}".format(kafkaPort1)  # ProducerIP : ProducerPort

collection_name = "nodeCollection"
database_name = "iot"

mongo_port = 27017
mongo_host = "localhost"


def fetch_nodes_status():
    try:
        kafka_consumer = KafkaConsumer(bootstrap_servers=[kafkaAddress, kafkaAddress1], auto_offset_reset='latest',
                                       enable_auto_commit=True, value_deserializer=lambda x: x.decode('utf-8'))
        kafka_consumer.subscribe(topics=["nodestats3"])
        print(kafka_consumer.subscription())
        mongo_utility = MongoUtility(_mongo_port=mongo_port, _mongo_host=mongo_host)
        for stats in kafka_consumer:
            node_details = dict()
            data = stats.value
            stats = json.loads(data)
            node_details['nodeID'] = stats["nodeID"]
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
    data = {}
    server_load = []

    for x in record:
        if time.time() - x['timestamp'] < 3:
            x["ip"] = x['nodeID'].split(':')[0]
            x["port"] = int(x['nodeID'].split(':')[1])
            x.pop('nodeID')
            x.pop('timestamp')
            server_load.append(x)

    data["n_servers"] = len(server_load)
    data["server_load"] = server_load
    res = json.dumps(data, default=json_util.default)
    return res
