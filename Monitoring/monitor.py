from kafka import KafkaConsumer
import json
import time
from mongo_utility import MongoUtility
from bson import json_util
import threading
from dotenv import load_dotenv
import os
import datetime
from communication_api import monitor
from loggingUtility import logger_func
from sshUtility import SSHUtil

logger = logger_func()

load_dotenv()  # take environment variables from .env.

threshold = 10

# kafkaPort1 = "9092"
# kafkaPort = "9092"
kafkaPort1 = os.getenv("kafkaPort")
kafkaPort = os.getenv("kafkaPort")

kafkaAddress = os.getenv("kafkaAddress") + ":{}".format(kafkaPort)  # ProducerIP : ProducerPort

kafkaAddress1 = os.getenv("kafkaAddress") + ":{}".format(kafkaPort1)  # ProducerIP : ProducerPort

collection_name = os.getenv("collection_name")
database_name = os.getenv("database_name")

mongo_port = int(os.getenv("mongo_port"))
mongo_host = os.getenv("mongo_host")

module_dict = dict()
module_status = dict()

mongo_utility = MongoUtility(_mongo_port=mongo_port, _mongo_host=mongo_host)


def fetch_status():
    for message in monitor():
        print("Message : ", message)
        logger.info("Message : "+str(message))
        module_dict[message['moduleName']] = message['currentTime']


# def node_deployer():


def fetch_module_status():
    t = threading.Thread(target=fetch_status)
    t.daemon = True
    t.start()

    # for message in monitor():
    #     module_dict[message['moduleName']] = message['currentTime']

    print("Inside fetch_module_status")
    down = []
    # current_time = datetime.datetime.utcnow()
    print(module_dict)

    while True:
        if len(module_dict) > 0:
            for module in module_dict.keys():
                current_time = datetime.datetime.utcnow()
                date_time_obj = datetime.datetime.strptime(module_dict[module], '%Y-%m-%d %H:%M:%S.%f')
                print("current_time : ", current_time)
                print("date_time_obj : ", date_time_obj)
                diff = (current_time - date_time_obj).total_seconds()
                print("Difference:", diff)
                if diff > threshold:
                    if module in down:
                        continue
                    else:
                        print(module + " down")
                        module_status[module] = 'down'
                        obj = SSHUtil()
                        # a, b = obj.execute_command(["python3 hello.py"], "10.2.136.254", "aman_2110")
                        down.append(module)
                else:
                    if module in down:
                        down.remove(module)

                    print(module + " up")
                    module_status[module] = 'up'
                # if mongo_utility.check_document(database_name, json_data, collection_name):
                json_data = {'status': module_status[module]}
                print("JSON TYPE : ", type(json_data))
                # json_data = json.dumps(json_data)
                # json_data = json.loads(json_data)

                mongo_utility.update_one_field(module, module_status[module], database_name, collection_name)

        time.sleep(5)


def node_monitoring():
    try:
        print("Hello")
        send_logs_thread = threading.Thread(target=fetch_module_status)
        send_logs_thread.daemon = True
        send_logs_thread.start()

    except Exception as e:
        print(e)

# def fetch_nodes_status():
#     try:
#         kafka_consumer = KafkaConsumer(bootstrap_servers=[kafkaAddress, kafkaAddress1], auto_offset_reset='latest',
#                                        enable_auto_commit=True, value_deserializer=lambda x: x.decode('utf-8'))
#         kafka_consumer.subscribe(topics=["nodestats3"])
#         print(kafka_consumer.subscription())
#         mongo_utility = MongoUtility(_mongo_port=mongo_port, _mongo_host=mongo_host)
#         for stats in kafka_consumer:
#             node_details = dict()
#             data = stats.value
#             stats = json.loads(data)
#             node_details['nodeID'] = stats["nodeID"]
#             node_details["username"] = stats["username"]
#             node_details["password"] = stats["password"]
#             node_details["free_cpu"] = float(stats["free_cpu"])
#             node_details["free_memory"] = float(stats["free_memory"])
#             node_details["number_of_events_per_sec"] = int(stats["number_of_events_per_sec"])
#             node_details["free_RAM"] = float(stats["free_RAM"])
#             node_details["temperature"] = float(stats["temperature"])
#             node_details["n_cores"] = int(stats["n_cores"])
#             node_details["timestamp"] = time.time()
#             json_data = {'nodeID': node_details['nodeID']}
#             if mongo_utility.check_document(database_name, json_data, collection_name):
#                 mongo_utility.update_one(json_data, node_details, database_name, collection_name)
#                 print(node_details['nodeID'], '- updated record into registry.')
#             else:
#                 rec = mongo_utility.insert_one(node_details, database_name, collection_name)
#                 print(node_details['nodeID'], '- new record inserted into registry with id :', rec)
#
#     except Exception as e:
#         print(e)
#
#
# def send_node_modules():
#     mongo_utility = MongoUtility(_mongo_port=mongo_port, _mongo_host=mongo_host)
#     record = mongo_utility.find_all(database_name, collection_name)
#     data = {}
#     server_load = []
#
#     for x in record:
#         if time.time() - x['timestamp'] < 3:
#             x["ip"] = x['nodeID'].split(':')[0]
#             x["port"] = int(x['nodeID'].split(':')[1])
#             x.pop('nodeID')
#             x.pop('timestamp')
#             server_load.append(x)
#
#     data["n_servers"] = len(server_load)
#     data["server_load"] = server_load
#     res = json.dumps(data, default=json_util.default)
#     return res
